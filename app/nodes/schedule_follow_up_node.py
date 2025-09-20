from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import json

load_dotenv()

# Pydantic Models for Structured Output
class FollowUpAnalysis(BaseModel):
    """Analysis of supplier's delay request and follow-up requirements"""
    delay_reason: str = Field(description="Primary reason for supplier's delay (management_approval, production_planning, market_check, internal_consultation, seasonal_factors)")
    delay_type: str = Field(description="Type of delay (decision_time, information_gathering, approval_process, capacity_check)")
    estimated_delay_duration: str = Field(description="Estimated time supplier needs (hours, days, weeks)")
    supplier_commitment_level: str = Field(description="How committed supplier seems (high, medium, low, uncertain)")
    urgency_of_our_timeline: str = Field(description="How urgent our timeline is (flexible, moderate, tight, critical)")
    competitive_risk: str = Field(description="Risk of losing to competitors during delay (low, medium, high)")
    relationship_preservation_importance: str = Field(description="Importance of maintaining this supplier relationship (low, medium, high, critical)")
    market_dynamics_impact: str = Field(description="How market conditions affect the delay decision")

class FollowUpSchedule(BaseModel):
    """Structured follow-up schedule and timing strategy"""
    schedule_id: str = Field(description="Unique identifier for this follow-up schedule")
    primary_follow_up_date: str = Field(description="Main follow-up date (ISO format)")
    follow_up_method: str = Field(description="Method of follow-up (email, phone, video_call, whatsapp)")
    follow_up_intervals: List[str] = Field(description="Sequence of follow-up dates if needed")
    escalation_timeline: Optional[str] = Field(None, description="When to escalate if no response")
    
    # Message strategy
    initial_follow_up_tone: str = Field(description="Tone for first follow-up (understanding, gentle_reminder, professional_urgency)")
    escalation_tone: str = Field(description="Tone for later follow-ups if needed (firm, deadline_focused, alternative_seeking)")
    
    # Content strategy
    value_reinforcement_points: List[str] = Field(description="Key points to reinforce our value proposition")
    urgency_factors_to_mention: List[str] = Field(description="Urgency factors to communicate appropriately")
    relationship_building_elements: List[str] = Field(description="Elements to maintain/build relationship")
    
    # Contingency planning
    alternative_actions: List[str] = Field(description="Alternative actions if supplier remains unresponsive")
    deadline_for_decision: Optional[str] = Field(None, description="Final deadline for supplier decision")
    
    confidence_in_schedule: float = Field(description="Confidence in the follow-up schedule effectiveness (0.0 to 1.0)", ge=0.0, le=1.0)

class FollowUpMessage(BaseModel):
    """Follow-up message to send to supplier"""
    message_id: str = Field(description="Unique identifier for this follow-up message")
    message_type: str = Field(description="Type of follow-up message (gentle_reminder, status_check, deadline_notice, relationship_maintenance)")
    subject_line: str = Field(description="Email subject line or message topic")
    message_body: str = Field(description="Main follow-up message content", min_length=50, max_length=1500)
    
    # Strategic elements
    key_message_points: List[str] = Field(description="Main points covered in the message")
    call_to_action: str = Field(description="Specific action requested from supplier")
    deadline_mentioned: Optional[str] = Field(None, description="Any deadline mentioned in message")
    
    # Relationship management
    relationship_building_language: bool = Field(False, description="Whether message includes relationship-building language")
    cultural_adaptation_notes: Optional[str] = Field(None, description="Cultural considerations applied to message")
    
    # Follow-up logistics
    expected_response_time: str = Field(description="Expected response timeframe (24_hours, 2_3_days, week, longer)")
    next_follow_up_if_no_response: Optional[str] = Field(None, description="Next follow-up date if no response")
    
    message_priority: str = Field(description="Message priority level (low, medium, high)")
    confidence_score: float = Field(description="Confidence in message effectiveness (0.0 to 1.0)", ge=0.0, le=1.0)

