from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

# Pydantic Models for structured output
class NegotiationStrategy(BaseModel):
    """Strategic framework for the negotiation approach"""
    primary_approach: str = Field(
        ..., 
        description="Main negotiation strategy (volume-based, market-rate, partnership, urgency, reciprocity)"
    )
    supporting_arguments: List[str] = Field(
        ..., 
        description="List of 2-3 key supporting arguments to justify the request"
    )
    tone_assessment: str = Field(
        ..., 
        description="Recommended tone (collaborative, assertive, relationship-focused, data-driven)"
    )
    cultural_considerations: Optional[str] = Field(
        None, 
        description="Cultural adjustments needed for this supplier's region"
    )
    risk_factors: List[str] = Field(
        default_factory=list, 
        description="Potential risks or sensitivities to avoid in messaging"
    )

class DraftedMessage(BaseModel):
    """Complete negotiation message with metadata"""
    message_id: str = Field(..., description="Unique identifier for this message")
    recipient: str = Field(..., description="Supplier contact information or identifier")
    subject_line: Optional[str] = Field(None, description="Email subject line if applicable")
    message_body: str = Field(..., description="Complete message text ready for transmission")
    message_type: str = Field(..., description="Type of negotiation message (counter_offer, terms_adjustment, clarification)")
    priority_level: str = Field(..., description="Message priority (high, medium, low)")
    expected_response_time: Optional[str] = Field(None, description="Expected supplier response timeframe")
    fallback_options: List[str] = Field(
        default_factory=list, 
        description="Alternative approaches if this message doesn't get desired response"
    )
    confidence_score: float = Field(
        ..., 
        description="Confidence in message effectiveness (0.0 to 1.0)", 
        ge=0.0, 
        le=1.0
    )

def analyze_negotiation_history(state: AgentState) -> Dict[str, Any]:
    """Analyze negotiation history to understand context and patterns"""
    
    # Extract conversation history
    messages = state.get('messages', [])
    supplier_data = state.get('top_suppliers', [])
    extracted_params = state.get('extracted_parameters', {})
    
    # Analyze conversation patterns
    negotiation_rounds = 0
    last_supplier_response = None
    negotiation_topic = "price"  # default
    
    for message in messages:
        if isinstance(message, tuple) and len(message) == 2:
            role, content = message
            if "negotiate" in content.lower() or "counter" in content.lower():
                negotiation_rounds += 1
            if role == "supplier":
                last_supplier_response = content
    
    # Extract original goal and current objectives
    original_request = extracted_params.get('fabric_details', {})
    current_objective = state.get('negotiation_objective', {})
    
    # Identify supplier profile for cultural context
    active_supplier = None
    if supplier_data:
        active_supplier = supplier_data[0]  # Assuming first supplier is active negotiation target
    
    return {
        "negotiation_rounds": negotiation_rounds,
        "last_supplier_response": last_supplier_response,
        "negotiation_topic": negotiation_topic,
        "original_request": original_request,
        "current_objective": current_objective,
        "active_supplier": active_supplier,
        "urgency_level": extracted_params.get('urgency_level', 'medium')
    }

