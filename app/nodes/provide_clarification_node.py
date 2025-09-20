from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

# Pydantic Models for Structured Output
class ClarificationAnalysis(BaseModel):
    """Analysis of supplier's clarification request"""
    clarification_type: str = Field(description="Type of clarification needed (specs, quantity, timeline, payment, logistics, quality)")
    specific_questions: List[str] = Field(description="Specific questions the supplier asked")
    missing_information: List[str] = Field(description="Information gaps identified")
    urgency_level: str = Field(description="How urgent the clarification is (low, medium, high)")
    complexity_score: float = Field(description="How complex the clarification is (0.0 to 1.0)", ge=0.0, le=1.0)
    supplier_engagement_level: str = Field(description="Level of supplier interest (high, medium, low)")
    potential_deal_impact: str = Field(description="How clarification might impact the deal")

class ClarificationResponse(BaseModel):
    """Structured response providing clarification to supplier"""
    response_id: str = Field(description="Unique ID for this clarification response")
    response_type: str = Field(description="Type of response (direct_answer, detailed_explanation, conditional_answer)")
    main_response: str = Field(description="Primary clarification response body")
    specific_answers: Dict[str, str] = Field(description="Specific answers to individual questions")
    additional_context: Optional[str] = Field(None, description="Additional context or background information")
    technical_specifications: Optional[Dict[str, Any]] = Field(None, description="Technical specs if requested")
    next_steps: List[str] = Field(description="What happens after this clarification")
    followup_questions: Optional[List[str]] = Field(None, description="Questions to ask supplier back if needed")
    confidence_score: float = Field(description="Confidence in provided clarification (0.0 to 1.0)", ge=0.0, le=1.0)
    requires_additional_input: bool = Field(False, description="Whether we need more info from user/internal team")

def create_clarification_analysis_prompt():
    """Create prompt for analyzing supplier clarification requests"""
    
    system_prompt = """You are an expert B2B textile communication analyst specializing in supplier clarification requests. Your expertise includes technical fabric specifications, commercial terms, logistics coordination, and quality standards.

Your task is to analyze supplier requests for clarification and categorize them for optimal response generation.

**CLARIFICATION TYPES:**

1. **Technical Specifications (specs):**
   - Fabric composition, GSM, weave type
   - Color specifications, dye methods
   - Finishing processes, treatments
   - Quality standards, testing requirements

2. **Quantity & Volume (quantity):**
   - Order quantities, MOQ clarification
   - Volume breakdowns, sizing
   - Packaging requirements

3. **Timeline & Delivery (timeline):**
   - Delivery dates, lead times
   - Production schedules
   - Shipping methods, deadlines

4. **Payment & Commercial (payment):**
   - Payment terms, currencies
   - Credit arrangements
   - Pricing structure clarification

5. **Logistics & Shipping (logistics):**
   - Incoterms, shipping points
   - Documentation requirements
   - Customs, duties, regulations

6. **Quality & Compliance (quality):**
   - Certifications needed
   - Quality control processes
   - Testing requirements, standards

**ENGAGEMENT ASSESSMENT:**
- **High**: Multiple detailed questions, technical focus, timeline urgency
- **Medium**: Specific but limited questions, moderate detail
- **Low**: Basic questions, minimal engagement

**COMPLEXITY SCORING:**
- **High (0.8-1.0)**: Multiple technical specs, custom requirements
- **Medium (0.5-0.8)**: Standard commercial terms, moderate complexity
- **Low (0.0-0.5)**: Basic information, standard industry practices

**URGENCY INDICATORS:**
- Deadline mentions, time pressure language
- Production schedule references
- Immediate decision requirements"""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Analyze this supplier clarification request:

**SUPPLIER'S MESSAGE:**
{supplier_message}

**NEGOTIATION CONTEXT:**
- Current round: {negotiation_round}
- Supplier: {supplier_name} ({supplier_location})
- Original request: {original_request_summary}

**PREVIOUS COMMUNICATION:**
- Last message type: {last_message_type}
- Previous terms discussed: {previous_terms}

Analyze the clarification request and categorize it for optimal response generation.""")
    ])

def create_clarification_response_prompt():
    """Create prompt for generating clarification responses"""
    
    system_prompt = """You are a senior B2B textile procurement specialist with deep expertise in fabric specifications, commercial terms, and international trade logistics. You function as the primary point of contact for supplier communications, providing clear, accurate, and professional clarifications.

Your expertise encompasses:
- Technical fabric specifications and industry standards
- Commercial terms and payment structures
- International logistics and compliance requirements
- Quality control and certification processes
- Cross-cultural business communication

**RESPONSE GENERATION FRAMEWORK:**