def create_follow_up_analysis_prompt():
    """Create prompt for analyzing supplier delay and follow-up requirements"""
    
    system_prompt = """You are an expert B2B negotiation strategist specializing in timing management and supplier relationship dynamics. Your expertise includes cross-cultural business practices, supply chain psychology, and strategic follow-up planning.

Your task is to analyze supplier delay requests and develop optimal follow-up strategies that balance urgency with relationship preservation.

**DELAY REASON ANALYSIS:**

1. **Management Approval (management_approval):**
   - Supplier needs internal management sign-off
   - Often involves pricing, terms, or capacity decisions
   - Usually 2-5 business days in most cultures
   - Shows serious consideration

2. **Production Planning (production_planning):**
   - Checking production capacity and scheduling
   - Coordinating with production teams
   - May involve raw material availability checks
   - Typically 1-3 days for established suppliers

3. **Market Check (market_check):**
   - Comparing with other opportunities
   - Checking current market rates
   - May indicate competitive shopping
   - Risk of losing opportunity

4. **Internal Consultation (internal_consultation):**
   - Consulting with technical, quality, or logistics teams
   - Getting expert opinions on specifications
   - Usually indicates serious consideration
   - Timeframe varies by complexity

5. **Seasonal Factors (seasonal_factors):**
   - Holiday periods, festival seasons
   - Fiscal year-end considerations
   - Industry seasonal patterns
   - May require longer patience

**COMMITMENT LEVEL ASSESSMENT:**
- **High**: Specific timeline, detailed reasons, proactive communication
- **Medium**: General interest, some engagement, vague timing
- **Low**: Minimal explanation, avoiding commitments
- **Uncertain**: Mixed signals, unclear intentions

**URGENCY CALIBRATION:**
- Consider our original timeline requirements
- Assess competitive marketplace dynamics
- Evaluate seasonal market factors
- Balance relationship preservation vs. speed

**CULTURAL CONSIDERATIONS:**
- **Asian cultures**: More time for consensus-building, face-saving important
- **European cultures**: Process-oriented, respect for procedures
- **Middle Eastern**: Relationship emphasis, patience with decision-making
- **Latin American**: Personal relationship factors, flexible timing
- **North American**: Efficiency-focused, clear timeline expectations

Be strategic about timing - too aggressive risks relationship damage, too passive risks losing opportunities."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Analyze this supplier delay situation and develop follow-up strategy:

**SUPPLIER'S MESSAGE:**
{supplier_message}

**NEGOTIATION CONTEXT:**
- Current round: {negotiation_round}
- Time in negotiation: {negotiation_duration}
- Our original urgency: {original_urgency}
- Deal importance: {deal_importance}

**SUPPLIER PROFILE:**
- Company: {supplier_name}
- Location: {supplier_location}  
- Cultural region: {cultural_region}
- Reliability score: {reliability_score}
- Previous relationship: {relationship_history}

**MARKET CONTEXT:**
- Alternative suppliers available: {alternatives_count}
- Market conditions: {market_conditions}
- Seasonal factors: {seasonal_factors}

**OUR POSITION:**
- Timeline flexibility: {timeline_flexibility}
- Deal priority: {deal_priority}
- Relationship importance: {relationship_importance}

Analyze the delay request and assess optimal follow-up strategy.""")
    ])

def create_follow_up_schedule_prompt():
    """Create prompt for developing follow-up schedule and strategy"""
    
    system_prompt = """You are a senior B2B relationship manager and timing strategist with expertise in international business practices and supplier relationship optimization. Your role is to design follow-up schedules that maximize deal closure probability while preserving valuable supplier relationships.

Your expertise covers:
- Cross-cultural business timing expectations
- Escalation strategies and relationship preservation
- Market dynamics and competitive timing
- Communication frequency optimization
- Deadline management and pressure application

**FOLLOW-UP STRATEGY FRAMEWORK:**

**1. TIMING OPTIMIZATION:**
- Initial follow-up: Based on supplier's stated timeline + buffer
- Reminder frequency: Balanced to maintain presence without annoyance
- Escalation points: Clear progression from gentle to firm
- Decision deadlines: Realistic but motivating

**2. COMMUNICATION METHODS:**
- **Email**: Standard, documented, non-intrusive
- **Phone**: More personal, immediate feedback, relationship building
- **Video call**: High-importance deals, complex discussions
- **WhatsApp/SMS**: Informal follow-up, quick status checks

**3. MESSAGE TONE PROGRESSION:**
- **Understanding**: Acknowledge their need for time
- **Gentle reminder**: Friendly check-in on progress
- **Professional urgency**: Communicate time sensitivity
- **Deadline focused**: Clear about final timeline
- **Alternative seeking**: Indicate other options being considered

**4. VALUE REINFORCEMENT:**
Throughout follow-ups, reinforce:
- Partnership benefits and long-term value
- Unique advantages of working together
- Market opportunities and timing
- Competitive advantages and positioning

**5. CULTURAL ADAPTATION:**
- **East Asian**: Longer follow-up intervals, face-saving language, relationship emphasis
- **European**: Process respect, clear timelines, professional communication
- **Middle Eastern**: Personal relationship focus, patience with decision-making
- **Latin American**: Relationship building, personal touch, flexible approach
- **North American**: Direct communication, efficiency focus, clear expectations

**6. CONTINGENCY PLANNING:**
- Alternative supplier activation points
- Internal decision points for proceeding
- Market opportunity cost considerations
- Relationship preservation vs. deal closure balance

**SCHEDULE DESIGN PRINCIPLES:**
- Build in cultural expectations for decision-making time
- Create multiple touchpoints without being overwhelming
- Provide clear value and urgency communication
- Include relationship preservation elements
- Plan for both positive and negative outcomes
- Balance patience with business necessity

Design schedules that optimize for both deal closure and long-term supplier relationship value."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Design comprehensive follow-up schedule based on analysis:

**DELAY ANALYSIS:**
- Delay reason: {delay_reason}
- Estimated duration: {estimated_delay_duration}
- Supplier commitment: {supplier_commitment_level}
- Competitive risk: {competitive_risk}

**STRATEGIC CONTEXT:**
- Our urgency level: {urgency_of_our_timeline}
- Relationship importance: {relationship_preservation_importance}
- Market dynamics: {market_dynamics_impact}
- Cultural region: {cultural_region}

**SUPPLIER INFORMATION:**
- Company: {supplier_name}
- Location: {supplier_location}
- Reliability: {reliability_score}
- Previous communication style: {communication_style}

**BUSINESS PARAMETERS:**
- Deal value/importance: {deal_importance}
- Alternative options: {alternative_suppliers}
- Timeline flexibility: {timeline_flexibility}
- Decision deadline: {internal_deadline}

**ORIGINAL REQUEST CONTEXT:**
- Product: {product_summary}
- Urgency: {original_urgency}
- Volume: {order_volume}

Design optimal follow-up schedule with clear timing, methods, and messaging strategy.""")
    ])

def create_follow_up_message_prompt():
    """Create prompt for drafting initial follow-up message"""
    
    system_prompt = """You are an expert B2B communication specialist with deep expertise in supplier relationship management and cross-cultural business communication. Your role is to craft follow-up messages that maintain momentum, preserve relationships, and optimize for positive responses.

Your expertise includes:
- International business communication protocols
- Supplier psychology and motivation factors  
- Cultural sensitivity in business messaging
- Urgency communication without relationship damage
- Value proposition reinforcement strategies

**FOLLOW-UP MESSAGE FRAMEWORK:**

**1. MESSAGE STRUCTURE:**
- **Opening**: Acknowledge their situation and request for time
- **Context**: Reinforce project importance and mutual benefits
- **Status Check**: Politely inquire about their progress/timeline
- **Value Reinforcement**: Remind of partnership benefits
- **Clear Action**: Specific, reasonable request for next steps
- **Relationship Preservation**: Maintain collaborative tone

**2. TONE CALIBRATION:**
- **Gentle Reminder**: Understanding, supportive, relationship-focused
- **Status Check**: Professional inquiry, collaborative problem-solving
- **Deadline Notice**: Firm but respectful, clear consequences
- **Relationship Maintenance**: Long-term focus, partnership emphasis

**3. CULTURAL ADAPTATION:**

- **East Asian Markets**: Indirect approach, face-saving language, patience acknowledgment
  - "We completely understand your need for thorough consideration..."
  - "When it's convenient for your team, we'd appreciate an update..."

- **European Markets**: Professional, process-oriented, clear expectations
  - "Following up on our previous discussion regarding timeline..."
  - "We'd appreciate confirmation of your expected decision timeframe..."

- **Middle Eastern Markets**: Relationship emphasis, personal respect, patience
  - "We value our developing partnership and understand the importance of proper consideration..."
  - "At your convenience, we'd welcome any update you can share..."

- **Latin American Markets**: Personal warmth, relationship building, flexible approach
  - "We hope you and your team are doing well..."
  - "We're excited about the possibility of working together and wanted to check in..."

- **North American Markets**: Direct, efficient, business-focused
  - "Following up on our proposal to understand your timeline..."
  - "We'd appreciate an update on your decision process..."

**4. VALUE PROPOSITION REINFORCEMENT:**
Subtly remind of:
- Partnership benefits and competitive advantages
- Market timing and opportunity considerations
- Quality and reliability factors
- Long-term relationship potential
- Unique value propositions of the deal

**5. URGENCY COMMUNICATION:**
- Balance time sensitivity with relationship preservation
- Provide business rationale for timing needs
- Offer collaborative solutions for timing challenges
- Avoid ultimatums in early follow-ups
- Communicate market dynamics appropriately

**6. CALL TO ACTION OPTIMIZATION:**
- Be specific about what you're requesting
- Provide reasonable timeframes for response
- Offer multiple ways to communicate
- Make it easy for supplier to respond positively
- Include alternative options when appropriate

**MESSAGE QUALITY STANDARDS:**
- Professional yet personable tone
- Clear, concise communication
- Cultural sensitivity and adaptation
- Value-focused rather than pressure-focused
- Relationship-preserving language
- Actionable and specific requests

Generate messages that suppliers want to respond to positively while maintaining business momentum."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Draft follow-up message based on schedule and analysis:

**FOLLOW-UP SCHEDULE:**
- Message type: {message_type}
- Follow-up method: {follow_up_method}
- Tone: {initial_follow_up_tone}
- Priority: {message_priority}

**SUPPLIER PROFILE:**
- Company: {supplier_name}
- Location: {supplier_location}
- Cultural region: {cultural_region}
- Communication style: {communication_style}

**STRATEGIC CONTEXT:**
- Delay reason: {delay_reason}
- Our urgency: {urgency_level}
- Relationship importance: {relationship_importance}
- Value points to reinforce: {value_reinforcement_points}

**ORIGINAL REQUEST:**
- Product summary: {product_summary}
- Order importance: {order_importance}
- Timeline requirements: {timeline_requirements}

**MESSAGE PARAMETERS:**
- Expected response time: {expected_response_time}
- Cultural adaptation needed: {cultural_adaptation}
- Deadline to mention: {deadline_mentioned}
- Call to action: {call_to_action}

Draft a complete follow-up message that maintains momentum while preserving the supplier relationship.""")
    ])

# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
analysis_model = model.with_structured_output(FollowUpAnalysis)
schedule_model = model.with_structured_output(FollowUpSchedule)
message_model = model.with_structured_output(FollowUpMessage)

analysis_prompt = create_follow_up_analysis_prompt()
schedule_prompt = create_follow_up_schedule_prompt()
message_prompt = create_follow_up_message_prompt()

def extract_follow_up_context(state: AgentState) -> Dict[str, Any]:
    """Extract relevant context for follow-up planning from current state"""
    
    # Get negotiation timeline
    messages = state.get('messages1', []) + state.get('msgs', [])
    negotiation_round = len([msg for msg in messages if 'negotiate' in str(msg).lower()]) + 1
    
    # Calculate negotiation duration (approximate)
    negotiation_history = state.get('negotiation_history', [])
    negotiation_duration = f"{len(negotiation_history)} days" if negotiation_history else "1 day"
    
    # Extract original request context
    extracted_params = state.get('extracted_parameters', {})
    
    # Get supplier information
    supplier_data = {}
    top_suppliers = state.get('top_suppliers', [])
    if top_suppliers:
        supplier_data = top_suppliers[0]
    
    # Determine market context
    market_conditions = determine_market_conditions(state)
    alternatives_count = len(top_suppliers) - 1 if len(top_suppliers) > 1 else 0
    
    return {
        'negotiation_round': negotiation_round,
        'negotiation_duration': negotiation_duration,
        'supplier_data': supplier_data,
        'extracted_params': extracted_params,
        'market_conditions': market_conditions,
        'alternatives_count': alternatives_count
    }

def determine_market_conditions(state: AgentState) -> str:
    """Determine current market conditions based on available data"""
    
    # This could be enhanced with real market data
    urgency = state.get('extracted_parameters', {}).get('urgency_level', 'medium')
    
    if urgency == 'urgent':
        return 'tight_supply_market'
    elif urgency == 'high':
        return 'competitive_market'
    else:
        return 'stable_market'

def determine_cultural_region(location: str) -> str:
    """Determine cultural communication region based on supplier location"""
    location_lower = location.lower()
    
    if any(country in location_lower for country in ['china', 'japan', 'korea', 'taiwan', 'singapore', 'hong kong']):
        return 'east_asian'
    elif any(country in location_lower for country in ['india', 'pakistan', 'bangladesh', 'sri lanka']):
        return 'south_asian'  
    elif any(country in location_lower for country in ['germany', 'italy', 'france', 'uk', 'netherlands', 'spain']):
        return 'european'
    elif any(country in location_lower for country in ['uae', 'turkey', 'egypt', 'saudi']):
        return 'middle_eastern'
    elif any(country in location_lower for country in ['mexico', 'brazil', 'argentina', 'colombia']):
        return 'latin_american'
    elif any(country in location_lower for country in ['usa', 'canada']):
        return 'north_american'
    else:
        return 'international'

