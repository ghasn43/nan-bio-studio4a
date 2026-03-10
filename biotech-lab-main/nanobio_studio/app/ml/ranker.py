"""
Candidate Formulation Ranking Engine

Scores and ranks candidate LNP formulations based on multi-objective criteria.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from .schemas import RankingRequest, RankingResult, CandidateScoreBreakdown
from .predict import ModelPredictor


logger = logging.getLogger(__name__)


class CandidateRanker:
    """
    Ranks candidate formulations using weighted multi-objective scoring.
    
    Scoring criteria:
    - Uptake: Maximized (weighted)
    - Toxicity: Minimized (penalty)
    - Particle size: Preference range (bonus/penalty)
    - PDI: Minimized (penalty)
    - Target match: Bonus for design target
    - Payload match: Bonus for intended payload
    
    Final score is composite, interpretable breakdown per candidate.
    """

    # Default scoring weights (can be customized per request)
    DEFAULT_WEIGHTS = {
        'uptake': 0.35,           # Uptake importance
        'toxicity': 0.25,         # Minimize toxicity
        'size_preference': 0.20,  # Prefer size range
        'pdi': 0.10,              # Minimize PDI
        'target_match': 0.05,     # Target alignment bonus
        'payload_match': 0.05,    # Payload alignment bonus
    }

    def __init__(
        self,
        uptake_predictor: Optional[ModelPredictor] = None,
        toxicity_predictor: Optional[ModelPredictor] = None,
        size_predictor: Optional[ModelPredictor] = None,
        pdi_predictor: Optional[ModelPredictor] = None,
    ):
        """
        Initialize ranker with trained predictors.
        
        Args:
            uptake_predictor: Trained model for predicting uptake
            toxicity_predictor: Trained model for predicting toxicity
            size_predictor: Trained model for predicting particle size
            pdi_predictor: Trained model for predicting PDI
        """
        self.uptake_predictor = uptake_predictor
        self.toxicity_predictor = toxicity_predictor
        self.size_predictor = size_predictor
        self.pdi_predictor = pdi_predictor

    def rank_formulations(
        self,
        candidates: List[Dict],
        request: RankingRequest,
    ) -> List[RankingResult]:
        """
        Rank candidate formulations.
        
        Args:
            candidates: List of candidate formulation dicts
            request: RankingRequest with criteria and weights
            
        Returns:
            Sorted list of RankingResult
        """
        
        results = []
        
        # Use custom weights or defaults
        weights = request.weights or self.DEFAULT_WEIGHTS
        
        for i, candidate in enumerate(candidates):
            score_breakdown = self._score_candidate(
                candidate=candidate,
                request=request,
                weights=weights,
            )
            
            result = RankingResult(
                rank=i + 1,  # Will be updated after sorting
                score_breakdown=score_breakdown,
                recommended=False,
            )
            results.append(result)
        
        # Sort by composite score (descending)
        results.sort(key=lambda x: x.score_breakdown.composite_score, reverse=True)
        
        # Update ranks
        for rank, result in enumerate(results, 1):
            result.rank = rank
            result.recommended = (rank <= 3)  # Top 3 as recommendations
        
        logger.info(f"Ranked {len(results)} formulations")
        return results

    def _score_candidate(
        self,
        candidate: Dict,
        request: RankingRequest,
        weights: Dict[str, float],
    ) -> CandidateScoreBreakdown:
        """
        Score a single candidate formulation.
        
        Args:
            candidate: Candidate dict with formulation data
            request: Ranking request with criteria
            weights: Scoring weights
            
        Returns:
            CandidateScoreBreakdown with detailed scores
        """
        
        formulation_id = candidate.get('formulation_id', f"candidate_{id(candidate)}")
        
        # Initialize scores
        uptake_score = 0.0
        toxicity_penalty = 0.0
        size_preference_score = 0.0
        pdi_penalty = 0.0
        target_match_bonus = 0.0
        payload_match_bonus = 0.0
        
        predicted_uptake = None
        predicted_toxicity = None
        predicted_particle_size = None
        predicted_pdi = None
        
        # Predict uptake if model available
        if self.uptake_predictor and request.maximize_uptake:
            try:
                uptake_df = pd.DataFrame([candidate])
                pred = self.uptake_predictor.predict_from_records(uptake_df)
                predicted_uptake = float(pred['prediction'].iloc[0])
                uptake_score = np.clip(predicted_uptake, 0, 100)
            except Exception as e:
                logger.warning(f"Error predicting uptake: {e}")
        
        # Predict toxicity if model available
        if self.toxicity_predictor and request.minimize_toxicity:
            try:
                toxicity_df = pd.DataFrame([candidate])
                pred = self.toxicity_predictor.predict_from_records(toxicity_df)
                predicted_toxicity = float(pred['prediction'].iloc[0])
                # Toxicity penalty: higher toxicity = higher penalty
                toxicity_penalty = np.clip(predicted_toxicity * 10, 0, 100)
            except Exception as e:
                logger.warning(f"Error predicting toxicity: {e}")
        
        # Predict particle size if model available
        if self.size_predictor:
            try:
                size_df = pd.DataFrame([candidate])
                pred = self.size_predictor.predict_from_records(size_df)
                predicted_particle_size = float(pred['prediction'].iloc[0])
                
                # Size preference score: bonus in preferred range, penalty outside
                min_size, max_size = request.preferred_size_range_nm
                if min_size <= predicted_particle_size <= max_size:
                    size_preference_score = 100.0
                else:
                    # Linear penalty for distance from range
                    if predicted_particle_size < min_size:
                        distance = min_size - predicted_particle_size
                    else:
                        distance = predicted_particle_size - max_size
                    size_preference_score = max(0, 100 - distance * 2)
            
            except Exception as e:
                logger.warning(f"Error predicting size: {e}")
        
        # Predict PDI if model available
        if self.pdi_predictor:
            try:
                pdi_df = pd.DataFrame([candidate])
                pred = self.pdi_predictor.predict_from_records(pdi_df)
                predicted_pdi = float(pred['prediction'].iloc[0])
                
                # PDI penalty: lower PDI is better
                if predicted_pdi <= request.max_pdi:
                    pdi_penalty = 0.0
                else:
                    pdi_penalty = min(100, (predicted_pdi - request.max_pdi) * 100)
            
            except Exception as e:
                logger.warning(f"Error predicting PDI: {e}")
        
        # Target match bonus
        if 'intended_target' in candidate:
            candidate_target = str(candidate.get('intended_target', '')).lower()
            request_target = request.target.lower()
            if candidate_target == request_target:
                target_match_bonus = 100.0
        
        # Payload match bonus
        if 'payload_type' in candidate:
            candidate_payload = str(candidate.get('payload_type', '')).lower()
            request_payload = request.payload_type.lower()
            if candidate_payload == request_payload:
                payload_match_bonus = 100.0
        
        # Compute composite score
        composite_score = (
            (uptake_score * weights['uptake']) +
            ((100 - toxicity_penalty) * weights['toxicity']) +
            (size_preference_score * weights['size_preference']) +
            ((100 - pdi_penalty) * weights['pdi']) +
            (target_match_bonus * weights['target_match']) +
            (payload_match_bonus * weights['payload_match'])
        )
        
        return CandidateScoreBreakdown(
            formulation_id=formulation_id,
            uptake_score=uptake_score,
            toxicity_penalty=toxicity_penalty,
            size_preference_score=size_preference_score,
            pdi_penalty=pdi_penalty,
            target_match_bonus=target_match_bonus,
            payload_match_bonus=payload_match_bonus,
            predicted_particle_size_nm=predicted_particle_size,
            predicted_pdi=predicted_pdi,
            predicted_toxicity=predicted_toxicity,
            predicted_uptake=predicted_uptake,
            composite_score=np.clip(composite_score, 0, 100),
        )