def create_strategy_prompt():
    """Create prompt for negotiation strategy analysis"""
    
    system_prompt = """You are an expert B2B textile negotiation strategist with deep knowledge of global supply chain dynamics and cross-cultural business communication.

Your task is to analyze the current negotiation context and develop an optimal strategic approach for the message that will be drafted.

**STRATEGIC FRAMEWORKS:**

1. **Volume-Based Strategy**: Leverage order size and future business potential
   - Use when: Large quantities, repeat business potential, new supplier relationship
   - Arguments: Economies of scale, long-term partnership value, bulk pricing expectations

2. **Market-Rate Strategy**: Appeal to competitive market dynamics  
   - Use when: Price is above market average, multiple supplier options available
   - Arguments: Competitive benchmarking, market research data, industry standards

3. **Partnership Strategy**: Build long-term relationship value
   - Use when: Seeking ongoing supplier relationships, quality is critical
   - Arguments: Mutual growth, reliability premium, strategic partnership benefits

4. **Urgency Strategy**: Leverage time-sensitive requirements
   - Use when: Tight deadlines, seasonal demands, critical delivery dates
   - Arguments: Premium for speed, expedited processing, priority allocation

5. **Reciprocity Strategy**: Offer value exchange for concessions
   - Use when: Have flexibility in other terms (payment, timeline, specs)
   - Arguments: Faster payment, simplified logistics, specification flexibility

**CULTURAL CONSIDERATIONS:**
- **Asian Markets**: Relationship-first, face-saving, indirect communication
- **European Markets**: Process-oriented, quality-focused, formal communication  
- **Middle Eastern Markets**: Personal relationships, hospitality, patience with negotiation
- **Latin American Markets**: Relationship-building, personal touch, flexible terms
- **North American Markets**: Direct communication, efficiency-focused, data-driven

**TONE GUIDELINES:**
- **Collaborative**: "We're looking to find a solution that works for both sides..."
- **Assertive**: "Based on our market analysis, we need to adjust the terms to..."
- **Relationship-focused**: "Given our interest in building a long-term partnership..."
- **Data-driven**: "Market benchmarks indicate that the current price point..."

Analyze the context and recommend the optimal strategy, supporting arguments, and communication approach."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Analyze this negotiation context and recommend strategy:

**NEGOTIATION HISTORY:**
- Rounds completed: {negotiation_rounds}
- Current tone: {conversation_tone}
- Urgency level: {urgency_level}

**SUPPLIER PROFILE:**
- Company: {supplier_name}
- Location: {supplier_location}
- Reliability score: {supplier_reliability}

**CURRENT OBJECTIVE:**
{current_objective}

**ORIGINAL REQUEST:**
- Fabric: {fabric_type}
- Quantity: {quantity}
- Budget constraints: {budget_info}

**CONTEXT:**
Last supplier response: {last_response}

Provide strategic recommendation for optimal negotiation approach.""")
    ])


def create_message_drafting_prompt():
    """Create prompt for actual message composition"""
    
    system_prompt = """You are an expert B2B textile negotiation specialist and communications writer. Your expertise spans global supply chain negotiations, cross-cultural business communication, and relationship management.

Your task is to draft a professional, strategic, and persuasive negotiation message that implements the recommended strategy while maintaining business relationships.

**MESSAGE STRUCTURE:**
1. **Professional Opening**: Appropriate greeting and context acknowledgment
2. **Strategic Rationale**: Clear, logical justification for the request using recommended arguments
3. **Specific Request**: Unambiguous statement of desired terms or changes
4. **Value Proposition**: What the supplier gains from agreeing to these terms
5. **Clear Call to Action**: Specific response requested with reasonable timeframe
6. **Professional Closing**: Maintains relationship and opens door for discussion

**WRITING PRINCIPLES:**
- **Clarity**: Every sentence serves a purpose, no ambiguous language
- **Respect**: Professional tone that maintains dignity for both parties
- **Logic**: Arguments flow logically and build upon each other
- **Brevity**: Concise but complete - no unnecessary words
- **Cultural Sensitivity**: Adjusted for recipient's business culture
- **Relationship Preservation**: Even assertive messages maintain long-term relationship focus

**PERSUASION TECHNIQUES:**
- **Reciprocity**: Offer something valuable in return
- **Social Proof**: Reference industry standards or common practices
- **Scarcity**: Highlight time-sensitive nature if applicable
- **Authority**: Use data and market intelligence appropriately
- **Commitment**: Show serious business intent and professionalism

**AVOID:**
- Ultimatums or threats
- Excessive pressure or manipulation
- Cultural insensitivity or assumptions
- Vague or ambiguous language
- Personal attacks or relationship damage
- Unrealistic or impossible requests

Generate a message that is ready for immediate transmission and likely to achieve the desired outcome while preserving business relationships."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Draft a negotiation message using this strategy and context:

**STRATEGY TO IMPLEMENT:**
Primary Approach: {primary_approach}
Supporting Arguments: {supporting_arguments}
Recommended Tone: {tone_assessment}
Cultural Considerations: {cultural_considerations}

**MESSAGE DETAILS:**
Recipient: {supplier_name} ({supplier_location})
Communication Channel: {channel}
Message Type: {message_type}
Priority: {priority}

**SPECIFIC REQUEST:**
{negotiation_objective}

**CONTEXT:**
Current conversation tone: {conversation_tone}
Negotiation round: {negotiation_round}
Original fabric request: {original_request}
Last response from supplier: {last_supplier_response}

**CONSTRAINTS:**
- Keep message under 200 words
- Include clear call to action
- Maintain professional business tone
- Be specific about terms requested

Draft the complete message ready for transmission.""")
    ])

# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
strategy_model = model.with_structured_output(NegotiationStrategy)
message_model = model.with_structured_output(DraftedMessage)

strategy_prompt = create_strategy_prompt()
message_prompt = create_message_drafting_prompt()

def draft_negotiation_message(state: AgentState) -> dict:
    """
    Node 4b: draft_negotiation_message - Strategic message composition engine
    
    Purpose:
    - Analyze complete negotiation context and history
    - Develop optimal strategic approach for current situation
    - Draft culturally-aware, persuasive negotiation message
    - Prepare message for transmission to supplier
    - Maintain relationship while achieving tactical objectives
    
    Args:
        state: Current agent state with negotiation context and history
    
    Returns:
        dict: State updates with drafted message and strategic analysis
    """
    
    try:
        # Step 1: Analyze negotiation context and history
        negotiation_context = analyze_negotiation_history(state)
        
        # Extract key context elements
        supplier_data = negotiation_context.get('active_supplier', {})
        supplier_name = supplier_data.get('company_name', 'Supplier')
        supplier_location = supplier_data.get('country', 'Unknown')
        supplier_reliability = supplier_data.get('reliability_score', 5.0)
        
        current_objective = negotiation_context.get('current_objective', {})
        urgency_level = negotiation_context.get('urgency_level', 'medium')
        conversation_tone = negotiation_context.get('conversation_tone', 'collaborative')
        
        # Step 2: Develop negotiation strategy
        strategy_formatted_prompt = strategy_prompt.invoke({
            "negotiation_rounds": negotiation_context.get('negotiation_rounds', 0),
            "conversation_tone": conversation_tone,
            "urgency_level": urgency_level,
            "supplier_name": supplier_name,
            "supplier_location": supplier_location,
            "supplier_reliability": supplier_reliability,
            "current_objective": str(current_objective),
            "fabric_type": negotiation_context.get('original_request', {}).get('type', 'textile'),
            "quantity": negotiation_context.get('original_request', {}).get('quantity', 'N/A'),
            "budget_info": state.get('extracted_parameters', {}).get('price_constraints', {}),
            "last_response": negotiation_context.get('last_supplier_response', 'No previous response')
        })
        
        # Get strategic recommendation from LLM
        strategy: NegotiationStrategy = strategy_model.invoke(strategy_formatted_prompt)
        
        # Step 3: Draft the negotiation message
        message_formatted_prompt = message_prompt.invoke({
            "primary_approach": strategy.primary_approach,
            "supporting_arguments": ", ".join(strategy.supporting_arguments),
            "tone_assessment": strategy.tone_assessment,
            "cultural_considerations": strategy.cultural_considerations or "Standard business communication",
            "supplier_name": supplier_name,
            "supplier_location": supplier_location,
            "channel": state.get('channel', 'email'),
            "message_type": determine_message_type(current_objective),
            "priority": determine_priority(urgency_level, negotiation_context.get('negotiation_rounds', 0)),
            "negotiation_objective": str(current_objective),
            "conversation_tone": conversation_tone,
            "negotiation_round": negotiation_context.get('negotiation_rounds', 0) + 1,
            "original_request": str(negotiation_context.get('original_request', {})),
            "last_supplier_response": negotiation_context.get('last_supplier_response', 'Initial outreach')
        })
        
        # Get drafted message from LLM
        drafted_message: DraftedMessage = message_model.invoke(message_formatted_prompt)

        draft_message = drafted_message.message_body
        
        # Step 4: Generate unique message ID and set metadata
        message_id = f"msg_{str(uuid.uuid4())[:8]}"
        
        # Update the drafted message with generated ID and current timestamp
        drafted_message.message_id = message_id
        drafted_message.recipient = f"{supplier_name} <{supplier_data.get('contact_info', {}).get('email', 'tybhsn001@gamil.com')}>"
        
        # Step 5: Create assistant response message
        assistant_message = f"""Drafted negotiation message using {strategy.primary_approach} strategy.
        
Key arguments: {', '.join(strategy.supporting_arguments[:2])}
Message tone: {strategy.tone_assessment}
Confidence score: {drafted_message.confidence_score:.2f}

Message ready for transmission to {supplier_name}."""

        # Step 6: Prepare state updates
        state_updates = {
            "drafted_message": drafted_message.model_dump(),
            'draft_message' : draft_message,
            "negotiation_strategy": strategy.model_dump(),
            "message_id": message_id,
            "message_ready": True,
            "next_step": "send_message_to_supplier",
            "messages": [("assistant", assistant_message)],
            "status": "message_drafted",
            "last_message_confidence": drafted_message.confidence_score
        }
        
        # Add fallback planning if confidence is low
        if drafted_message.confidence_score < 0.7:
            state_updates["requires_review"] = True
            state_updates["fallback_options"] = drafted_message.fallback_options
            state_updates["next_step"] = "review_message_before_send"
        
        return state_updates
        
    except Exception as e:
        error_message = f"Error in drafting negotiation message: {str(e)}"
        return {
            "error": str(e),
            "messages": [("assistant", error_message)],
            "next_step": "handle_error",
            "status": "error"
        }
    