def calculate_follow_up_dates(delay_duration: str, cultural_region: str) -> List[str]:
    """Calculate appropriate follow-up dates based on delay duration and culture"""
    
    base_date = datetime.now()
    follow_up_dates = []
    
    # Parse delay duration
    if 'hour' in delay_duration:
        primary_delay = timedelta(hours=24)  # Give at least a day
        follow_up_interval = timedelta(days=1)
    elif 'day' in delay_duration:
        days = int(''.join(filter(str.isdigit, delay_duration)) or 3)
        primary_delay = timedelta(days=days)
        follow_up_interval = timedelta(days=max(2, days // 2))
    elif 'week' in delay_duration:
        weeks = int(''.join(filter(str.isdigit, delay_duration)) or 1)
        primary_delay = timedelta(weeks=weeks)
        follow_up_interval = timedelta(days=3)
    else:
        primary_delay = timedelta(days=3)
        follow_up_interval = timedelta(days=2)
    
    # Cultural adjustments
    if cultural_region in ['east_asian', 'middle_eastern']:
        primary_delay *= 1.5  # More time for consensus cultures
    elif cultural_region == 'north_american':
        primary_delay *= 0.8  # Faster decision cultures
    
    # Generate follow-up dates
    primary_followup = base_date + primary_delay
    follow_up_dates.append(primary_followup.strftime('%Y-%m-%d'))
    
    # Add additional follow-ups
    for i in range(2):
        next_followup = primary_followup + (follow_up_interval * (i + 1))
        follow_up_dates.append(next_followup.strftime('%Y-%m-%d'))
    
    return follow_up_dates

def create_product_summary(extracted_params: Dict[str, Any]) -> str:
    """Create brief product summary for follow-up messages"""
    
    fabric_details = extracted_params.get('fabric_details', {})
    
    summary_parts = []
    
    if fabric_details.get('type'):
        summary_parts.append(fabric_details['type'])
    
    if fabric_details.get('quantity'):
        unit = fabric_details.get('unit', 'units')
        summary_parts.append(f"{fabric_details['quantity']} {unit}")
    
    if fabric_details.get('quality_specs'):
        summary_parts.append(f"({', '.join(fabric_details['quality_specs'][:2])})")
    
    return " ".join(summary_parts) if summary_parts else "textile order"

def schedule_follow_up(state: AgentState) -> dict:
    """
    Node: schedule_follow_up - Supplier delay and follow-up management system
    
    Purpose:
    - Analyze supplier delay requests and develop strategic follow-up plans
    - Create culturally-appropriate follow-up schedules and messaging
    - Balance urgency with relationship preservation
    - Maintain negotiation momentum during supplier decision periods
    - Plan contingency actions and escalation strategies
    
    Args:
        state: Current agent state containing supplier's delay request and context
    
    Returns:
        dict: State updates with follow-up analysis, schedule, and initial message
    """
    
    try:
        # Step 1: Extract supplier message and context
        supplier_message = state.get('supplier_response') or state.get('human_response')
        
        if not supplier_message:
            return {
                "error": "No supplier delay message found",
                "messages1": ["No supplier delay request to process"],
                "status": "no_delay_request"
            }
        
        context = extract_follow_up_context(state)
        supplier_info = context['supplier_data']
        cultural_region = determine_cultural_region(supplier_info.get('location', ''))
        
        # Step 2: Analyze the delay situation
        analysis_formatted_prompt = analysis_prompt.invoke({
            "supplier_message": supplier_message,
            "negotiation_round": context['negotiation_round'],
            "negotiation_duration": context['negotiation_duration'],
            "original_urgency": context['extracted_params'].get('urgency_level', 'medium'),
            "deal_importance": determine_deal_importance(context['extracted_params']),
            "supplier_name": supplier_info.get('name', 'Supplier'),
            "supplier_location": supplier_info.get('location', 'Unknown'),
            "cultural_region": cultural_region,
            "reliability_score": supplier_info.get('reliability_score', 5.0),
            "relationship_history": supplier_info.get('notes', 'New supplier'),
            "alternatives_count": context['alternatives_count'],
            "market_conditions": context['market_conditions'],
            "seasonal_factors": determine_seasonal_factors(),
            "timeline_flexibility": determine_timeline_flexibility(context['extracted_params']),
            "deal_priority": context['extracted_params'].get('urgency_level', 'medium'),
            "relationship_importance": determine_relationship_importance(supplier_info)
        })
        
        follow_up_analysis: FollowUpAnalysis = analysis_model.invoke(analysis_formatted_prompt)
        
        # Step 3: Develop follow-up schedule
        schedule_formatted_prompt = schedule_prompt.invoke({
            "delay_reason": follow_up_analysis.delay_reason,
            "estimated_delay_duration": follow_up_analysis.estimated_delay_duration,
            "supplier_commitment_level": follow_up_analysis.supplier_commitment_level,
            "competitive_risk": follow_up_analysis.competitive_risk,
            "urgency_of_our_timeline": follow_up_analysis.urgency_of_our_timeline,
            "relationship_preservation_importance": follow_up_analysis.relationship_preservation_importance,
            "market_dynamics_impact": follow_up_analysis.market_dynamics_impact,
            "cultural_region": cultural_region,
            "supplier_name": supplier_info.get('name', 'Supplier'),
            "supplier_location": supplier_info.get('location', 'Unknown'),
            "reliability_score": supplier_info.get('reliability_score', 5.0),
            "communication_style": determine_communication_style(supplier_info),
            "deal_importance": determine_deal_importance(context['extracted_params']),
            "alternative_suppliers": context['alternatives_count'],
            "timeline_flexibility": determine_timeline_flexibility(context['extracted_params']),
            "internal_deadline": calculate_internal_deadline(context['extracted_params']),
            "product_summary": create_product_summary(context['extracted_params']),
            "original_urgency": context['extracted_params'].get('urgency_level', 'medium'),
            "order_volume": context['extracted_params'].get('fabric_details', {}).get('quantity', 'standard')
        })
        
        follow_up_schedule: FollowUpSchedule = schedule_model.invoke(schedule_formatted_prompt)
        
        # Step 4: Generate follow-up dates
        follow_up_dates = calculate_follow_up_dates(
            follow_up_analysis.estimated_delay_duration, 
            cultural_region
        )
        follow_up_schedule.follow_up_intervals = follow_up_dates
        
        # Step 5: Draft initial follow-up message
        message_formatted_prompt = message_prompt.invoke({
            "message_type": follow_up_schedule.initial_follow_up_tone,
            "follow_up_method": follow_up_schedule.follow_up_method,
            "initial_follow_up_tone": follow_up_schedule.initial_follow_up_tone,
            "message_priority": determine_message_priority(follow_up_analysis),
            "supplier_name": supplier_info.get('name', 'Supplier'),
            "supplier_location": supplier_info.get('location', 'Unknown'),
            "cultural_region": cultural_region,
            "communication_style": determine_communication_style(supplier_info),
            "delay_reason": follow_up_analysis.delay_reason,
            "urgency_level": follow_up_analysis.urgency_of_our_timeline,
            "relationship_importance": follow_up_analysis.relationship_preservation_importance,
            "value_reinforcement_points": follow_up_schedule.value_reinforcement_points,
            "product_summary": create_product_summary(context['extracted_params']),
            "order_importance": determine_deal_importance(context['extracted_params']),
            "timeline_requirements": context['extracted_params'].get('logistics_details', {}).get('timeline', 'standard'),
            "expected_response_time": calculate_expected_response_time(follow_up_analysis),
            "cultural_adaptation": cultural_region,
            "deadline_mentioned": follow_up_schedule.deadline_for_decision,
            "call_to_action": "Please provide an update on your decision timeline"
        })
        
        follow_up_message: FollowUpMessage = message_model.invoke(message_formatted_prompt)
        
        # Step 6: Set message metadata
        message_id = f"followup_{str(uuid.uuid4())[:8]}"
        schedule_id = f"schedule_{str(uuid.uuid4())[:8]}"
        
        follow_up_message.message_id = message_id
        follow_up_schedule.schedule_id = schedule_id
        
        # Step 7: Update follow-up schedule in state
        follow_up_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "follow_up_scheduled",
            "delay_reason": follow_up_analysis.delay_reason,
            "schedule_id": schedule_id,
            "next_follow_up": follow_up_dates[0],
            "supplier_commitment": follow_up_analysis.supplier_commitment_level
        }
        
        updated_history = state.get('negotiation_history', []) + [follow_up_entry]
        
        # Step 8: Create assistant response message
        assistant_message = f"""📅 **Follow-up Schedule Created**

**Delay Analysis:**
- Reason: {follow_up_analysis.delay_reason.replace('_', ' ').title()}
- Duration: {follow_up_analysis.estimated_delay_duration}
- Supplier commitment: {follow_up_analysis.supplier_commitment_level.title()}
- Competitive risk: {follow_up_analysis.competitive_risk.title()}

**Follow-up Strategy:**
- Primary follow-up: {follow_up_dates[0]}
- Method: {follow_up_schedule.follow_up_method}
- Tone: {follow_up_schedule.initial_follow_up_tone.replace('_', ' ').title()}
- Escalation: {follow_up_schedule.escalation_timeline or 'As needed'}

**Message Prepared:**
- Type: {follow_up_message.message_type}
- Priority: {follow_up_message.message_priority}
- Expected response: {follow_up_message.expected_response_time}

**Schedule Confidence:** {follow_up_schedule.confidence_in_schedule:.2f}/1.0

Ready to maintain momentum while respecting supplier's timeline needs."""
        
        # Step 9: Determine next step
        if follow_up_analysis.supplier_commitment_level == 'low':
            next_step = "consider_alternative_suppliers"
        elif follow_up_analysis.competitive_risk == 'high':
            next_step = "accelerate_alternative_sourcing"
        else:
            next_step = "send_follow_up_message"
        
        # Step 10: Prepare comprehensive state updates
        state_updates = {
            "follow_up_analysis": follow_up_analysis.model_dump(),
            "follow_up_schedule": follow_up_schedule.model_dump(),
            "follow_up_message": follow_up_message.model_dump(),
            "schedule_id": schedule_id,
            "message_id": message_id,
            "follow_up_dates": follow_up_dates,
            "next_follow_up_date": follow_up_dates[0],
            "follow_up_ready": True,
            "next_step": next_step,
            "messages1": [assistant_message],
            "status": "follow_up_scheduled",
            "negotiation_history": updated_history,
            "last_follow_up_confidence": follow_up_schedule.confidence_in_schedule
        }
        
        # Add risk management flags
        if follow_up_analysis.competitive_risk == 'high':
            state_updates["high_competitive_risk"] = True
            state_updates["risk_mitigation_actions"] = follow_up_schedule.alternative_actions
        
        if follow_up_analysis.supplier_commitment_level == 'low':
            state_updates["low_supplier_commitment"] = True
            state_updates["consider_alternatives"] = True
        
        # Add monitoring alerts
        if follow_up_schedule.confidence_in_schedule < 0.6:
            state_updates["requires_human_review"] = True
            state_updates["low_confidence_areas"] = ["follow_up_strategy", "timing_optimization"]
        
        return state_updates
        
    except Exception as e:
        error_message = f"Error in scheduling follow-up: {str(e)}"
        return {
            "error": str(e),
            "messages1": [error_message],
            "next_step": "handle_error",
            "status": "follow_up_error"
        }

def determine_deal_importance(extracted_params: Dict[str, Any]) -> str:
    """Determine deal importance based on order parameters"""
    
    fabric_details = extracted_params.get('fabric_details', {})
    urgency = extracted_params.get('urgency_level', 'medium')
    quantity = fabric_details.get('quantity', 0)
    
    if urgency == 'urgent' or quantity > 50000:
        return 'high'
    elif urgency == 'high' or quantity > 10000:
        return 'medium'
    else:
        return 'standard'

def determine_timeline_flexibility(extracted_params: Dict[str, Any]) -> str:
    """Determine how flexible our timeline is"""
    
    urgency = extracted_params.get('urgency_level', 'medium')
    logistics = extracted_params.get('logistics_details', {})
    
    if urgency == 'urgent':
        return 'tight'
    elif urgency == 'high':
        return 'moderate'
    elif logistics.get('timeline_days') and logistics['timeline_days'] < 30:
        return 'moderate'
    else:
        return 'flexible'

def determine_relationship_importance(supplier_info: Dict[str, Any]) -> str:
    """Determine importance of maintaining this supplier relationship"""
    
    reliability = supplier_info.get('reliability_score', 5.0)
    
    if reliability >= 8.0:
        return 'critical'
    elif reliability >= 6.0:
        return 'high'
    elif reliability >= 4.0:
        return 'medium'
    else:
        return 'low'

def determine_seasonal_factors() -> str:
    """Determine current seasonal business factors"""
    
    current_month = datetime.now().month
    
    if current_month in [1, 2]:  # January-February
        return 'post_holiday_season'
    elif current_month in [11, 12]:  # November-December
        return 'holiday_season'
    elif current_month in [6, 7, 8]:  # Summer months
        return 'summer_production_peak'
    else:
        return 'standard_season'

def determine_communication_style(supplier_info: Dict[str, Any]) -> str:
    """Determine supplier's preferred communication style"""
    
    # This could be enhanced with historical communication data
    location = supplier_info.get('location', '').lower()
    
    if any(country in location for country in ['china', 'japan', 'korea']):
        return 'formal_relationship_focused'
    elif any(country in location for country in ['germany', 'netherlands', 'uk']):
        return 'process_oriented_direct'
    elif any(country in location for country in ['india', 'pakistan']):
        return 'relationship_collaborative'
    elif any(country in location for country in ['usa', 'canada']):
        return 'direct_efficient'
    else:
        return 'standard_professional'

def calculate_internal_deadline(extracted_params: Dict[str, Any]) -> str:
    """Calculate our internal deadline for decision"""
    
    logistics = extracted_params.get('logistics_details', {})
    urgency = extracted_params.get('urgency_level', 'medium')
    
    if urgency == 'urgent':
        deadline = datetime.now() + timedelta(days=3)
    elif urgency == 'high':
        deadline = datetime.now() + timedelta(days=7)
    elif logistics.get('timeline_days'):
        deadline = datetime.now() + timedelta(days=min(14, logistics['timeline_days'] // 2))
    else:
        deadline = datetime.now() + timedelta(days=14)
    
    return deadline.strftime('%Y-%m-%d')

def determine_message_priority(analysis: FollowUpAnalysis) -> str:
    """Determine message priority level"""
    
    if analysis.urgency_of_our_timeline == 'critical' or analysis.competitive_risk == 'high':
        return 'high'
    elif analysis.urgency_of_our_timeline == 'tight' or analysis.competitive_risk == 'medium':
        return 'medium'
    else:
        return 'low'

def calculate_expected_response_time(analysis: FollowUpAnalysis) -> str:
    """Calculate expected response timeframe"""
    
    if analysis.estimated_delay_duration in ['hours', '24_hours']:
        return '24_hours'
    elif 'day' in analysis.estimated_delay_duration:
        days = int(''.join(filter(str.isdigit, analysis.estimated_delay_duration)) or 3)
        if days <= 2:
            return '2_3_days'
        else:
            return 'week'
    elif 'week' in analysis.estimated_delay_duration:
        return 'week'
    else:
        return 'longer'

def validate_follow_up_schedule(
    analysis: FollowUpAnalysis, 
    schedule: FollowUpSchedule
) -> tuple[bool, List[str]]:
    """Validate the quality and effectiveness of the follow-up schedule"""
    
    issues = []
    
    # Check timeline alignment
    if analysis.urgency_of_our_timeline == 'critical' and len(schedule.follow_up_intervals) < 2:
        issues.append("Critical urgency requires more frequent follow-ups")
    
    # Check cultural appropriateness
    if analysis.estimated_delay_duration == 'weeks' and schedule.primary_follow_up_date:
        follow_up_date = datetime.fromisoformat(schedule.primary_follow_up_date)
        if follow_up_date < datetime.now() + timedelta(days=7):
            issues.append("Follow-up too soon for week-long delays")
    
    # Check confidence levels
    if schedule.confidence_in_schedule < 0.6:
        issues.append("Low confidence in schedule effectiveness")
    
    # Check completeness
    if not schedule.alternative_actions:
        issues.append("No alternative actions planned")
    
    if not schedule.value_reinforcement_points:
        issues.append("No value reinforcement strategy")
    
    is_valid = len(issues) == 0
    return is_valid, issues

def generate_contingency_plans(
    analysis: FollowUpAnalysis, 
    alternatives_count: int
) -> List[str]:
    """Generate contingency plans based on analysis"""
    
    contingencies = []
    
    if analysis.competitive_risk == 'high':
        contingencies.append("Accelerate outreach to alternative suppliers")
        contingencies.append("Consider offering improved terms to close quickly")
    
    if analysis.supplier_commitment_level == 'low':
        contingencies.append("Prepare to shift focus to backup suppliers")
        contingencies.append("Set firm deadline for supplier decision")
    
    if alternatives_count == 0:
        contingencies.append("Source additional supplier options immediately")
        contingencies.append("Consider adjusting specifications to expand supplier pool")
    
    if analysis.urgency_of_our_timeline == 'critical':
        contingencies.append("Escalate to direct phone/video communication")
        contingencies.append("Consider premium pricing for expedited service")
    
    return contingencies[:4]  # Return top 4 contingencies

# Utility functions for testing and monitoring
def test_follow_up_scenarios():
    """Test function to validate follow-up logic with various scenarios"""
    
    test_cases = [
        {
            "name": "High urgency, reliable supplier",
            "state": {
                "extracted_parameters": {"urgency_level": "urgent"},
                "top_suppliers": [{"reliability_score": 8.5, "location": "Germany"}],
                "supplier_response": "Need 3 days for management approval"
            },
            "expected_priority": "high"
        },
        {
            "name": "Low commitment, competitive risk",
            "state": {
                "extracted_parameters": {"urgency_level": "medium"},
                "top_suppliers": [{"reliability_score": 5.0, "location": "China"}],
                "supplier_response": "Will try to get back to you sometime"
            },
            "expected_next_step": "consider_alternative_suppliers"
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        # Test implementation would go here

def log_follow_up_metrics(state: AgentState, schedule: FollowUpSchedule) -> None:
    """Log metrics for follow-up effectiveness monitoring"""
    
    metrics = {
        "schedule_id": schedule.schedule_id,
        "delay_reason": state.get('follow_up_analysis', {}).get('delay_reason'),
        "cultural_region": determine_cultural_region(
            state.get('top_suppliers', [{}])[0].get('location', '')
        ),
        "urgency_level": state.get('follow_up_analysis', {}).get('urgency_of_our_timeline'),
        "competitive_risk": state.get('follow_up_analysis', {}).get('competitive_risk'),
        "schedule_confidence": schedule.confidence_in_schedule,
        "follow_up_method": schedule.follow_up_method,
        "timestamp": datetime.now().isoformat()
    }
    
    # In production, this would log to monitoring system
    print(f"Follow-up metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    # Run tests if module is executed directly
    test_follow_up_scenarios()