**1. DIRECT TECHNICAL RESPONSES:**
For specifications, quantities, and technical requirements:
- Provide exact numbers, measurements, and standards
- Reference industry specifications (ASTM, ISO, etc.)
- Include tolerance ranges where applicable
- Clarify testing methods and quality benchmarks

**2. COMMERCIAL CLARIFICATIONS:**
For pricing, payment, and terms:
- Be specific about currency, payment schedules
- Clarify incoterms and responsibilities
- Explain any conditional pricing
- Detail penalty/incentive structures

**3. TIMELINE COMMUNICATIONS:**
For delivery and production schedules:
- Provide specific dates and milestones
- Explain critical path dependencies
- Clarify flexibility and buffer periods
- Detail expedite options if available

**4. LOGISTICS COORDINATION:**
For shipping and documentation:
- Specify exact documentation requirements
- Clarify customs and regulatory compliance
- Detail packaging and labeling requirements
- Explain tracking and communication protocols

**5. QUALITY ASSURANCE:**
For quality and compliance matters:
- Detail inspection processes and timing
- Specify acceptance criteria and testing
- Explain certification requirements
- Clarify remediation processes for non-conformance

**COMMUNICATION PRINCIPLES:**
- Be precise and unambiguous
- Provide context for complex requirements
- Include relevant background information
- Anticipate follow-up questions
- Maintain professional, collaborative tone
- Use industry-standard terminology
- Include specific examples where helpful

**CULTURAL CONSIDERATIONS:**
Adapt communication style based on supplier location:
- **Asian suppliers**: Detailed, respectful, relationship-focused
- **European suppliers**: Process-oriented, quality-focused, formal
- **Middle Eastern suppliers**: Personal relationship emphasis
- **Latin American suppliers**: Warm, relationship-building approach

**RESPONSE STRUCTURE:**
1. **Acknowledgment**: Confirm understanding of their questions
2. **Direct Answers**: Provide specific responses to each question
3. **Context**: Explain reasoning or background where relevant
4. **Next Steps**: Clear guidance on what happens next
5. **Open Door**: Encourage further questions if needed

Generate responses that eliminate ambiguity and move the negotiation forward efficiently."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Generate a comprehensive clarification response:

**CLARIFICATION ANALYSIS:**
- Type: {clarification_type}
- Questions: {specific_questions}
- Missing info: {missing_information}
- Complexity: {complexity_score}
- Supplier engagement: {supplier_engagement_level}

**SUPPLIER PROFILE:**
- Company: {supplier_name}
- Location: {supplier_location}
- Cultural region: {cultural_region}
- Previous relationship: {relationship_history}

**ORIGINAL REQUEST CONTEXT:**
- Fabric details: {fabric_details}
- Quantity: {requested_quantity}
- Timeline: {delivery_requirements}
- Budget: {budget_constraints}
- Special requirements: {special_requirements}

**AVAILABLE INFORMATION TO SHARE:**
- Technical specs: {available_tech_specs}
- Commercial terms: {available_commercial_terms}
- Timeline details: {available_timeline_info}
- Quality requirements: {available_quality_specs}

**COMMUNICATION PARAMETERS:**
- Urgency level: {urgency_level}
- Response tone: Professional and collaborative
- Max length: 300 words
- Required: Clear answers, next steps, open invitation for more questions

