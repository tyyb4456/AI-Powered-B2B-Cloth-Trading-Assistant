from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ClarificationAnalysis(BaseModel):
    """Analysis of supplier's clarification request with categorization and assessment"""
    
    clarification_type: str = Field(
        description="Primary category of clarification needed",
        enum=["specs", "quantity", "timeline", "payment", "logistics", "quality", "general"]
    )
    
    specific_questions: List[str] = Field(
        description="Exact questions the supplier asked, extracted from their message"
    )
    
    missing_information: List[str] = Field(
        description="Information gaps that need to be filled to provide complete answers"
    )
    
    urgency_level: str = Field(
        description="How urgent the clarification request is based on language and context",
        enum=["low", "medium", "high", "urgent"]
    )
    
    complexity_score: float = Field(
        description="Technical complexity of the clarification request (0.0 = simple, 1.0 = very complex)",
        ge=0.0,
        le=1.0
    )
    
    supplier_engagement_level: str = Field(
        description="Level of supplier interest and engagement based on question depth",
        enum=["low", "medium", "high"]
    )
    
    potential_deal_impact: str = Field(
        description="How this clarification might impact the deal progression"
    )
    
    requires_internal_consultation: bool = Field(
        False,
        description="Whether internal team consultation is needed before responding"
    )
    
    estimated_response_time: str = Field(
        description="Estimated time needed to prepare comprehensive response",
        enum=["immediate", "within_hour", "within_day", "multiple_days"]
    )
    
    confidence: float = Field(
        description="Confidence in the analysis accuracy (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

class ClarificationResponse(BaseModel):
    """Complete structured response providing clarification to supplier"""
    
    response_id: str = Field(
        description="Unique identifier for this clarification response"
    )
    
    response_type: str = Field(
        description="Type of clarification response being provided",
        enum=["direct_answer", "detailed_explanation", "conditional_answer", "partial_answer"]
    )
    
    main_response: str = Field(
        description="Primary clarification response body that addresses supplier's request",
        min_length=50,
        max_length=2000
    )
    
    specific_answers: Dict[str, str] = Field(
        description="Direct answers to each specific question asked by supplier"
    )
    
    additional_context: Optional[str] = Field(
        None,
        description="Additional background information or context that might be helpful"
    )
    
    technical_specifications: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed technical specs if the clarification involves technical questions"
    )
    
    commercial_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Commercial terms and conditions if relevant to the clarification"
    )
    
    next_steps: List[str] = Field(
        description="Clear next steps for both parties after this clarification"
    )
    
    followup_questions: Optional[List[str]] = Field(
        None,
        description="Questions to ask supplier back if we need more information from them"
    )
    
    requires_supplier_confirmation: bool = Field(
        False,
        description="Whether this clarification requires explicit confirmation from supplier"
    )
    
    requires_additional_input: bool = Field(
        False,
        description="Whether we need more information from user/internal team"
    )
    
    confidence_score: float = Field(
        description="Confidence in the provided clarification accuracy (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    urgency_for_response: str = Field(
        description="How quickly supplier should respond to maintain momentum",
        enum=["no_rush", "within_week", "within_days", "urgent"]
    )
    
    relationship_impact: str = Field(
        description="Expected impact on supplier relationship",
        enum=["positive", "neutral", "potentially_negative"]
    )

class TechnicalSpecification(BaseModel):
    """Detailed technical specification for fabric clarifications"""
    
    parameter: str = Field(description="Technical parameter name (e.g., GSM, weave type)")
    value: str = Field(description="Specific value or range")
    tolerance: Optional[str] = Field(None, description="Acceptable tolerance range")
    test_method: Optional[str] = Field(None, description="Testing method if applicable")
    certification_required: Optional[bool] = Field(None, description="Whether certification is needed")

class CommercialTerm(BaseModel):
    """Commercial terms and conditions for business clarifications"""
    
    term_type: str = Field(
        description="Type of commercial term",
        enum=["price", "payment", "delivery", "quantity", "quality", "penalty"]
    )
    description: str = Field(description="Clear description of the term")
    conditions: Optional[List[str]] = Field(None, description="Any conditions that apply")
    flexibility: Optional[str] = Field(
        None, 
        description="How flexible this term is",
        enum=["fixed", "negotiable", "conditional"]
    )

class ClarificationMetrics(BaseModel):
    """Metrics and tracking for clarification effectiveness"""
    
    questions_addressed: int = Field(description="Number of questions fully addressed")
    information_gaps_filled: int = Field(description="Number of information gaps resolved")
    response_comprehensiveness: float = Field(
        description="How comprehensive the response is (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    technical_accuracy_score: float = Field(
        description="Accuracy of technical information provided (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    estimated_supplier_satisfaction: float = Field(
        description="Estimated supplier satisfaction with clarification (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )