"""
Regulatory Assessment Engine for NanoBio Studio
Carefully positions regulatory strategy with evidence-appropriate language
"""

from typing import List, Tuple, Dict
from models.scientific_assessment import (
    RegulatoryAssessment,
    TrialDesignInputs,
    MechanisticPredictionResult,
    SafetyRiskProfile,
    DiseaseBiologyFit,
)
from config.disease_profiles import DiseaseProfile
from config.scoring_config import get_confidence_label


class RegulatoryEngine:
    """
    Positions regulatory strategy with disciplined, evidence-appropriate language.
    Core principle: Claims match evidence level; downgrade assertions when uncertain.
    """

    # Regulatory pathway stages (progression)
    REGULATORY_STAGES = [
        "concept",              # Pre-IND: literature based
        "in_silico_design",     # Initial computational design
        "formulation_screening",  # Lab-scale optimization
        "preclinical_candidate", # GLP toxicology ready
        "regulatory_enabling",   # IND-enabling studies complete
        "clinical_phase_i",      # Human studies initiated
        "clinical_phase_ii",     # Efficacy signals emerging
        "clinical_phase_iii",    # Pivotal efficacy trials
    ]

    # Language qualification levels (for claims calibration)
    LANGUAGE_LEVELS = {
        "validated": {
            "verb": "demonstrates",
            "basis": "has been experimentally validated in this formulation",
            "confidence_min": 0.85,
        },
        "predicted": {
            "verb": "is predicted to",
            "basis": "based on mechanistic principles and similar literature systems",
            "confidence_min": 0.70,
        },
        "anticipated": {
            "verb": "is anticipated to",
            "basis": "based on formulation design parameters",
            "confidence_min": 0.60,
        },
        "proposed": {
            "verb": "is proposed to",
            "basis": "would be addressed by the formulation strategy",
            "confidence_min": 0.50,
        },
        "requires_investigation": {
            "verb": "requires investigation to",
            "basis": "formulation design has potential to address",
            "confidence_min": 0.0,
        },
    }

    @staticmethod
    def assess_regulatory_position(
        design_inputs: TrialDesignInputs,
        disease_profile: DiseaseProfile,
        mechanistic_results: MechanisticPredictionResult,
        safety_results: SafetyRiskProfile,
        disease_fit: DiseaseBiologyFit,
    ) -> RegulatoryAssessment:
        """
        Comprehensive regulatory positioning assessment.
        
        Returns:
            RegulatoryAssessment: Regulatory strategy with calibrated language
        """
        
        # Determine current regulatory stage
        current_stage = RegulatoryEngine._determine_regulatory_stage(design_inputs)
        
        # Generate pathway (what's next)
        pathway = RegulatoryEngine._generate_regulatory_pathway(current_stage)
        
        # Create regulatory assertions (carefully worded)
        assertions = RegulatoryEngine._generate_regulatory_assertions(
            design_inputs,
            disease_profile,
            mechanistic_results,
            safety_results,
            disease_fit,
        )
        
        # Identify regulatory risks
        risks = RegulatoryEngine._identify_regulatory_risks(
            design_inputs,
            disease_profile,
            safety_results,
        )
        
        # Document key regulatory gaps
        gaps = RegulatoryEngine._identify_evidence_gaps(
            mechanistic_results,
            safety_results,
            disease_fit,
        )
        
        # Generate regulatory strategy narrative
        narrative = RegulatoryEngine._generate_regulatory_narrative(
            current_stage,
            pathway,
            assertions,
            risks,
            gaps,
            disease_profile,
        )
        
        confidence_score = RegulatoryEngine._calculate_regulatory_confidence()
        
        assumptions = [
            "Assumes FDA guidance on nanomedicine products (2017) is applicable",
            "Regulatory positioning based on CDER/CBER precedent for similar therapeutics",
            "Pathways may differ by disease indication and drug substance",
            "International regulatory requirements (EMA, PMDA, etc.) not addressed",
            "Assumes current applicant has manufacturing capability for proposed stage",
        ]
        
        # Identify unmet needs (evidence gaps)
        unmet_needs = RegulatoryEngine._identify_unmet_needs(design_inputs, disease_profile)
        
        return RegulatoryAssessment(
            current_regulatory_stage=current_stage,
            proposed_regulatory_pathway=pathway,
            regulatory_category=RegulatoryEngine._determine_regulatory_category(design_inputs),
            primary_regulatory_strategy=RegulatoryEngine._determine_primary_strategy(design_inputs),
            key_regulatory_assertions=assertions,
            critical_regulatory_risks=risks,
            evidence_gaps=gaps,
            unmet_regulatory_needs=unmet_needs,
            recommended_next_studies=RegulatoryEngine._recommend_next_studies(current_stage),
            quality_overall_summary=RegulatoryEngine._generate_quality_summary(design_inputs),
            nonclinical_summary=RegulatoryEngine._generate_nonclinical_approach(safety_results),
            clinical_strategy=RegulatoryEngine._generate_clinical_strategy(disease_profile),
            detailed_regulatory_narrative=narrative,
            assumptions=assumptions,
            confidence_level=get_confidence_label(confidence_score),
            numeric_confidence=confidence_score,
        )

    @staticmethod
    def _determine_regulatory_stage(design_inputs: TrialDesignInputs) -> str:
        """Determine current development stage"""
        # For NanoBio Studio context: all designs are at in_silico/formulation_screening
        # This would be determined by project context in real system
        return "formulation_screening"

    @staticmethod
    def _determine_regulatory_category(design_inputs: TrialDesignInputs) -> str:
        """Determine regulatory classification"""
        # For targeted nanoparticle therapeutics
        return "Combination Product: Drug-Nanoparticle System (Class III, likely)" if design_inputs.targeting_ligand else "Drug-Delivery System (Class III)"

    @staticmethod
    def _determine_primary_strategy(design_inputs: TrialDesignInputs) -> str:
        """Determine primary regulatory positioning strategy"""
        if design_inputs.targeting_ligand and design_inputs.targeting_ligand.lower() != "none":
            return "Molecular Targeted Therapy: Active targeting ligand + nanoparticle drug delivery"
        else:
            return "Passive Targeted Drug Delivery: EPR-mediated tumor accumulation"

    @staticmethod
    def _generate_regulatory_assertions(
        design_inputs: TrialDesignInputs,
        disease_profile: DiseaseProfile,
        mechanistic_results: MechanisticPredictionResult,
        safety_results: SafetyRiskProfile,
        disease_fit: DiseaseBiologyFit,
    ) -> List[Tuple[str, str, float]]:
        """
        Generate key regulatory assertions with calibrated language.
        Returns: [(assertion, language_level, confidence)]
        """
        assertions = []
        
        # Delivery efficacy assertion
        delivery_conf = mechanistic_results.delivery_efficacy.numeric_confidence
        if delivery_conf > 0.80:
            lang_level = "predicted"
        elif delivery_conf > 0.70:
            lang_level = "anticipated"
        else:
            lang_level = "proposed"
        
        assertion = f"The formulation {RegulatoryEngine.LANGUAGE_LEVELS[lang_level]['verb']} achieve "
        assertion += f"improved tumor accumulation vs free drug via {delivery_conf*100:.0f}% confidence mechanism"
        assertions.append((assertion, lang_level, delivery_conf))
        
        # Safety assertion
        safety_score = 100.0 - safety_results.overall_safety_score
        if safety_score < 40:
            lang_level = "predicted"
            assertion = f"The nanoparticle is {RegulatoryEngine.LANGUAGE_LEVELS[lang_level]['verb']} present "
            assertion += "acceptable safety profile in preclinical studies"
        else:
            lang_level = "anticipated"
            assertion = f"Safety profile is {RegulatoryEngine.LANGUAGE_LEVELS[lang_level]['verb']} be "
            assertion += "acceptable pending in vivo toxicology validation"
        assertions.append((assertion, lang_level, 1.0 - (safety_score / 100.0)))
        
        # Disease fit assertion
        disease_conf = disease_fit.numeric_confidence
        if disease_fit.overall_fit_score > 70:
            lang_level = "predicted"
            assertion = f"Formulation design {RegulatoryEngine.LANGUAGE_LEVELS[lang_level]['verb']} "
            assertion += f"address key {disease_profile.name} biological barriers ({disease_fit.overall_fit_score:.0f}% fit score)"
        else:
            lang_level = "anticipated"
            assertion = f"Formulation is {RegulatoryEngine.LANGUAGE_LEVELS[lang_level]['verb']} "
            assertion += f"achieve meaningful disease-specific targeting"
        assertions.append((assertion, lang_level, disease_conf))
        
        # Manufacturing claim
        manufacturing_complexity = design_inputs.peg_surface_coating + design_inputs.targeting_ligand
        if manufacturing_complexity:
            assertion = "Manufacturing process requires development; capable of GMP-scale production"
            assertions.append((assertion, "proposed", 0.65))
        else:
            assertion = "Manufacturing is feasible using standard pharmaceutical techniques"
            assertions.append((assertion, "predicted", 0.85))
        
        return assertions

    @staticmethod
    def _generate_regulatory_pathway(current_stage: str) -> List[Tuple[str, List[str]]]:
        """
        Generate recommended regulatory pathway forward.
        Returns: [(stage, [required_studies])]
        """
        current_idx = RegulatoryEngine.REGULATORY_STAGES.index(current_stage)
        pathway = []
        
        # Define required studies per stage transition
        stage_requirements = {
            "formulation_screening": [
                "Optimize encapsulation efficiency and batch consistency",
                "Develop Quality Overall Summary (QOS): analytics and specifications",
                "Preliminary in vitro target cell studies",
            ],
            "preclinical_candidate": [
                "GLP in vivo toxicology (14-28 day IV repeat dose)",
                "Pharmacokinetics and biodistribution (PK/BD)",
                "Efficacy proof-of-concept in disease model",
                "Analytical method validation for GMP",
            ],
            "regulatory_enabling": [
                "Additional toxicology studies addressing preliminary findings",
                "Manufacturing process validation",
                "Stability data (12-month real-time minimum)",
                "IND-enabling package preparation",
            ],
        }
        
        # Next 3 stages
        for i in range(current_idx + 1, min(current_idx + 4, len(RegulatoryEngine.REGULATORY_STAGES))):
            stage = RegulatoryEngine.REGULATORY_STAGES[i]
            studies = stage_requirements.get(stage, ["Further development required"])
            pathway.append((stage, studies))
        
        return pathway

    @staticmethod
    def _identify_regulatory_risks(
        design_inputs: TrialDesignInputs,
        disease_profile: DiseaseProfile,
        safety_results: SafetyRiskProfile,
    ) -> List[str]:
        """Identify potential regulatory concerns that need addressing"""
        risks = []
        
        # Safety profile risks
        if safety_results.overall_safety_score < 50:
            risks.append(
                "SAFETY CONCERN: Low overall safety score; may require additional preclinical toxicology "
                + "studies or formulation modifications before IND submission"
            )
        
        # High-risk safety components
        high_risk_components = [
            (safety_results.systemic_toxicity, "Systemic Toxicity"),
            (safety_results.immunogenicity, "Immunogenicity"),
            (safety_results.off_target_effects, "Off-Target Effects"),
        ]
        
        for component, name in high_risk_components:
            if component and component.risk_band in ["High", "Critical"]:
                risks.append(
                    f"{name}: {component.risk_band} risk - regulatory review will require "
                    + "sophisticated risk mitigation strategies or alternative formulation"
                )
        
        # Targeting ligand risks
        if design_inputs.targeting_ligand and design_inputs.targeting_ligand.lower() != "none":
            risks.append(
                f"TARGETING LIGAND: {design_inputs.targeting_ligand} may elicit neutralizing antibodies; "
                + "immunogenicity assessment and repeated-dose tolerance studies mandatory"
            )
        
        # Encapsulation complexity risks
        if design_inputs.encapsulation_method.lower() == "active_loading":
            risks.append(
                "ACTIVE LOADING: pH-gradient maintenance in vivo unproven; may require separate "
                + "mechanism of action studies or biomarker-driven clinical design"
            )
        
        # Size extremes
        size = design_inputs.nanoparticle_size_nm
        if size < 50:
            risks.append(
                f"SIZE RISK: {size}nm particles < optimal window; renal accumulation and potential "
                + "glomerulonephritis requires careful renal monitoring studies"
            )
        elif size > 200:
            risks.append(
                f"SIZE RISK: {size}nm particles > optimal window; prolonged circulation and hepatic "
                + "accumulation may result in chronic toxicity signal"
            )
        
        return risks

    @staticmethod
    def _identify_evidence_gaps(
        mechanistic_results: MechanisticPredictionResult,
        safety_results: SafetyRiskProfile,
        disease_fit: DiseaseBiologyFit,
    ) -> List[str]:
        """Identify key evidence gaps that must be filled"""
        gaps = []
        
        # Mechanistic predictions not yet validated
        confidence_threshold = 0.75
        
        predictions = [
            (mechanistic_results.delivery_efficacy, "Delivery Efficacy"),
            (mechanistic_results.toxicity_safety, "Toxicity/Safety"),
            (mechanistic_results.targeting_efficacy, "Targeting Efficacy"),
            (mechanistic_results.payload_release, "Payload Release Kinetics"),
        ]
        
        for prediction, name in predictions:
            if prediction.numeric_confidence < confidence_threshold:
                gaps.append(
                    f"{name}: Prediction confidence {prediction.numeric_confidence*100:.0f}% < {confidence_threshold*100:.0f}% threshold; "
                    + "in vitro and in vivo validation studies required"
                )
        
        # Disease fit confidence
        if disease_fit.numeric_confidence < 0.75:
            gaps.append(
                f"{disease_fit.disease_name} Fit: Confidence {disease_fit.numeric_confidence*100:.0f}% < target; "
                + "disease-specific target validation and penetration studies needed"
            )
        
        # Manufacturing gaps
        gaps.append(
            "Manufacturing: Analytical method validation and specification ranges must be "
            + "established through DOE and preclinical manufacturing process characterization"
        )
        
        return gaps

    @staticmethod
    def _identify_unmet_needs(
        design_inputs: TrialDesignInputs,
        disease_profile: DiseaseProfile,
    ) -> List[str]:
        """Identify unmet regulatory/development needs"""
        needs = []
        
        needs.append(
            f"Target validation in {disease_profile.name}: Confirm target expression level and "
            + "location via IHC/flow cytometry on clinical patient samples"
        )
        
        needs.append(
            "Pharmacology/toxicology bridging: Connect in vitro mechanism of action to in vivo efficacy"
        )
        
        if design_inputs.encapsulation_method.lower() == "active_loading":
            needs.append(
                "pH-Gradient Stability: Characterize gradient maintenance under physiological conditions; "
                + "develop predictive in vitro release model"
            )
        
        if design_inputs.targeting_ligand and design_inputs.targeting_ligand.lower() != "none":
            needs.append(
                f"Ligand Immunogenicity: Perform immunogenicity assessment for {design_inputs.targeting_ligand}; "
                + "design for tolerance or immunomodulation"
            )
        
        needs.append(
            "Complex Product Chemistry: Characterize all components (core, shell, ligand) with "
            + "orthogonal analytical methods; establish batch-to-batch consistency"
        )
        
        return needs

    @staticmethod
    def _recommend_next_studies(current_stage: str) -> List[str]:
        """Recommend specific next studies based on current development stage"""
        base_studies = [
            "Finalize formulation and analytical method protocol",
            "Characterize batch consistency and specifications (3-5 batches)",
            "In vitro target cell uptake and mechanistic studies",
            "Stability testing (accelerated 3-month and real-time ongoing)",
        ]
        
        if current_stage == "formulation_screening":
            base_studies.extend([
                "Preliminary single-dose IV toxicology in rodents (GLP-quality)",
                "PK/biodistribution study in disease-relevant model",
                "Disease model efficacy proof-of-concept",
            ])
        
        return base_studies

    @staticmethod
    def _generate_quality_summary(design_inputs: TrialDesignInputs) -> str:
        """Generate Quality Overall Summary statement"""
        lines = [
            "QUALITY OVERALL SUMMARY (Regulatory Module 3)",
            "",
            "DRUG SUBSTANCE:",
            f"  • {design_inputs.encapsulation_method} encapsulated nanoparticles",
            f"  • Target size: {design_inputs.nanoparticle_size_nm} nm (±10nm)",
            f"  • Surface charge: {design_inputs.surface_charge_mv} mV",
            "",
            "DRUG PRODUCT:",
            f"  • PEG coating: {'Yes' if design_inputs.peg_surface_coating else 'No'}" +
                (f" ({design_inputs.peg_density_percent}%)" if design_inputs.peg_surface_coating else ""),
            f"  • Targeting ligand: {design_inputs.targeting_ligand or 'None'}",
            "",
            "CONTROLS:",
            "  • In-process: Size distribution, encapsulation efficiency, sterility",
            "  • In-vitro release kinetics: Simulated plasma conditions",
            "  • Stability: ICH conditions (real-time + accelerated)",
            "",
            "STATUS: Analytical methods require validation; specifications pending preclinical data",
        ]
        
        return "\n".join(lines)

    @staticmethod
    def _generate_nonclinical_approach(safety_results: SafetyRiskProfile) -> str:
        """Generate nonclinical/toxicology regulatory strategy"""
        lines = [
            "NONCLINICAL TOXICOLOGY STRATEGY (Regulatory Module 4)",
            "",
            f"OVERALL SAFETY ASSESSMENT: {100.0 - safety_results.overall_safety_score:.0f}/100 risk",
            "",
            "STUDY PLAN:",
            "  Phase 1: Single-dose IV toxicity (14-day observation)",
            "  Phase 2: Repeat-dose IV toxicity (14-28 days)",
            "  Phase 3: PK/biodistribution (tissue distribution, clearance kinetics)",
            "  Phase 4: Organ toxicity assessment (histopathology of liver, spleen, kidney)",
            "",
            "CRITICAL SAFETY PARAMETERS TO MONITOR:",
        ]
        
        if safety_results.systemic_toxicity and safety_results.systemic_toxicity.risk_band in ["High", "Critical"]:
            lines.append(f"  ⚠️ Systemic toxicity: {safety_results.systemic_toxicity.risk_band}")
        
        if safety_results.immunogenicity and safety_results.immunogenicity.risk_band in ["High", "Critical"]:
            lines.append(f"  ⚠️ Immunogenicity: {safety_results.immunogenicity.risk_band}")
        
        if safety_results.off_target_effects and safety_results.off_target_effects.risk_band in ["High", "Critical"]:
            lines.append(f"  ⚠️ Off-target effects: {safety_results.off_target_effects.risk_band}")
        
        lines.append("")
        lines.append("REGULATORY PATHWAY: IND-enabling studies required before human studies")
        
        return "\n".join(lines)

    @staticmethod
    def _generate_clinical_strategy(disease_profile: DiseaseProfile) -> str:
        """Generate clinical development strategy"""
        lines = [
            "CLINICAL STRATEGY",
            "",
            f"INDICATION: {disease_profile.name}",
            "",
            "PHASE I (Safety/Tolerability):",
            "  • Dose escalation (3+3 design)",
            "  • Small patient cohorts (n=15-30)",
            "  • PK/BD sampling + immunogenicity monitoring",
            "  • Focus: MTD establishment, DLT characterization",
            "",
            "PHASE II (Efficacy/Biomarkers):",
            "  • Dose expansion at MTD",
            "  • Larger population (n=50-100)",
            "  • Primary endpoint: ORR (objective response rate)",
            "  • Secondary: PFS, OS, biomarker response",
            "  • Focus: Disease-specific response assessment",
            "",
            "CONSIDERATION: Adaptive trial design may be warranted given targetingapproach",
        ]
        
        return "\n".join(lines)

    @staticmethod
    def _generate_regulatory_narrative(
        current_stage: str,
        pathway: List[Tuple],
        assertions: List[Tuple],
        risks: List[str],
        gaps: List[str],
        disease_profile: DiseaseProfile,
        narrative: str = "",
    ) -> str:
        """Generate comprehensive regulatory narrative"""
        
        lines = [
            "REGULATORY ASSESSMENT & PATHWAY",
            "=" * 70,
            "",
            f"Current Development Stage: {current_stage.replace('_', ' ').title()}",
            "",
            "RECOMMENDED REGULATORY PATHWAY:",
        ]
        
        for stage, studies in pathway:
            lines.append(f"\n{stage.replace('_', ' ').upper()}:")
            for study in studies:
                lines.append(f"  • {study}")
        
        lines.extend([
            "",
            "KEY REGULATORY ASSERTIONS:",
        ])
        
        for assertion, lang_level, confidence in assertions:
            conf_pct = f"{confidence*100:.0f}%"
            lines.append(f"  • [{lang_level}] {assertion} (confidence: {conf_pct})")
        
        if risks:
            lines.extend([
                "",
                "CRITICAL REGULATORY RISKS:",
            ])
            for risk in risks[:3]:  # Top 3 risks
                lines.append(f"  ⚠️ {risk}")
        
        if gaps:
            lines.extend([
                "",
                "EVIDENCE GAPS TO ADDRESS:",
            ])
            for gap in gaps[:3]:  # Top 3 gaps
                lines.append(f"  • {gap}")
        
        return "\n".join(lines)

    @staticmethod
    def _calculate_regulatory_confidence() -> float:
        """
        Regulatory assessment confidence.
        Lower than mechanistic because regulatory pathway depends on political/scientific
        consensus that evolves with clinical data
        """
        return 0.62  # 62% confidence in regulatory strategy
