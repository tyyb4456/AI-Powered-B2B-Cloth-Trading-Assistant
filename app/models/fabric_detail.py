from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Define Pydantic Models for Structured Output
class FabricDetails(BaseModel):
    """Structured fabric specifications extracted from user input"""
    type: Optional[str] = Field(None, description="Type of fabric (cotton, silk, polyester, denim, etc.)")
    quantity: Optional[float] = Field(None, description="Numeric quantity requested")
    unit: Optional[str] = Field(None, description="Unit of measurement (meters, tons, rolls, yards)")
    quality_specs: Optional[List[str]] = Field(default_factory=list, description="Quality specifications (GSM, organic, recycled, waterproof, etc.)")
    color: Optional[str] = Field(None, description="Color or pattern requirement")
    width: Optional[float] = Field(
        None, 
        description="Fabric width in inches or cm",
        gt=0
    )
    composition: Optional[str] = Field(
        None, 
        description="Fabric composition (e.g., '100% cotton', '80/20 cotton/polyester')"
    )
    finish: Optional[str] = Field(
        None, 
        description="Special fabric finish (e.g., 'pre-shrunk', 'mercerized', 'enzyme washed')"
    )
    certifications: Optional[List[str]] = Field(default_factory=list, description="Required certifications (GOTS, OEKO-TEX, etc.)")

class LogisticsDetails(BaseModel):
    """Delivery and logistics requirements"""
    destination: Optional[str] = Field(None, description="Delivery destination")
    timeline: Optional[str] = Field(None, description="Delivery timeline or urgency")
    timeline_days: Optional[int] = Field(None, description="Specific number of days if mentioned")

class PriceConstraints(BaseModel):
    """Budget and pricing constraints"""
    max_price: Optional[float] = Field(None, description="Maximum price per unit")
    currency: Optional[str] = Field(None, description="Currency (USD, EUR, etc.)")
    price_unit: Optional[str] = Field(None, description="Price unit (per meter, per kg, etc.)")

class ExtractedRequest(BaseModel):
    """Complete structured representation of user's trading request"""
    item_id: str = Field(description="Unique identifier for this request")
    request_type: str = Field(description="Type of request (get_quote, find_supplier, negotiate, etc.)")
    confidence: float = Field(
        ...,
        description="Overall confidence in the extraction (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    fabric_details: FabricDetails
    logistics_details: LogisticsDetails
    price_constraints: PriceConstraints
    urgency_level: str = Field("medium", description="Urgency level: low, medium, high, urgent")
    supplier_preference: Optional[str] = Field(
        None, 
        description="Preferred supplier region or specific supplier name"
    )
    moq_flexibility: Optional[bool] = Field(
        None, 
        description="Whether user is flexible with minimum order quantities"
    )
    payment_terms: Optional[str] = Field(None, description="Preferred payment terms (e.g., 'Net 30', 'Letter of Credit')")
    additional_notes: Optional[str] = Field(None, description="Any additional requirements or notes")
    needs_clarification: bool = Field(False, description="Whether the request needs follow-up questions")
    clarification_questions: Optional[List[str]] = Field(default_factory=list, description="Specific questions to ask for clarification")
    detailed_extraction: str = Field(None, description="Brirf extraction notes or any assumptions made for reference to tell the user")
    missing_info: List[str] = Field(
        default_factory=list,
        description="List of important parameters that couldn't be extracted"
    )