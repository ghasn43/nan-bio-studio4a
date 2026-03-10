"""
Feature Builder for LNP Experiment Data

Transforms raw LNP experiment and formulation records into ML-ready numerical
and categorical features, handling composition, process conditions, and assay results.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class FeatureConfig:
    """Configuration for feature engineering"""
    include_composition: bool = True
    include_ratios: bool = True
    include_process: bool = True
    include_characterization: bool = True
    include_biological: bool = True
    include_metadata: bool = True
    handle_missing_numeric: str = "median"  # "drop", "median", "mean"
    handle_missing_categorical: str = "unknown"


class FeatureBuilder:
    """
    Builds ML-ready features from LNP experiment and formulation records.
    
    Feature groups:
    - Composition (lipid types, payload, ligand)
    - Ratios (molar ratios between components)
    - Process (preparation method, flow rates, conditions)
    - Characterization (particle size, PDI, zeta potential, etc.)
    - Biological (model type, model name, species, route, etc.)
    - Metadata (source, institution, QC status)
    """

    def __init__(self, config: Optional[FeatureConfig] = None):
        self.config = config or FeatureConfig()
        self.feature_columns = []
        self.categorical_features = []
        self.numeric_features = []

    def build_features(
        self,
        records: pd.DataFrame,
        target_variable: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Transform raw records into feature dataframe.
        
        Args:
            records: Flattened dataframe with experiment/formulation data
            target_variable: If provided, exclude this from features
            
        Returns:
            Feature dataframe with engineered features
        """
        features = pd.DataFrame()
        
        if self.config.include_composition:
            features = pd.concat([features, self._build_composition_features(records)], axis=1)
        
        if self.config.include_ratios:
            features = pd.concat([features, self._build_ratio_features(records)], axis=1)
        
        if self.config.include_process:
            features = pd.concat([features, self._build_process_features(records)], axis=1)
        
        if self.config.include_characterization:
            features = pd.concat([features, self._build_characterization_features(records)], axis=1)
        
        if self.config.include_biological:
            features = pd.concat([features, self._build_biological_features(records)], axis=1)
        
        if self.config.include_metadata:
            features = pd.concat([features, self._build_metadata_features(records)], axis=1)
        
        # Remove target variable if specified
        if target_variable and target_variable in features.columns:
            features = features.drop(columns=[target_variable])
        
        # Remove non-existent columns and deduplicate
        self.feature_columns = list(set(features.columns))
        
        return features

    def _build_composition_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer composition features"""
        composition = pd.DataFrame()
        
        # Lipid identities (categorical)
        for col in ['ionizable_lipid', 'helper_lipid', 'sterol', 'peg_lipid']:
            if col in records.columns:
                composition[f'{col}_name'] = records[col].astype(str).str.lower().str.strip()
                self.categorical_features.append(f'{col}_name')
        
        # Payload type
        if 'payload_type' in records.columns:
            composition['payload_type'] = records['payload_type'].astype(str).str.lower().str.strip()
            self.categorical_features.append('payload_type')
        
        # Ligand
        if 'ligand' in records.columns:
            composition['ligand'] = records['ligand'].astype(str).str.lower().str.strip()
            self.categorical_features.append('ligand')
        
        # Intended target
        if 'intended_target' in records.columns:
            composition['intended_target'] = records['intended_target'].astype(str).str.lower().str.strip()
            self.categorical_features.append('intended_target')
        
        return composition

    def _build_ratio_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer ratio features"""
        ratios = pd.DataFrame()
        
        # Direct ratios (if available)
        for col in ['ionizable_ratio', 'helper_ratio', 'sterol_ratio', 'peg_ratio']:
            if col in records.columns:
                ratios[col] = pd.to_numeric(records[col], errors='coerce')
                self.numeric_features.append(col)
        
        # Derived ratios
        if 'sterol_ratio' in records.columns and 'ionizable_ratio' in records.columns:
            stereo_ion = pd.to_numeric(records['sterol_ratio'], errors='coerce')
            ion = pd.to_numeric(records['ionizable_ratio'], errors='coerce')
            ratios['sterol_to_ionizable_ratio'] = stereo_ion / ion
            self.numeric_features.append('sterol_to_ionizable_ratio')
        
        if 'peg_ratio' in records.columns:
            peg = pd.to_numeric(records['peg_ratio'], errors='coerce')
            total = peg + pd.to_numeric(records.get('ionizable_ratio', 0), errors='coerce')
            ratios['peg_to_total_ratio'] = peg / total
            self.numeric_features.append('peg_to_total_ratio')
        
        if 'helper_ratio' in records.columns and 'ionizable_ratio' in records.columns:
            helper = pd.to_numeric(records['helper_ratio'], errors='coerce')
            ion = pd.to_numeric(records['ionizable_ratio'], errors='coerce')
            ratios['helper_to_ionizable_ratio'] = helper / ion
            self.numeric_features.append('helper_to_ionizable_ratio')
        
        return ratios

    def _build_process_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer process condition features"""
        process = pd.DataFrame()
        
        # Preparation method
        if 'preparation_method' in records.columns:
            process['preparation_method'] = records['preparation_method'].astype(str).str.lower().str.strip()
            self.categorical_features.append('preparation_method')
        
        # Flow rate parsing
        if 'flow_rate_ratio' in records.columns:
            process['flow_rate_ratio_numeric'] = pd.to_numeric(
                records['flow_rate_ratio'].astype(str).str.extract(r'(\d+\.?\d*)')[0],
                errors='coerce'
            )
            self.numeric_features.append('flow_rate_ratio_numeric')
        
        # Total flow rate
        if 'total_flow_rate_ml_min' in records.columns:
            process['total_flow_rate_ml_min'] = pd.to_numeric(
                records['total_flow_rate_ml_min'],
                errors='coerce'
            )
            self.numeric_features.append('total_flow_rate_ml_min')
        
        # Buffer type
        if 'buffer_type' in records.columns:
            process['buffer_type'] = records['buffer_type'].astype(str).str.lower().str.strip()
            self.categorical_features.append('buffer_type')
        
        # Buffer pH
        if 'buffer_ph' in records.columns:
            process['buffer_ph'] = pd.to_numeric(records['buffer_ph'], errors='coerce')
            self.numeric_features.append('buffer_ph')
        
        # Temperature
        if 'temperature_c' in records.columns:
            process['temperature_c'] = pd.to_numeric(records['temperature_c'], errors='coerce')
            self.numeric_features.append('temperature_c')
        
        # Mixer/chip type
        if 'mixing_chip_type' in records.columns:
            process['mixing_chip_type'] = records['mixing_chip_type'].astype(str).str.lower().str.strip()
            self.categorical_features.append('mixing_chip_type')
        
        return process

    def _build_characterization_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract particle characterization features"""
        characterization = pd.DataFrame()
        
        # Numeric characterization values
        for col in ['particle_size_nm', 'pdi', 'zeta_potential_mv',
                   'encapsulation_efficiency_pct', 'stability_hours']:
            if col in records.columns:
                characterization[col] = pd.to_numeric(records[col], errors='coerce')
                self.numeric_features.append(col)
        
        return characterization

    def _build_biological_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract biological model and context features"""
        biological = pd.DataFrame()
        
        # Model type and name
        if 'model_type' in records.columns:
            biological['model_type'] = records['model_type'].astype(str).str.lower().str.strip()
            self.categorical_features.append('model_type')
        
        if 'model_name' in records.columns:
            biological['model_name'] = records['model_name'].astype(str).str.lower().str.strip()
            self.categorical_features.append('model_name')
        
        # Species
        if 'species' in records.columns:
            biological['species'] = records['species'].astype(str).str.lower().str.strip()
            self.categorical_features.append('species')
        
        # Disease context
        if 'disease_context' in records.columns:
            biological['disease_context'] = records['disease_context'].astype(str).str.lower().str.strip()
            self.categorical_features.append('disease_context')
        
        # Route of administration
        if 'route_of_administration' in records.columns:
            biological['route_of_administration'] = records['route_of_administration'].astype(str).str.lower().str.strip()
            self.categorical_features.append('route_of_administration')
        
        # Numeric biological features
        if 'timepoint_hours' in records.columns:
            biological['timepoint_hours'] = pd.to_numeric(records['timepoint_hours'], errors='coerce')
            self.numeric_features.append('timepoint_hours')
        
        if 'dose' in records.columns:
            biological['dose'] = pd.to_numeric(records['dose'], errors='coerce')
            self.numeric_features.append('dose')
        
        return biological

    def _build_metadata_features(self, records: pd.DataFrame) -> pd.DataFrame:
        """Extract metadata features"""
        metadata = pd.DataFrame()
        
        # Source type
        if 'source_type' in records.columns:
            metadata['source_type'] = records['source_type'].astype(str).str.lower().str.strip()
            self.categorical_features.append('source_type')
        
        # Institution
        if 'institution' in records.columns:
            metadata['institution'] = records['institution'].astype(str).str.lower().str.strip()
            self.categorical_features.append('institution')
        
        # QC status
        if 'qc_status' in records.columns:
            metadata['qc_status'] = records['qc_status'].astype(str).str.lower().str.strip()
            self.categorical_features.append('qc_status')
        
        return metadata

    def get_numeric_features(self) -> List[str]:
        """Get list of numeric feature names"""
        return list(set(self.numeric_features))

    def get_categorical_features(self) -> List[str]:
        """Get list of categorical feature names"""
        return list(set(self.categorical_features))

    def get_all_feature_names(self) -> List[str]:
        """Get all engineered feature names"""
        return list(set(self.feature_columns))