Generate a complete clarification response that addresses all supplier questions while maintaining momentum toward deal closure.""")
    ])

# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
analysis_model = model.with_structured_output(ClarificationAnalysis)
response_model = model.with_structured_output(ClarificationResponse)

analysis_prompt = create_clarification_analysis_prompt()
response_prompt = create_clarification_response_prompt()

def extract_clarification_context(state: AgentState) -> Dict[str, Any]:
    """Extract relevant context for clarification from current state"""
    
    # Get negotiation context
    messages = state.get('messages1', []) + state.get('msgs', [])
    negotiation_round = len([msg for msg in messages if 'negotiate' in str(msg).lower()]) + 1
    
    # Extract original request
    extracted_params = state.get('extracted_parameters', {})
    fabric_details = extracted_params.get('fabric_details', {})
    
    # Get supplier information
    supplier_data = {}
    top_suppliers = state.get('top_suppliers', [])
    if top_suppliers:
        supplier_data = top_suppliers[0]
    
    # Get previous communication context
    drafted_message = state.get('drafted_message', {})
    last_message_type = drafted_message.get('message_type', 'initial')
    
    return {
        'negotiation_round': negotiation_round,
        'fabric_details': fabric_details,
        'supplier_data': supplier_data,
        'last_message_type': last_message_type,
        'original_params': extracted_params
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

def prepare_available_information(state: AgentState) -> Dict[str, Any]:
    """Prepare available information that can be shared in clarification"""
    
    extracted_params = state.get('extracted_parameters', {})
    
    return {
        'tech_specs': {
            'fabric_type': extracted_params.get('fabric_details', {}).get('type'),
            'quality_specs': extracted_params.get('fabric_details', {}).get('quality_specs', []),
            'composition': extracted_params.get('fabric_details', {}).get('composition'),
            'certifications': extracted_params.get('fabric_details', {}).get('certifications', [])
        },
        'commercial_terms': {
            'quantity': extracted_params.get('fabric_details', {}).get('quantity'),
            'unit': extracted_params.get('fabric_details', {}).get('unit'),
            'budget': extracted_params.get('price_constraints', {}).get('max_price'),
            'currency': extracted_params.get('price_constraints', {}).get('currency')
        },
        'timeline_info': {
            'delivery_timeline': extracted_params.get('logistics_details', {}).get('timeline'),
            'destination': extracted_params.get('logistics_details', {}).get('destination'),
            'urgency': extracted_params.get('urgency_level', 'medium')
        },
        'quality_specs': {
            'certifications': extracted_params.get('fabric_details', {}).get('certifications', []),
            'quality_requirements': extracted_params.get('fabric_details', {}).get('quality_specs', [])
        }
    }

def provide_clarification(state: AgentState) -> dict:
    """
    Node: provide_clarification - Supplier clarification request handler
    
    Purpose:
    - Analyze supplier's clarification requests and categorize them
    - Generate comprehensive, accurate clarification responses
    - Maintain negotiation momentum while providing needed information
    - Handle complex technical, commercial, and logistical questions
    - Preserve relationship while moving toward deal closure
    
    Args:
        state: Current agent state containing supplier's clarification request
    
    Returns:
        dict: State updates with clarification analysis and response
    """
    
    try:
        # Step 1: Extract supplier message and context
        supplier_message = state.get('supplier_response') or state.get('human_response')
        
        if not supplier_message:
            return {
                "error": "No supplier clarification request found",
                "messages1": ["No clarification request to process"],
                "status": "no_clarification_request"
            }
        
        context = extract_clarification_context(state)
        supplier_info = context['supplier_data']
        
        # Step 2: Analyze the clarification request
        analysis_formatted_prompt = analysis_prompt.invoke({
            "supplier_message": supplier_message,
            "negotiation_round": context['negotiation_round'],
            "supplier_name": supplier_info.get('name', 'Supplier'),
            "supplier_location": supplier_info.get('location', 'Unknown'),
            "original_request_summary": create_request_summary(context['original_params']),
            "last_message_type": context['last_message_type'],
            "previous_terms": state.get('extracted_terms', {})
        })
        
        clarification_analysis: ClarificationAnalysis = analysis_model.invoke(analysis_formatted_prompt)
        
        # Step 3: Prepare available information for response
        available_info = prepare_available_information(state)
        
        # Step 4: Generate clarification response
        response_formatted_prompt = response_prompt.invoke({
            "clarification_type": clarification_analysis.clarification_type,
            "specific_questions": clarification_analysis.specific_questions,
            "missing_information": clarification_analysis.missing_information,
            "complexity_score": clarification_analysis.complexity_score,
            "supplier_engagement_level": clarification_analysis.supplier_engagement_level,
            "supplier_name": supplier_info.get('name', 'Supplier'),
            "supplier_location": supplier_info.get('location', 'Unknown'),
            "cultural_region": determine_cultural_region(supplier_info.get('location', '')),
            "relationship_history": supplier_info.get('notes', 'New supplier'),
            "fabric_details": available_info['tech_specs'],
            "requested_quantity": available_info['commercial_terms']['quantity'],
            "delivery_requirements": available_info['timeline_info'],
            "budget_constraints": available_info['commercial_terms']['budget'],
            "special_requirements": context['original_params'].get('additional_notes', 'None'),
            "available_tech_specs": available_info['tech_specs'],
            "available_commercial_terms": available_info['commercial_terms'],
            "available_timeline_info": available_info['timeline_info'],
            "available_quality_specs": available_info['quality_specs'],
            "urgency_level": clarification_analysis.urgency_level
        })
        
        clarification_response: ClarificationResponse = response_model.invoke(response_formatted_prompt)
        
        # Step 5: Generate response ID and set metadata
        response_id = f"clarif_{str(uuid.uuid4())[:8]}"
        clarification_response.response_id = response_id
        
        # Step 6: Determine next step based on response requirements
        if clarification_response.requires_additional_input:
            next_step = "request_additional_information"
        elif clarification_response.followup_questions:
            next_step = "await_supplier_response"
        else:
            next_step = "share_clarification_response"
        
        # Step 7: Create assistant response message
        assistant_message = f"""📋 **Clarification Response Prepared**

