from pydantic import BaseModel,Field
from typing import List

# Pydantic Models for Structured Output
class EscalationSummary(BaseModel):
    """Structured summary of negotiation context for human review"""
    escalation_id: str = Field(description="Unique identifier for this escalation")
    escalation_reason: str = Field(description="Primary reason for human escalation")
    urgency_level: str = Field(description="Urgency level: low, medium, high, critical")
    negotiation_overview: str = Field(description="Brief overview of the negotiation progress")
    key_sticking_points: List[str] = Field(description="Main issues preventing agreement")
    supplier_profile: str = Field(description="Relevant supplier information and history")
    current_terms_gap: str = Field(description="Difference between our position and supplier's position")
    recommended_human_actions: List[str] = Field(description="Specific actions human negotiator should consider")
    fallback_options: List[str] = Field(description="Alternative approaches if current negotiation fails")
    timeline_pressure: str = Field(description="Time constraints and deadline implications")
    relationship_implications: str = Field(description="Impact on long-term supplier relationship")
    risk_assessment: str = Field(description="Potential risks if negotiation fails")
    success_probability: float = Field(
        description="Estimated probability of successful resolution (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    next_suggested_steps: List[str] = Field(description="Immediate next steps for human negotiator")
    context_preservation_notes: str = Field(description="Important context that must be preserved")

class HumanInterventionRequest(BaseModel):
    """Request structure for human intervention with all necessary context"""
    request_id: str = Field(description="Unique identifier for this intervention request")
    request_type: str = Field(description="Type of intervention needed")
    priority_level: str = Field(description="Priority level for human attention")
    escalation_trigger: str = Field(description="What triggered the escalation")
    negotiation_context: str = Field(description="Complete context of current negotiation state")
    supplier_details: str = Field(description="Supplier information and communication style")
    original_requirements: str = Field(description="Original user request and requirements")
    negotiation_history: str = Field(description="Summary of negotiation rounds and key events")
    current_obstacles: List[str] = Field(description="Current obstacles preventing agreement")
    strategic_recommendations: List[str] = Field(description="Strategic recommendations for human negotiator")
    communication_notes: str = Field(description="Important communication style and cultural considerations")
    deadline_constraints: str = Field(description="Time constraints and urgency factors")
    alternative_suppliers: str = Field(description="Information about alternative suppliers if available")
    expected_human_input: str = Field(description="What specific input or decision is needed from human")
    confidence_in_ai_analysis: float = Field(
        description="Confidence level in AI's analysis and recommendations",
        ge=0.0,
        le=1.0
    )
