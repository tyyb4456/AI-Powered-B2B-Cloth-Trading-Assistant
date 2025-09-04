from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Pydantic Models for structured data
class Supplier(BaseModel):
    """Individual supplier recommendation with scoring details"""
    supplier_id: str = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier company name")
    location: str = Field(..., description="Supplier location/country")
    price_per_unit: Optional[float] = Field(None, description="Price per unit (meter/kg/yard)")
    currency: str = Field(default="USD", description="Currency for pricing")
    lead_time_days: Optional[int] = Field(None, description="Production + shipping lead time in days")
    minimum_order_qty: Optional[float] = Field(None, description="Minimum order quantity")
    reputation_score: float = Field(..., description="Reliability score (0-10)", ge=0.0, le=10.0)
    specialties: List[str] = Field(default_factory=list, description="Supplier specializations")
    certifications: List[str] = Field(default_factory=list, description="Available certifications")
    contact_info: Dict[str, str] = Field(default_factory=dict, description="Contact details")
    notes: Optional[str] = Field(None, description="Additional notes about this supplier")
    overall_score: float = Field(..., description="Weighted overall score", ge=0.0, le=100.0)

class SupplierSearchResult(BaseModel):
    """Complete supplier sourcing results with analysis"""
    request_id: str = Field(..., description="Reference to the original request")
    total_suppliers_found: int = Field(..., description="Total number of suppliers found")
    filtered_suppliers: int = Field(..., description="Number after filtering")
    top_recommendations: List[Supplier] = Field(..., description="Top ranked suppliers (max 10)")
    search_strategy: str = Field(..., description="Strategy used for this search")
    market_insights: str = Field(..., description="Brief market analysis and recommendations")
    confidence: float = Field(..., description="Confidence in recommendations", ge=0.0, le=1.0)
    alternative_suggestions: Optional[List[str]] = Field(default_factory=list, description="Alternative options if results are limited")