def determine_message_type(objective: Dict[str, Any]) -> str:
    """Determine the type of negotiation message based on objective"""
    
    if not objective:
        return "initial_outreach"
    
    objective_str = str(objective).lower()
    
    if "price" in objective_str or "cost" in objective_str:
        return "price_negotiation"
    elif "delivery" in objective_str or "timeline" in objective_str or "lead" in objective_str:
        return "timeline_adjustment"
    elif "payment" in objective_str or "terms" in objective_str:
        return "terms_negotiation"
    elif "quantity" in objective_str or "moq" in objective_str:
        return "quantity_adjustment"
    elif "specification" in objective_str or "quality" in objective_str:
        return "spec_clarification"
    else:
        return "general_negotiation"

def determine_priority(urgency_level: str, negotiation_round: int) -> str:
    """Determine message priority based on urgency and negotiation stage"""
    
    if urgency_level == "urgent" or negotiation_round >= 3:
        return "high"
    elif urgency_level == "high" or negotiation_round >= 2:
        return "medium"
    else:
        return "normal"

def validate_message_quality(drafted_message: DraftedMessage) -> tuple[bool, List[str]]:
    """Validate the quality and completeness of drafted message"""
    
    issues = []
    
    # Check message length (should be professional but not too long)
    if len(drafted_message.message_body) < 50:
        issues.append("Message too short - may lack necessary detail")
    elif len(drafted_message.message_body) > 1000:
        issues.append("Message too long - may lose recipient's attention")
    
    # Check for clear call to action
    cta_keywords = ["please", "kindly", "could you", "would you", "let us know", "confirm", "respond"]
    if not any(keyword in drafted_message.message_body.lower() for keyword in cta_keywords):
        issues.append("Message lacks clear call to action")
    
    # Check for specific terms or numbers
    if "TBD" in drafted_message.message_body or "XXX" in drafted_message.message_body:
        issues.append("Message contains placeholder text")
    
    # Check confidence score
    if drafted_message.confidence_score < 0.5:
        issues.append("Low confidence score - message may need human review")
    
    is_valid = len(issues) == 0
    return is_valid, issues

def generate_message_alternatives(strategy: NegotiationStrategy, context: Dict[str, Any]) -> List[str]:
    """Generate alternative message approaches if primary message fails"""
    
    alternatives = []
    
    # Alternative 1: More collaborative approach
    if strategy.tone_assessment != "collaborative":
        alternatives.append("Try more collaborative, partnership-focused approach")
    
    # Alternative 2: Data-driven approach
    if "market-rate" not in strategy.primary_approach:
        alternatives.append("Present market data and competitive analysis")
    
    # Alternative 3: Direct human-to-human contact
    alternatives.append("Escalate to direct phone call or video meeting")
    
    # Alternative 4: Adjust terms creatively
    alternatives.append("Offer alternative value propositions (payment terms, volume commitments)")
    
    return alternatives[:3]  # Return top 3 alternatives