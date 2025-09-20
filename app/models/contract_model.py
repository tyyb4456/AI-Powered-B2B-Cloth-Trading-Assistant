from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ContractTerms(BaseModel):
    """Contract terms extracted from negotiation"""
    fabric_specifications: str = Field(
        ..., 
        description="Final fabric specifications (type, quality, GSM, etc.) as structured text"
    )
    quantity: int = Field(..., description="Final agreed quantity in meters/yards")
    unit_price: float = Field(..., description="Final unit price per meter/yard")
    total_value: float = Field(..., description="Total contract value")
    currency: str = Field(default="USD", description="Contract currency")
    
    delivery_terms: str = Field(
        ..., 
        description="Delivery timeline, shipping terms, incoterms as structured text"
    )
    payment_terms: str = Field(
        ..., 
        description="Payment schedule, methods, advance percentage as structured text"
    )
    quality_standards: str = Field(
        default="Standard quality control procedures", 
        description="Quality control, testing, certification requirements as structured text"
    )
    
    penalties_and_incentives: List[str] = Field(
        default_factory=list,
        description="List of penalty clauses for delays, quality issues, and incentives"
    )
    force_majeure: Optional[str] = Field(
        None,
        description="Force majeure clause details"
    )
    dispute_resolution: Optional[str] = Field(
        None,
        description="Dispute resolution mechanism"
    )

class ContractMetadata(BaseModel):
    """Contract metadata and tracking information"""
    contract_id: str = Field(..., description="Unique contract identifier")
    contract_type: str = Field(
        default="textile_procurement", 
        description="Type of contract"
    )
    contract_version: str = Field(default="1.0", description="Version number")
    
    buyer_company: str = Field(
        ..., 
        description="Buyer company details as structured text" 
    )
    supplier_company: str = Field(
        ..., 
        description="Supplier company details as structured text"
    )
    
    creation_date: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Contract creation timestamp in ISO format"
    )
    effective_date: Optional[str] = Field(
        None,
        description="Contract effective date in ISO format"
    )
    expiry_date: Optional[str] = Field(
        None,
        description="Contract expiry date in ISO format"
    )
    
    governing_law: str = Field(
        default="International Commercial Law",
        description="Governing law for the contract"
    )
    jurisdiction: Optional[str] = Field(
        None,
        description="Legal jurisdiction"
    )

class DraftedContract(BaseModel):
    """Complete drafted contract with all components"""
    contract_id: str = Field(..., description="Unique contract identifier")
    contract_title: str = Field(..., description="Contract title")
    
    # Core contract content
    preamble: str = Field(..., description="Contract introduction and parties")
    terms_and_conditions: str = Field(..., description="Main contract body")
    schedules_and_annexures: List[str] = Field(
        default_factory=list,
        description="Additional schedules, specifications, annexures as text"
    )
    signature_block: str = Field(..., description="Signature section")
    
    # Contract structure - using string representation instead of nested models
    contract_terms_summary: str = Field(..., description="Summary of structured contract terms")
    contract_metadata_summary: str = Field(..., description="Summary of contract metadata")
    
    # Review and approval
    review_status: str = Field(
        default="draft",
        description="Review status (draft, under_review, approved, executed)"
    )
    review_comments: List[str] = Field(
        default_factory=list,
        description="Review comments and feedback"
    )
    
    # Quality and compliance
    compliance_checklist: str = Field(
        default="Standard compliance requirements",
        description="Compliance requirements checklist as structured text"
    )
    legal_review_required: bool = Field(
        default=True,
        description="Whether legal review is required"
    )
    
    # Generation metadata
    confidence_score: float = Field(
        ..., 
        description="Confidence in contract completeness and accuracy (0.0 to 1.0)",
        ge=0.0, 
        le=1.0
    )
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Contract generation timestamp in ISO format"
    )
    
    # Next steps
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended next steps for contract execution"
    )

class ContractTemplate(BaseModel):
    """Template configuration for contract generation"""
    template_id: str = Field(..., description="Template identifier")
    template_name: str = Field(..., description="Template name")
    industry: str = Field(default="textile", description="Industry sector")
    contract_type: str = Field(..., description="Type of contract")
    
    # Template structure
    sections: List[str] = Field(..., description="Main contract sections")
    mandatory_clauses: List[str] = Field(..., description="Mandatory legal clauses")
    optional_clauses: List[str] = Field(..., description="Optional clauses")
    
    # Customization
    customizable_fields: str = Field(
        default="Standard customizable fields",
        description="Fields that can be customized as structured text"
    )
    default_terms: str = Field(
        default="Standard default terms",
        description="Default terms and values as structured text"
    )
    
    # Legal compliance
    jurisdiction_requirements: str = Field(
        default="Standard jurisdiction requirements",
        description="Jurisdiction-specific requirements as structured text"
    )
    compliance_standards: List[str] = Field(
        default_factory=list,
        description="Applicable compliance standards"
    )

class ContractReview(BaseModel):
    """Contract review and feedback structure"""
    review_id: str = Field(..., description="Review session identifier")
    reviewer_type: str = Field(..., description="Type of reviewer (legal, business, technical)")
    reviewer_info: str = Field(..., description="Reviewer information as structured text")
    
    review_date: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Review completion date in ISO format"
    )
    
    # Review results
    overall_status: str = Field(
        ...,
        description="Overall review status (approved, rejected, needs_revision)"
    )
    risk_assessment: str = Field(
        ...,
        description="Risk level (low, medium, high, critical)"
    )
    
    # Detailed feedback
    section_feedback: str = Field(
        default="No specific section feedback",
        description="Section-wise feedback with issues and suggestions as structured text"
    )
    missing_clauses: List[str] = Field(
        default_factory=list,
        description="Identified missing clauses"
    )
    problematic_terms: List[str] = Field(
        default_factory=list,
        description="Problematic terms with explanations"
    )
    
    # Recommendations
    priority_changes: List[str] = Field(
        default_factory=list,
        description="High priority changes required"
    )
    suggested_improvements: List[str] = Field(
        default_factory=list,
        description="Suggested improvements"
    )
    
    # Next steps
    next_review_required: bool = Field(
        default=False,
        description="Whether another review cycle is needed"
    )
    approval_authority: Optional[str] = Field(
        None,
        description="Required approval authority level"
    )