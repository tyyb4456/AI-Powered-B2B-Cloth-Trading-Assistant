from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FollowUpAnalysis(BaseModel):
    """Comprehensive analysis of supplier's delay request and follow-up requirements"""
    
    delay_reason: str = Field(
        description="Primary reason for supplier's delay",
        enum=[
            "management_approval",
            "production_planning", 
            "market_check",
            "internal_consultation",
            "seasonal_factors",
            "capacity_assessment",
            "technical_review",
            "financial_approval",
            "supply_chain_check"
        ]
    )
    
    delay_type: str = Field(
        description="Category of delay process",
        enum=["decision_time", "information_gathering", "approval_process", "capacity_check", "market_analysis"]
    )
    
    estimated_delay_duration: str = Field(
        description="Supplier's estimated time requirement",
        enum=["hours", "1_2_days", "3_5_days", "1_week", "2_weeks", "longer"]
    )
    
    supplier_commitment_level: str = Field(
        description="Assessment of supplier's genuine interest and commitment",
        enum=["high", "medium", "low", "uncertain"]
    )
    
    urgency_of_our_timeline: str = Field(
        description="How urgent our business timeline requirements are",
        enum=["flexible", "moderate", "tight", "critical"]
    )
    
    competitive_risk: str = Field(
        description="Risk level of losing opportunity to competitors during delay",
        enum=["low", "medium", "high"]
    )
    
    relationship_preservation_importance: str = Field(
        description="Strategic importance of maintaining this supplier relationship",
        enum=["low", "medium", "high", "critical"]
    )
    
    market_dynamics_impact: str = Field(
        description="How current market conditions affect the delay decision"
    )
    
    cultural_considerations: Optional[str] = Field(
        None,
        description="Cultural business practices affecting timing expectations"
    )
    
    supplier_track_record: Optional[str] = Field(
        None,
        description="Supplier's historical reliability and communication patterns"
    )
    
    deal_complexity_factor: float = Field(
        description="How complex this deal is (affects decision time needs) (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    confidence: float = Field(
        description="Confidence in the delay analysis accuracy (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

class FollowUpSchedule(BaseModel):
    """Strategic follow-up schedule with timing and escalation planning"""
    
    schedule_id: str = Field(
        description="Unique identifier for this follow-up schedule"
    )
    
    primary_follow_up_date: str = Field(
        description="Main follow-up date (ISO format YYYY-MM-DD)"
    )
    
    follow_up_method: str = Field(
        description="Primary communication method for follow-up",
        enum=["email", "phone", "video_call", "whatsapp", "mixed_approach"]
    )
    
    follow_up_intervals: List[str] = Field(
        description="Sequence of follow-up dates if multiple touches needed"
    )
    
    escalation_timeline: Optional[str] = Field(
        None,
        description="When to escalate approach if no response (ISO format)"
    )
    
    # Communication strategy
    initial_follow_up_tone: str = Field(
        description="Tone for first follow-up message",
        enum=["understanding", "gentle_reminder", "professional_urgency", "collaborative_check"]
    )
    
    escalation_tone: str = Field(
        description="Tone progression for subsequent follow-ups",
        enum=["gentle_to_firm", "maintain_collaborative", "deadline_focused", "alternative_seeking"]
    )
    
    # Content strategy
    value_reinforcement_points: List[str] = Field(
        description="Key value propositions to reinforce during follow-up"
    )
    
    urgency_factors_to_mention: List[str] = Field(
        description="Appropriate urgency factors to communicate"
    )
    
    relationship_building_elements: List[str] = Field(
        description="Elements to maintain/strengthen supplier relationship"
    )
    
    # Strategic planning
    alternative_actions: List[str] = Field(
        description="Alternative actions if supplier remains unresponsive"
    )
    
    deadline_for_decision: Optional[str] = Field(
        None,
        description="Final deadline for supplier decision (ISO format)"
    )
    
    contingency_triggers: List[str] = Field(
        description="Conditions that trigger contingency actions"
    )
    
    # Quality metrics
    confidence_in_schedule: float = Field(
        description="Confidence in follow-up schedule effectiveness (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    expected_success_probability: float = Field(
        description="Estimated probability of positive supplier response (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    # Monitoring
    success_metrics: List[str] = Field(
        description="How to measure follow-up success"
    )

class FollowUpMessage(BaseModel):
    """Strategic follow-up message for supplier communication"""
    
    message_id: str = Field(
        description="Unique identifier for this follow-up message"
    )
    
    message_type: str = Field(
        description="Type and purpose of follow-up message",
        enum=[
            "gentle_reminder",
            "status_check", 
            "deadline_notice",
            "relationship_maintenance",
            "value_reinforcement",
            "timeline_clarification"
        ]
    )
    
    subject_line: str = Field(
        description="Email subject line or message topic",
        max_length=100
    )
    
    message_body: str = Field(
        description="Complete follow-up message content",
        min_length=50,
        max_length=1500
    )
    
    # Strategic messaging elements
    key_message_points: List[str] = Field(
        description="Main strategic points covered in the message"
    )
    
    call_to_action: str = Field(
        description="Specific action or response requested from supplier"
    )
    
    deadline_mentioned: Optional[str] = Field(
        None,
        description="Any deadline communicated in the message"
    )
    
    value_propositions_included: List[str] = Field(
        description="Value propositions reinforced in message"
    )
    
    # Relationship management
    relationship_building_language: bool = Field(
        False,
        description="Whether message includes specific relationship-building elements"
    )
    
    cultural_adaptation_notes: Optional[str] = Field(
        None,
        description="Cultural communication adaptations applied"
    )
    
    tone_assessment: str = Field(
        description="Overall tone of the message",
        enum=["warm_collaborative", "professional_neutral", "business_focused", "urgency_balanced"]
    )
    
    # Response management
    expected_response_time: str = Field(
        description="Expected timeframe for supplier response",
        enum=["24_hours", "2_3_days", "week", "longer"]
    )
    
    next_follow_up_if_no_response: Optional[str] = Field(
        None,
        description="Next follow-up date if no response received"
    )
    
    response_tracking_method: str = Field(
        description="How to track and measure response",
        enum=["email_reply", "phone_callback", "meeting_scheduled", "any_communication"]
    )
    
    # Quality and effectiveness
    message_priority: str = Field(
        description="Priority level for this message",
        enum=["low", "medium", "high"]
    )
    
    confidence_score: float = Field(
        description="Confidence in message effectiveness (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    personalization_level: str = Field(
        description="Level of personalization applied to message",
        enum=["standard", "customized", "highly_personalized"]
    )

class FollowUpMetrics(BaseModel):
    """Metrics and tracking for follow-up effectiveness measurement"""
    
    schedule_created_date: str = Field(
        description="When the follow-up schedule was created"
    )
    
    supplier_response_received: bool = Field(
        False,
        description="Whether supplier responded to follow-up"
    )
    
    response_time_hours: Optional[float] = Field(
        None,
        description="Hours between follow-up and supplier response"
    )
    
    response_sentiment: Optional[str] = Field(
        None,
        description="Sentiment of supplier's response",
        enum=["positive", "neutral", "negative", "mixed"]
    )
    
    follow_up_effectiveness_score: Optional[float] = Field(
        None,
        description="Effectiveness rating of follow-up approach (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    relationship_impact: Optional[str] = Field(
        None,
        description="Impact on supplier relationship",
        enum=["strengthened", "maintained", "neutral", "strained"]
    )
    
    deal_outcome: Optional[str] = Field(
        None,
        description="Final outcome of the deal",
        enum=["closed_positive", "continued_negotiation", "supplier_declined", "we_moved_to_alternative"]
    )

class CulturalFollowUpGuidelines(BaseModel):
    """Cultural-specific guidelines for follow-up communication"""
    
    cultural_region: str = Field(
        description="Geographic/cultural region",
        enum=["east_asian", "south_asian", "european", "middle_eastern", "latin_american", "north_american", "international"]
    )
    
    typical_decision_timeframes: Dict[str, str] = Field(
        description="Expected decision timeframes for different types of requests"
    )
    
    preferred_communication_methods: List[str] = Field(
        description="Preferred communication methods in order of preference"
    )
    
    relationship_building_importance: str = Field(
        description="Importance of relationship building in communication",
        enum=["critical", "important", "moderate", "minimal"]
    )
    
    directness_preference: str = Field(
        description="Preference for direct vs indirect communication",
        enum=["very_direct", "moderately_direct", "diplomatic", "very_diplomatic"]
    )
    
    urgency_communication_style: str = Field(
        description="How to communicate urgency appropriately"
    )
    
    patience_expectations: str = Field(
        description="Cultural expectations around patience and timing"
    )

class FollowUpContingency(BaseModel):
    """Contingency actions and alternative strategies"""
    
    trigger_condition: str = Field(
        description="Condition that triggers this contingency"
    )
    
    contingency_action: str = Field(
        description="Specific action to take"
    )
    
    timeline_for_action: str = Field(
        description="When to implement this contingency"
    )
    
    success_probability: float = Field(
        description="Estimated success probability of contingency (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    resource_requirements: List[str] = Field(
        description="Resources needed to execute contingency"
    )
    
    risk_factors: List[str] = Field(
        description="Risks associated with this contingency action"
    )