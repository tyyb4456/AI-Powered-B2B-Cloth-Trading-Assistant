from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from models.nagotiation_model import NegotiationStrategy, DraftedMessage
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()


def analyze_negotiation_history(state: AgentState):
    """
    Conduct thorough contextual analysis and historical review
    
    This is the core intelligence function that examines:
    1. The Original Goal: Initial user request that started negotiation
    2. The Conversation Thread: Complete record of all messages exchanged
    3. Supplier Profile: Company info, cultural origin, reliability scores
    4. User's Latest Instruction: Specific immediate goal or counter-offer
    """
    
    # Extract conversation history - using correct state field
    messages = state.get('messages', [])
    supplier_data = state.get('top_suppliers', [])
    extracted_params = state.get('extracted_parameters', {})
    
    # Analyze conversation patterns and negotiation context
    negotiation_rounds = 0
    last_supplier_response = None
    supplier_offers = []  # Track all supplier offers/responses
    negotiation_topic = "price"  # default
    conversation_tone = "collaborative"  # Track overall tone
    
    # Deep analysis of conversation thread
    if messages:
        for message in messages:
            # Handle the correct message format: list[dict] = [{'role': 'user', 'content': 'hey ...'}]
            if isinstance(message, dict):
                role = message.get('role', 'unknown')
                content = message.get('content', '')
            elif isinstance(message, str):
                content = message
                role = "user"  # default assumption
            else:
                continue
            
            content_str = str(content).lower()
            
            # Count negotiation rounds and analyze patterns
            if any(keyword in content_str for keyword in ["negotiate", "counter", "offer", "price", "terms", "discount", "adjust"]):
                negotiation_rounds += 1
            
            # Capture supplier responses and offers
            if role in ["supplier", "assistant"] and any(keyword in content_str for keyword in ["supplier", "offer", "quote", "price"]):
                last_supplier_response = str(content)
                supplier_offers.append(content_str)
            
            # Detect negotiation topics
            if any(keyword in content_str for keyword in ["delivery", "timeline", "lead time", "shipping"]):
                negotiation_topic = "delivery_terms"
            elif any(keyword in content_str for keyword in ["payment", "terms", "credit", "advance"]):
                negotiation_topic = "payment_terms"
            elif any(keyword in content_str for keyword in ["quantity", "moq", "minimum"]):
                negotiation_topic = "quantity_terms"
            
            # Assess conversation tone
            if any(keyword in content_str for keyword in ["urgent", "need", "must", "require"]):
                conversation_tone = "assertive"
            elif any(keyword in content_str for keyword in ["partnership", "relationship", "long-term"]):
                conversation_tone = "relationship-focused"
    
    # Extract the Original Goal (initial user request)
    original_goal = {}
    if isinstance(extracted_params, dict):
        original_goal = {
            "fabric_details": extracted_params.get('fabric_details', {}),
            "quantity": extracted_params.get('fabric_details', {}).get('quantity'),
            "urgency": extracted_params.get('urgency_level', 'medium'),
            "budget_constraints": extracted_params.get('price_constraints', {}),
            "delivery_requirements": extracted_params.get('logistics_details', {})
        }
    
    # Extract User's Latest Instruction (immediate tactical goal)
    latest_instruction = state.get('user_input', '')
    current_objective = state.get('negotiation_objective', latest_instruction)
    
    # Build comprehensive Supplier Profile for cultural context
    active_supplier = {}
    if supplier_data and len(supplier_data) > 0:
        supplier_info = supplier_data[0]
        active_supplier = {
            "name": supplier_info.get('name', 'Supplier'),
            "location": supplier_info.get('location', 'Unknown'),
            "country": supplier_info.get('country', 'Unknown'),
            "reliability_score": supplier_info.get('reliability_score', 5.0),
            "cultural_region": determine_cultural_region(supplier_info.get('location', '')),
            "past_negotiations": len(supplier_offers),
            "communication_style": assess_supplier_communication_style(supplier_offers)
        }
    
    # Extract urgency and timing context
    urgency_level = 'medium'
    if isinstance(extracted_params, dict):
        urgency_level = extracted_params.get('urgency_level', 'medium')
    
    return {
        "negotiation_rounds": negotiation_rounds,
        "last_supplier_response": last_supplier_response,
        "supplier_offers_history": supplier_offers,
        "negotiation_topic": negotiation_topic,
        "conversation_tone": conversation_tone,
        "original_goal": original_goal,  # The foundational request
        "current_objective": current_objective,  # Immediate tactical goal
        "latest_instruction": latest_instruction,  # User's specific instruction
        "active_supplier": active_supplier,  # Complete supplier profile
        "urgency_level": urgency_level
    }

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