**Clarification Type:** {clarification_analysis.clarification_type.title()}
**Questions Addressed:** {len(clarification_analysis.specific_questions)}
**Complexity Level:** {clarification_analysis.complexity_score:.2f}/1.0
**Supplier Engagement:** {clarification_analysis.supplier_engagement_level.title()}

**Response Overview:**
- Response type: {clarification_response.response_type}
- Specific answers provided: {len(clarification_response.specific_answers)}
- Additional context included: {'Yes' if clarification_response.additional_context else 'No'}
- Follow-up questions: {len(clarification_response.followup_questions or [])}

**Confidence Score:** {clarification_response.confidence_score:.2f}/1.0
**Ready for transmission to:** {supplier_info.get('name', 'Supplier')}"""

        # Step 8: Update negotiation history
        clarification_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "clarification_request",
            "supplier_questions": clarification_analysis.specific_questions,
            "clarification_type": clarification_analysis.clarification_type,
            "our_response": clarification_response.main_response[:100] + "...",  # Truncated for history
            "confidence": clarification_response.confidence_score
        }
        
        updated_history = state.get('negotiation_history', []) + [clarification_entry]
        
        # Step 9: Prepare comprehensive state updates
        state_updates = {
            "clarification_analysis": clarification_analysis.model_dump(),
            "clarification_response": clarification_response.model_dump(),
            "response_id": response_id,
            "clarification_ready": True,
            "next_step": next_step,
            "messages1": [assistant_message],
            "status": "clarification_prepared",
            "last_clarification_confidence": clarification_response.confidence_score,
            "negotiation_history": updated_history,
            "supplier_engagement_level": clarification_analysis.supplier_engagement_level
        }
        
        # Add additional handling flags
        if clarification_response.requires_additional_input:
            state_updates["needs_internal_info"] = True
            state_updates["missing_info_list"] = clarification_analysis.missing_information
        
        if clarification_response.confidence_score < 0.7:
            state_updates["requires_review"] = True
            state_updates["low_confidence_areas"] = identify_low_confidence_areas(clarification_analysis, clarification_response)
        
        return state_updates
        
    except Exception as e:
        error_message = f"Error in providing clarification: {str(e)}"
        return {
            "error": str(e),
            "messages1": [error_message],
            "next_step": "handle_error",
            "status": "clarification_error"
        }

def create_request_summary(extracted_params: Dict[str, Any]) -> str:
    """Create a brief summary of the original request for context"""
    
    fabric_details = extracted_params.get('fabric_details', {})
    logistics = extracted_params.get('logistics_details', {})
    
    summary_parts = []
    
    if fabric_details.get('type'):
        summary_parts.append(f"{fabric_details['type']}")
    
    if fabric_details.get('quantity'):
        unit = fabric_details.get('unit', 'units')
        summary_parts.append(f"{fabric_details['quantity']} {unit}")
    
    if logistics.get('destination'):
        summary_parts.append(f"to {logistics['destination']}")
    
    if logistics.get('timeline'):
        summary_parts.append(f"by {logistics['timeline']}")
    
    return " ".join(summary_parts) if summary_parts else "Standard textile order"

def identify_low_confidence_areas(analysis: ClarificationAnalysis, response: ClarificationResponse) -> List[str]:
    """Identify areas where confidence is low and may need human review"""
    
    low_confidence_areas = []
    
    if analysis.complexity_score > 0.8:
        low_confidence_areas.append("High complexity clarification")
    
    if len(analysis.missing_information) >= 3:
        low_confidence_areas.append("Multiple information gaps")
    
    if response.requires_additional_input:
        low_confidence_areas.append("Requires additional internal information")
    
    if len(response.specific_answers) < len(analysis.specific_questions):
        low_confidence_areas.append("Incomplete answers to all questions")
    
    return low_confidence_areas

def validate_clarification_quality(analysis: ClarificationAnalysis, response: ClarificationResponse) -> tuple[bool, List[str]]:
    """Validate the quality and completeness of the clarification"""
    
    issues = []
    
    # Check if all questions were addressed
    if len(response.specific_answers) < len(analysis.specific_questions):
        issues.append("Not all supplier questions were addressed")
    
    # Check response length (should be comprehensive but not overwhelming)
    if len(response.main_response) < 50:
        issues.append("Response too brief - may lack necessary detail")
    elif len(response.main_response) > 2000:
        issues.append("Response too lengthy - may overwhelm supplier")
    
    # Check confidence level
    if response.confidence_score < 0.6:
        issues.append("Low confidence in response accuracy")
    
    # Check for clear next steps
    if not response.next_steps:
        issues.append("No clear next steps provided")
    
    is_valid = len(issues) == 0
    return is_valid, issues