def assess_supplier_communication_style(supplier_offers: List[str]) -> str:
    """Assess supplier's communication style from past messages"""
    if not supplier_offers:
        return 'standard'
    
    combined_text = ' '.join(supplier_offers).lower()
    
    if any(keyword in combined_text for keyword in ['relationship', 'partnership', 'honor', 'respect']):
        return 'relationship_focused'
    elif any(keyword in combined_text for keyword in ['data', 'market', 'analysis', 'benchmark']):
        return 'data_driven'
    elif any(keyword in combined_text for keyword in ['quick', 'fast', 'efficient', 'direct']):
        return 'direct_efficient'
    else:
        return 'standard'

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
    """Create prompt for strategic message composition with cultural tailoring"""
    
    system_prompt = """You are a veteran B2B textile negotiation specialist and strategic communications expert. You function as the "chief of staff" for negotiations, drafting messages that are tactically sound, strategically aligned, and culturally nuanced.

Your expertise encompasses:
- Global supply chain negotiation dynamics
- Cross-cultural business communication protocols  
- Relationship preservation while achieving tactical objectives
- Persuasive argumentation frameworks
- Professional tone calibration

**STRATEGIC MESSAGE COMPOSITION FRAMEWORK:**

**1. PERSUASIVE RATIONALE CONSTRUCTION:**
Build logical, compelling arguments using these frameworks:

- **Volume-Based Appeals**: "This order is part of our larger procurement strategy for the upcoming season, representing significant volume potential..."
- **Market Intelligence**: "Based on current market benchmarks and our industry analysis, the proposed adjustment reflects fair market rates..."
- **Partnership Value**: "We are seeking to establish a long-term strategic partnership and believe this pricing enables sustainable mutual growth..."
- **Reciprocal Benefits**: "In exchange for this price adjustment, we can offer accelerated payment terms and simplified logistics coordination..."
- **Timeline Optimization**: "Given our production schedule requirements, this arrangement allows for optimal planning and resource allocation..."

**2. CULTURAL COMMUNICATION ADAPTATION:**

- **East Asian Markets**: Indirect approach, relationship emphasis, face-saving language, patience with process
  - "We respectfully request your consideration of..." 
  - "We believe this arrangement honors both our business objectives..."

- **European Markets**: Process-oriented, quality-focused, formal but direct
  - "Our analysis indicates..." 
  - "We propose the following adjustment based on quality specifications..."

- **South Asian Markets**: Relationship-building, respectful hierarchy, collaborative tone
  - "We value our partnership and seek a solution that benefits both parties..."
  - "Given our mutual interest in long-term cooperation..."

- **Middle Eastern Markets**: Personal relationship emphasis, hospitality acknowledgment, patience
  - "We appreciate your hospitality and openness to discussion..."
  - "Building on our positive interactions..."

- **North American Markets**: Direct communication, efficiency-focused, data-driven
  - "Our market analysis shows..."
  - "To optimize efficiency for both organizations..."

**3. PROFESSIONAL TONE CALIBRATION:**

- **Collaborative**: "We're confident we can find a solution that works for both sides..."
- **Assertive**: "Based on our analysis and requirements, we need to adjust the terms to..."
- **Relationship-Focused**: "Given our commitment to building a strong partnership, we propose..."
- **Data-Driven**: "Market benchmarks and our procurement standards indicate..."

**4. STRUCTURAL REQUIREMENTS:**

1. **Professional Opening**: Contextual greeting acknowledging previous communication
2. **Strategic Context**: Brief rationale that justifies the request logically  
3. **Specific Request**: Unambiguous statement of desired terms with clear parameters
4. **Value Proposition**: What the supplier gains from accepting these terms
5. **Clear Call to Action**: Specific response requested with reasonable timeframe
6. **Relationship-Preserving Close**: Maintains long-term partnership potential

**5. COMMUNICATION PRINCIPLES:**
- Every sentence serves a strategic purpose
- Maintain dignity and respect for both parties
- Build logical argument progression
- Be concise but complete
- Include specific terms and numbers
- Avoid ultimatums while being clear about requirements
- Preserve business relationship for future opportunities

Generate a message that reads like it was written by an experienced international trade professional who understands both the technical requirements and the interpersonal dynamics of B2B negotiations."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Draft a strategic negotiation message using this context:

**NEGOTIATION CONTEXT:**
- Current Round: {negotiation_round}
- Negotiation Topic: {negotiation_topic}  
- Conversation Tone: {conversation_tone}
- Last Supplier Response: {last_supplier_response}

**SUPPLIER PROFILE:**
- Company: {supplier_name}
- Location: {supplier_location}
- Cultural Region: {cultural_region}
- Communication Style: {communication_style}
- Reliability Score: {supplier_reliability}

**STRATEGIC FRAMEWORK:**
- Primary Approach: {primary_approach}
- Key Arguments: {supporting_arguments}
- Recommended Tone: {tone_assessment}
- Cultural Considerations: {cultural_considerations}

**ORIGINAL GOAL (Foundation):**
{original_goal}

**CURRENT TACTICAL OBJECTIVE:**
{negotiation_objective}

**USER'S SPECIFIC INSTRUCTION:**
{latest_instruction}

**MESSAGE PARAMETERS:**
- Channel: {channel}
- Priority Level: {priority}  
- Max Length: 200 words
- Required: Clear call to action, specific terms, professional tone

Draft a complete message ready for transmission that implements the strategic approach while maintaining relationship integrity.""")
    ])

# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
strategy_model = model.with_structured_output(NegotiationStrategy)
message_model = model.with_structured_output(DraftedMessage)

strategy_prompt = create_strategy_prompt()
message_prompt = create_message_drafting_prompt()

def draft_negotiation_message(state: AgentState):
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
        supplier_name = supplier_data.get('name', 'Supplier')
        supplier_location = supplier_data.get('location', 'Unknown')
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
            "fabric_type": negotiation_context.get('original_goal', {}).get('fabric_details', {}).get('type', 'textile'),
            "quantity": negotiation_context.get('original_goal', {}).get('quantity', 'N/A'),
            "budget_info": negotiation_context.get('original_goal', {}).get('budget_constraints', {}),
            "last_response": negotiation_context.get('last_supplier_response', 'No previous response')
        })
        
        # Get strategic recommendation from LLM
        strategy: NegotiationStrategy = strategy_model.invoke(strategy_formatted_prompt)
        
        # Step 3: Draft the negotiation message with enhanced context
        message_formatted_prompt = message_prompt.invoke({
            "primary_approach": strategy.primary_approach,
            "supporting_arguments": ", ".join(strategy.supporting_arguments),
            "tone_assessment": strategy.tone_assessment,
            "cultural_considerations": strategy.cultural_considerations or "Standard business communication",
            "supplier_name": supplier_name,
            "supplier_location": supplier_location,
            "cultural_region": supplier_data.get('cultural_region', 'international'),
            "communication_style": supplier_data.get('communication_style', 'standard'),
            "supplier_reliability": supplier_reliability,
            "channel": state.get('channel', 'email'),
            "message_type": determine_message_type(current_objective),
            "priority": determine_priority(urgency_level, negotiation_context.get('negotiation_rounds', 0)),
            "negotiation_objective": str(current_objective),
            "latest_instruction": negotiation_context.get('latest_instruction', ''),
            "original_goal": str(negotiation_context.get('original_goal', {})),
            "conversation_tone": conversation_tone,
            "negotiation_topic": negotiation_context.get('negotiation_topic', 'general'),
            "negotiation_round": negotiation_context.get('negotiation_rounds', 0) + 1,
            "last_supplier_response": negotiation_context.get('last_supplier_response', 'Initial outreach')
        })
        
        # Get drafted message from LLM
        drafted_message: DraftedMessage = message_model.invoke(message_formatted_prompt)
        
        # Step 4: Generate unique message ID and set metadata
        message_id = f"msg_{str(uuid.uuid4())[:8]}"
        
        # Update the drafted message with generated ID and current timestamp
        drafted_message.message_id = message_id
        drafted_message.recipient = f"{supplier_name} <{supplier_data.get('contact_info', {}).get('email', 'supplier@email.com')}>"
        
        # Step 5: Create assistant response message that reflects strategic depth
        assistant_message = f"""📋 **Negotiation Message Drafted**

**Strategic Approach:** {strategy.primary_approach}
**Key Arguments:** {', '.join(strategy.supporting_arguments[:2])}
**Cultural Adaptation:** {supplier_data.get('cultural_region', 'Standard')} communication style
**Message Tone:** {strategy.tone_assessment}
**Confidence Score:** {drafted_message.confidence_score:.2f}/1.0

**Ready for transmission to:** {supplier_name} ({supplier_location})
**Message Type:** {drafted_message.message_type}
**Priority:** {drafted_message.priority_level}

The message maintains professional relationship standards while clearly presenting our tactical objectives."""

        # Step 6: Prepare state updates
        state_updates = {
            "drafted_message": drafted_message.model_dump(),
            "negotiation_strategy": strategy.model_dump(),
            "message_id": message_id,
            "message_ready": True,
            "next_step": "send_message_to_supplier",
            "messages1": [assistant_message],
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
            "messages1": [error_message],
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