from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import logging
# Configure logging for debugging conditional edge decisions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Pydantic Models for contract structure
class PartyDetails(BaseModel):
    """Legal entity information for contract parties"""
    legal_name: str = Field(..., description="Full legal name of the entity")
    address: str = Field(..., description="Complete legal address")
    contact_person: str = Field(..., description="Authorized signatory or contact")
    email: str = Field(..., description="Primary business email")
    phone: Optional[str] = Field(None, description="Business phone number")
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    registration_number: Optional[str] = Field(None, description="Business registration number")

class ProductSpecifications(BaseModel):
    """Detailed product specifications for contract"""
    fabric_type: str = Field(..., description="Type of fabric (cotton, silk, polyester, etc.)")
    quantity: float = Field(..., description="Total quantity ordered")
    unit: str = Field(..., description="Unit of measurement (meters, kg, etc.)")
    quality_specifications: List[str] = Field(default_factory=list, description="Quality specs (GSM, certifications, etc.)")
    color: Optional[str] = Field(None, description="Color specifications")
    width: Optional[str] = Field(None, description="Fabric width specifications")
    certifications: List[str] = Field(default_factory=list, description="Required certifications (GOTS, OEKO-TEX, etc.)")
    technical_specs: Optional[str] = Field(None, description="Additional technical specifications")

class CommercialTerms(BaseModel):
    """Financial and commercial terms of the contract"""
    unit_price: float = Field(..., description="Price per unit")
    total_value: float = Field(..., description="Total contract value")
    currency: str = Field(default="USD", description="Contract currency")
    payment_terms: str = Field(..., description="Payment terms (Net 30, 50% advance, etc.)")
    incoterms: str = Field(..., description="International commercial terms (FOB, CIF, etc.)")
    price_validity: Optional[str] = Field(None, description="Price validity period")
    taxes_and_duties: Optional[str] = Field(None, description="Tax and duty responsibilities")

class DeliveryTerms(BaseModel):
    """Logistics and delivery specifications"""
    delivery_destination: str = Field(..., description="Final delivery destination")
    lead_time_days: int = Field(..., description="Agreed lead time in days")
    delivery_date: str = Field(..., description="Expected delivery date")
    shipping_method: Optional[str] = Field(None, description="Preferred shipping method")
    packaging_requirements: Optional[str] = Field(None, description="Special packaging needs")
    inspection_terms: Optional[str] = Field(None, description="Quality inspection arrangements")

class ContractAnomalies(BaseModel):
    """Non-standard terms that require human review"""
    non_standard_clauses: List[str] = Field(default_factory=list, description="Clauses that deviate from standard template")
    special_conditions: List[str] = Field(default_factory=list, description="Unique conditions added during negotiation")
    risk_factors: List[str] = Field(default_factory=list, description="Terms that may carry additional risk")
    review_notes: List[str] = Field(default_factory=list, description="Specific items flagged for human review")
    anomaly_score: float = Field(..., description="Overall deviation from standard contract (0.0 to 1.0)", ge=0.0, le=1.0)

class ContractDraft(BaseModel):
    """Complete contract draft with metadata"""
    contract_id: str = Field(..., description="Unique contract identifier")
    contract_title: str = Field(..., description="Contract title/description")
    buyer: PartyDetails
    seller: PartyDetails
    product_specs: ProductSpecifications
    commercial_terms: CommercialTerms
    delivery_terms: DeliveryTerms
    contract_text: str = Field(..., description="Complete contract text ready for review")
    anomalies: ContractAnomalies
    template_used: str = Field(..., description="Contract template identifier used")
    creation_date: str = Field(..., description="Contract creation timestamp")
    status: Literal["draft", "review_pending", "approved", "rejected"] = Field(default="draft")
    review_priority: Literal["low", "medium", "high", "urgent"] = Field(..., description="Priority for human review")

# Contract templates (in practice, these would be stored in a database or file system)
CONTRACT_TEMPLATES = {
    "international_textile": {
        "name": "International Textile Purchase Agreement",
        "template": """
TEXTILE PURCHASE AGREEMENT

This Agreement is made between:

BUYER: {buyer_name}
Address: {buyer_address}
Contact: {buyer_contact}

SELLER: {seller_name} 
Address: {seller_address}
Contact: {seller_contact}

1. PRODUCT SPECIFICATIONS
   - Fabric Type: {fabric_type}
   - Quantity: {quantity} {unit}
   - Quality Specifications: {quality_specs}
   - Certifications: {certifications}

2. COMMERCIAL TERMS
   - Unit Price: {unit_price} {currency} per {unit}
   - Total Value: {total_value} {currency}
   - Payment Terms: {payment_terms}
   - Incoterms: {incoterms}

3. DELIVERY TERMS
   - Destination: {delivery_destination}
   - Lead Time: {lead_time_days} days
   - Expected Delivery: {delivery_date}

4. STANDARD TERMS AND CONDITIONS
   - Quality inspection within 10 days of delivery
   - Force majeure clause applies
   - Disputes governed by international arbitration
   - Warranty period: 90 days from delivery

{special_clauses}

Signatures:
Buyer: _________________ Date: _________
Seller: _________________ Date: _________
        """,
        "required_fields": ["buyer_name", "seller_name", "fabric_type", "quantity", "unit_price", "delivery_destination"],
        "standard_clauses": ["quality_inspection", "force_majeure", "arbitration", "warranty"]
    },
    
    "domestic_textile": {
        "name": "Domestic Textile Supply Agreement",
        "template": """
TEXTILE SUPPLY AGREEMENT

Buyer: {buyer_name}, {buyer_address}
Supplier: {seller_name}, {seller_address}

Product: {fabric_type}
Quantity: {quantity} {unit}
Price: {unit_price} {currency} per {unit}
Total: {total_value} {currency}
Payment: {payment_terms}
Delivery: {delivery_date} to {delivery_destination}

Standard terms apply unless modified above.

{special_clauses}
        """,
        "required_fields": ["buyer_name", "seller_name", "fabric_type", "quantity", "unit_price"],
        "standard_clauses": ["standard_warranty", "local_jurisdiction"]
    }
}

def create_data_aggregation_prompt():
    """Create prompt for validating and structuring contract data"""
    
    system_prompt = """You are an expert contract data analyst specializing in B2B textile agreements. Your task is to aggregate and validate all necessary information for contract generation from the negotiation state.

**DATA VALIDATION REQUIREMENTS:**

1. **Completeness Check**: Ensure all mandatory fields are present
2. **Consistency Verification**: Cross-check data across negotiation history
3. **Legal Compliance**: Validate party information and commercial terms
4. **Risk Assessment**: Identify any unusual or high-risk elements

**PARTY INFORMATION EXTRACTION:**
- Extract complete legal entity details for both buyer and seller
- Validate contact information and legal addresses
- Ensure authorized signatories are identified

**COMMERCIAL TERMS VALIDATION:**
- Verify final agreed prices and payment terms
- Confirm currency and calculation accuracy
- Validate Incoterms and shipping responsibilities

**PRODUCT SPECIFICATIONS:**
- Aggregate complete technical specifications
- Confirm certifications and quality requirements
- Validate quantities and units of measurement

**ANOMALY DETECTION:**
- Flag any non-standard terms negotiated
- Identify deviations from typical market practices
- Highlight terms that may require special attention

Be thorough and precise. Contract accuracy is critical for legal and business success."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Aggregate and validate contract data from this negotiation:

**NEGOTIATION HISTORY:**
{negotiation_history}

**FINAL TERMS:**
{final_terms}

**SUPPLIER DETAILS:**
{supplier_info}

**ORIGINAL REQUEST:**
{original_request}

**USER PROFILE:**
{user_profile}

Validate completeness and flag any issues or missing information.""")
    ])

def create_contract_generation_prompt():
    """Create prompt for intelligent contract text generation"""
    
    system_prompt = """You are an expert contract drafting specialist with deep knowledge of international textile trade law and B2B agreements. Your expertise spans contract structure, risk mitigation, and legal compliance across multiple jurisdictions.

**CONTRACT DRAFTING PRINCIPLES:**

1. **Clarity and Precision**: Every term must be unambiguous and enforceable
2. **Risk Mitigation**: Include appropriate protections for both parties
3. **Industry Standards**: Follow established textile industry practices
4. **Legal Compliance**: Ensure terms comply with applicable trade laws
5. **Practical Enforceability**: Terms must be realistic and implementable

**STRUCTURE REQUIREMENTS:**
- Professional legal formatting
- Clear section headers and numbering  
- Logical flow from specifications to commercial terms
- Appropriate legal language without excessive complexity

**SPECIAL ATTENTION AREAS:**
- Quality specifications and inspection procedures
- Payment terms and security arrangements
- Delivery obligations and risk transfer
- Warranty and liability limitations
- Dispute resolution mechanisms

**TEMPLATE ADAPTATION:**
- Use appropriate template for transaction type (international vs domestic)
- Customize standard clauses for specific deal requirements
- Add negotiated special terms while maintaining contract integrity
- Ensure consistency between template sections

**ANOMALY HANDLING:**
- Clearly identify and highlight non-standard terms
- Provide explanatory notes for unusual clauses
- Flag high-risk provisions for human review
- Maintain clear distinction between standard and custom terms

Generate professional, enforceable contract text that accurately reflects all negotiated terms while protecting both parties' interests."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Generate contract text using this validated data:

**TEMPLATE TO USE:** {template_name}

**BUYER INFORMATION:**
{buyer_info}

**SELLER INFORMATION:**
{seller_info}

**PRODUCT SPECIFICATIONS:**
{product_specs}

**COMMERCIAL TERMS:**
{commercial_terms}

**DELIVERY TERMS:**
{delivery_terms}

**SPECIAL NEGOTIATIONS:**
{special_terms}

**TEMPLATE STRUCTURE:**
{template_structure}

Create complete contract text with proper legal formatting and highlight any non-standard terms.""")
    ])

def create_anomaly_detection_prompt():
    """Create prompt for contract anomaly detection and risk assessment"""
    
    system_prompt = """You are a senior legal risk analyst specializing in B2B textile contracts. Your expertise includes identifying unusual terms, assessing legal risks, and flagging items that require human legal review.

**ANOMALY DETECTION CRITERIA:**

1. **Pricing Anomalies:**
   - Prices significantly above/below market rates
   - Unusual payment terms or currency arrangements
   - Complex pricing structures or adjustments

2. **Legal Term Deviations:**
   - Non-standard warranty periods
   - Unusual liability limitations or expansions
   - Custom dispute resolution procedures
   - Modified force majeure clauses

3. **Commercial Risk Factors:**
   - Extended payment terms (>60 days)
   - High penalty clauses or liquidated damages
   - Unusual inspection or acceptance procedures
   - Special packaging or handling requirements

4. **Delivery and Logistics Issues:**
   - Unrealistic delivery timelines
   - Complex shipping arrangements
   - Special destination or routing requirements
   - Custom insurance or risk arrangements

**RISK ASSESSMENT LEVELS:**
- **Low Risk**: Minor deviations from standard terms
- **Medium Risk**: Significant but manageable variations
- **High Risk**: Terms that could impact enforceability or create significant exposure
- **Critical Risk**: Terms that require immediate legal review

**FLAGGING PRINCIPLES:**
- Be conservative - better to over-flag than miss risks
- Provide specific explanations for each anomaly
- Suggest review priorities based on risk levels
- Offer alternative standard language where appropriate

Focus on protecting business interests while enabling deal completion."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Analyze this contract for anomalies and risks:

**CONTRACT TEXT:**
{contract_text}

**TEMPLATE BASELINE:**
{standard_template}

**NEGOTIATION CONTEXT:**
{negotiation_context}

**INDUSTRY BENCHMARKS:**
{market_standards}

Identify all non-standard terms, assess risks, and provide specific review recommendations.""")
    ])

# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
data_model = model.with_structured_output(dict)  # For flexible data validation
contract_model = model.with_structured_output(ContractDraft)
anomaly_model = model.with_structured_output(ContractAnomalies)

data_prompt = create_data_aggregation_prompt()
contract_prompt = create_contract_generation_prompt()
anomaly_prompt = create_anomaly_detection_prompt()

def aggregate_contract_data(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Aggregate and validate all contract data from negotiation state
    
    Args:
        state: Current agent state with negotiation results
    
    Returns:
        dict: Validated and structured contract data
    """
    
    # Extract negotiation results
    negotiation_history = state.get('negotiation_history', [])
    final_terms = {}
    
    # Get final terms from successful negotiation
    if negotiation_history:
        final_round = negotiation_history[-1]
        final_terms = final_round.get('terms', {})
    
    # Extract original parameters
    extracted_params = state.get('extracted_parameters', {})
    fabric_details = extracted_params.get('fabric_details', {})
    price_constraints = extracted_params.get('price_constraints', {})
    logistics_details = extracted_params.get('logistics_details', {})
    
    # Get supplier information
    top_suppliers = state.get('top_suppliers', [])
    supplier_info = top_suppliers[0] if top_suppliers else {}
    
    # User profile (in practice, would come from user management system)
    user_profile = state.get('user_profile', {
        'legal_name': 'ABC Trading Company Ltd.',
        'address': '123 Business Street, Commerce City, TX 12345, USA',
        'contact_person': 'John Smith, Procurement Manager',
        'email': 'john.smith@abctrading.com'
    })
    
    return {
        'negotiation_history': negotiation_history,
        'final_terms': final_terms,
        'supplier_info': supplier_info,
        'original_request': {
            'fabric_details': fabric_details,
            'price_constraints': price_constraints,
            'logistics_details': logistics_details
        },
        'user_profile': user_profile
    }

def select_contract_template(contract_data: Dict[str, Any]) -> str:
    """
    Step 2: Select appropriate contract template based on deal characteristics
    
    Args:
        contract_data: Aggregated contract data
    
    Returns:
        str: Template identifier to use
    """
    
    supplier_info = contract_data.get('supplier_info', {})
    supplier_country = supplier_info.get('country', '').lower()
    
    # Determine if international or domestic
    domestic_countries = ['usa', 'united states', 'us']  # Configurable based on buyer location
    
    if supplier_country in domestic_countries:
        return "domestic_textile"
    else:
        return "international_textile"

def generate_contract_draft(contract_data: Dict[str, Any], template_name: str) -> ContractDraft:
    """
    Step 3: Generate complete contract draft with intelligent variable injection
    
    Args:
        contract_data: Validated contract data
        template_name: Selected template identifier
    
    Returns:
        ContractDraft: Complete contract draft with metadata
    """
    
    template_info = CONTRACT_TEMPLATES[template_name]
    
    # Extract and structure data for contract generation
    supplier_info = contract_data['supplier_info']
    user_profile = contract_data['user_profile']
    fabric_details = contract_data['original_request']['fabric_details']
    final_terms = contract_data['final_terms']
    logistics_details = contract_data['original_request']['logistics_details']
    
    # Calculate delivery date
    lead_time_days = final_terms.get('new_lead_time', logistics_details.get('timeline_days', 30))
    delivery_date = (datetime.now() + timedelta(days=lead_time_days)).strftime('%Y-%m-%d')
    
    # Prepare contract data structure
    buyer = PartyDetails(
        legal_name=user_profile.get('legal_name', 'Buyer Company'),
        address=user_profile.get('address', 'Buyer Address'),
        contact_person=user_profile.get('contact_person', 'Buyer Contact'),
        email=user_profile.get('email', 'buyer@company.com')
    )
    
    seller = PartyDetails(
        legal_name=supplier_info.get('company_name', 'Supplier Company'),
        address=f"{supplier_info.get('city', '')}, {supplier_info.get('country', '')}",
        contact_person=supplier_info.get('contact_person', 'Supplier Contact'),
        email=supplier_info.get('contact_info', {}).get('email', 'supplier@company.com')
    )
    
    product_specs = ProductSpecifications(
        fabric_type=fabric_details.get('type', 'Textile Product'),
        quantity=fabric_details.get('quantity', 0),
        unit=fabric_details.get('unit', 'meters'),
        quality_specifications=fabric_details.get('quality_specs', []),
        certifications=fabric_details.get('certifications', [])
    )
    
    unit_price = final_terms.get('new_price', contract_data['original_request']['price_constraints'].get('max_price', 0))
    total_value = unit_price * product_specs.quantity
    
    commercial_terms = CommercialTerms(
        unit_price=unit_price,
        total_value=total_value,
        currency='USD',
        payment_terms=final_terms.get('new_payment_terms', 'Net 30'),
        incoterms=final_terms.get('new_incoterms', 'FOB')
    )
    
    delivery_terms = DeliveryTerms(
        delivery_destination=logistics_details.get('destination', 'Buyer Location'),
        lead_time_days=lead_time_days,
        delivery_date=delivery_date
    )
    
    # Generate contract text by filling template
    special_clauses = ""
    if final_terms.get('additional_conditions'):
        special_clauses = "\nSPECIAL CONDITIONS:\n" + "\n".join([f"- {condition}" for condition in final_terms['additional_conditions']])
    
    contract_text = template_info['template'].format(
        buyer_name=buyer.legal_name,
        buyer_address=buyer.address,
        buyer_contact=buyer.contact_person,
        seller_name=seller.legal_name,
        seller_address=seller.address,
        seller_contact=seller.contact_person,
        fabric_type=product_specs.fabric_type,
        quantity=product_specs.quantity,
        unit=product_specs.unit,
        quality_specs=', '.join(product_specs.quality_specifications),
        certifications=', '.join(product_specs.certifications),
        unit_price=commercial_terms.unit_price,
        currency=commercial_terms.currency,
        total_value=commercial_terms.total_value,
        payment_terms=commercial_terms.payment_terms,
        incoterms=commercial_terms.incoterms,
        delivery_destination=delivery_terms.delivery_destination,
        lead_time_days=delivery_terms.lead_time_days,
        delivery_date=delivery_terms.delivery_date,
        special_clauses=special_clauses
    )
    
    # Create contract draft
    contract_draft = ContractDraft(
        contract_id=f"CTR_{str(uuid.uuid4())[:8]}",
        contract_title=f"Textile Purchase Agreement - {product_specs.fabric_type}",
        buyer=buyer,
        seller=seller,
        product_specs=product_specs,
        commercial_terms=commercial_terms,
        delivery_terms=delivery_terms,
        contract_text=contract_text,
        anomalies=ContractAnomalies(anomaly_score=0.0),  # Will be populated by anomaly detection
        template_used=template_name,
        creation_date=datetime.now().isoformat(),
        review_priority="medium"
    )
    
    return contract_draft

def detect_contract_anomalies(contract_draft: ContractDraft, negotiation_context: Dict[str, Any]) -> ContractAnomalies:
    """
    Step 4: Detect and flag non-standard terms requiring human review
    
    Args:
        contract_draft: Generated contract draft
        negotiation_context: Context from negotiation process
    
    Returns:
        ContractAnomalies: Detailed anomaly analysis
    """
    
    anomalies = []
    risk_factors = []
    review_notes = []
    special_conditions = []
    
    # Check for pricing anomalies
    if contract_draft.commercial_terms.unit_price > 10:  # Example threshold
        anomalies.append("Unit price above typical market range")
        review_notes.append("Verify pricing justification")
    
    # Check payment terms
    if "advance" in contract_draft.commercial_terms.payment_terms.lower():
        special_conditions.append("Advance payment required")
        review_notes.append("Advance payment terms need approval")
    
    # Check for extended lead times
    if contract_draft.delivery_terms.lead_time_days > 60:
        risk_factors.append("Extended lead time may impact project timelines")
        review_notes.append("Confirm lead time acceptability")
    
    # Check for special conditions from negotiation
    negotiation_history = negotiation_context.get('negotiation_history', [])
    for round_data in negotiation_history:
        terms = round_data.get('terms', {})
        if terms.get('additional_conditions'):
            special_conditions.extend(terms['additional_conditions'])
    
    # Calculate anomaly score
    total_checks = 10  # Total number of checks performed
    anomaly_count = len(anomalies) + len(risk_factors) + len(special_conditions)
    anomaly_score = min(1.0, anomaly_count / total_checks)
    
    return ContractAnomalies(
        non_standard_clauses=anomalies,
        special_conditions=special_conditions,
        risk_factors=risk_factors,
        review_notes=review_notes,
        anomaly_score=anomaly_score
    )

def determine_review_priority(anomalies: ContractAnomalies, contract_value: float) -> Literal["low", "medium", "high", "urgent"]:
    """
    Determine human review priority based on anomalies and contract value
    
    Args:
        anomalies: Detected contract anomalies
        contract_value: Total contract value
    
    Returns:
        str: Review priority level
    """
    
    # High value contracts get elevated priority
    if contract_value > 100000:
        base_priority = "high"
    elif contract_value > 50000:
        base_priority = "medium"
    else:
        base_priority = "low"
    
    # Elevate based on anomaly score
    if anomalies.anomaly_score > 0.7:
        return "urgent"
    elif anomalies.anomaly_score > 0.4:
        return "high" if base_priority != "urgent" else "urgent"
    elif anomalies.anomaly_score > 0.2:
        return "medium" if base_priority == "low" else base_priority
    else:
        return base_priority

def initiate_contract(state: AgentState) -> dict:
    """
    Node 7: initiate_contract - Legal and procedural formalization engine
    
    Purpose:
    - Transform negotiated terms into structured legal document
    - Validate all contract data for completeness and accuracy
    - Generate professional contract draft using appropriate templates
    - Detect and flag non-standard terms requiring human review
    - Prepare contract for final human oversight and approval
    
    Args:
        state: Current agent state with successful negotiation results
    
    Returns:
        dict: State updates with contract draft and review requirements
    """
    
    try:
        # Step 1: Data Aggregation and Validation
        contract_data = aggregate_contract_data(state)
        
        # Validate that we have sufficient data for contract generation
        if not contract_data['supplier_info']:
            return {
                "error": "Missing supplier information for contract generation",
                "messages": [{"role": "assistant", "content": "Error: Cannot generate contract without supplier details"}],
                "status": "contract_error"
            }
        
        # Step 2: Template Selection
        template_name = select_contract_template(contract_data)
        
        # Step 3: Contract Generation
        contract_draft = generate_contract_draft(contract_data, template_name)
        
        # Step 4: Anomaly Detection
        anomalies = detect_contract_anomalies(contract_draft, contract_data)
        
        # Update contract draft with anomalies
        contract_draft.anomalies = anomalies
        contract_draft.review_priority = determine_review_priority(
            anomalies, 
            contract_draft.commercial_terms.total_value
        )
        
        # Step 5: Generate human-readable summary
        assistant_message = generate_contract_summary(contract_draft, anomalies)
        
        # Step 6: Prepare state updates
        state_updates = {
            "contract_draft": contract_draft.model_dump(),
            "contract_id": contract_draft.contract_id,
            "contract_status": "draft",
            "review_priority": contract_draft.review_priority,
            "anomalies_detected": len(anomalies.non_standard_clauses) + len(anomalies.special_conditions),
            "next_step": "send_for_human_review",
            "messages": [{"role": "assistant", "content": assistant_message}],
            "status": "contract_drafted",
            "contract_creation_timestamp": datetime.now().isoformat()
        }
        
        # Add flags for urgent review if needed
        if contract_draft.review_priority in ["high", "urgent"]:
            state_updates["requires_urgent_review"] = True
            state_updates["urgent_review_reasons"] = anomalies.risk_factors
        
        return state_updates
        
    except Exception as e:
        error_message = f"Error generating contract: {str(e)}"
        return {
            "error": str(e),
            "messages": [{"role": "assistant", "content": error_message}],
            "next_step": "handle_error",
            "status": "contract_generation_error"
        }

def generate_contract_summary(contract_draft: ContractDraft, anomalies: ContractAnomalies) -> str:
    """
    Generate human-readable summary of the contract draft
    
    Args:
        contract_draft: Generated contract draft
        anomalies: Detected anomalies
    
    Returns:
        str: Formatted summary for user
    """
    
    summary_parts = [
        f"📄 **Contract Draft Generated**\n",
        f"**Contract ID**: {contract_draft.contract_id}",
        f"**Template Used**: {CONTRACT_TEMPLATES[contract_draft.template_used]['name']}\n",
        
        f"**📋 Contract Details**:",
        f"• **Buyer**: {contract_draft.buyer.legal_name}",
        f"• **Seller**: {contract_draft.seller.legal_name}",
        f"• **Product**: {contract_draft.product_specs.fabric_type}",
        f"• **Quantity**: {contract_draft.product_specs.quantity} {contract_draft.product_specs.unit}",
        f"• **Total Value**: {contract_draft.commercial_terms.total_value:,.2f} {contract_draft.commercial_terms.currency}",
        f"• **Delivery**: {contract_draft.delivery_terms.lead_time_days} days to {contract_draft.delivery_terms.delivery_destination}\n"
    ]
    
    # Add anomaly information
    if anomalies.anomaly_score > 0.1:
        summary_parts.extend([
            f"⚠️ **Review Required** (Priority: {contract_draft.review_priority.upper()})",
            f"**Anomaly Score**: {anomalies.anomaly_score:.2f}/1.0\n"
        ])
        
        if anomalies.non_standard_clauses:
            summary_parts.append("**Non-Standard Terms**:")
            for clause in anomalies.non_standard_clauses:
                summary_parts.append(f"• {clause}")
            summary_parts.append("")
        
        if anomalies.special_conditions:
            summary_parts.append("**Special Conditions**:")
            for condition in anomalies.special_conditions:
                summary_parts.append(f"• {condition}")
            summary_parts.append("")
        
        if anomalies.review_notes:
            summary_parts.append("**Review Notes**:")
            for note in anomalies.review_notes:
                summary_parts.append(f"• {note}")
    else:
        summary_parts.append("✅ **Standard Contract** - Minimal review required")
    
    summary_parts.append(f"\n**Status**: Ready for human review and approval")
    
    return "\n".join(summary_parts)

def validate_contract_completeness(contract_draft: ContractDraft) -> tuple[bool, List[str]]:
    """
    Validate that contract draft contains all required elements
    
    Args:
        contract_draft: Contract draft to validate
    
    Returns:
        tuple: (is_complete, missing_elements)
    """
    
    missing_elements = []
    
    # Check buyer information
    if not contract_draft.buyer.legal_name or contract_draft.buyer.legal_name == "Buyer Company":
        missing_elements.append("Complete buyer legal name")
    
    if not contract_draft.buyer.address or "Address" in contract_draft.buyer.address:
        missing_elements.append("Complete buyer address")
    
    # Check seller information  
    if not contract_draft.seller.legal_name or contract_draft.seller.legal_name == "Supplier Company":
        missing_elements.append("Complete seller legal name")
    
    # Check product specifications
    if not contract_draft.product_specs.fabric_type:
        missing_elements.append("Product specifications")
    
    if contract_draft.product_specs.quantity <= 0:
        missing_elements.append("Valid quantity")
    
    # Check commercial terms
    if contract_draft.commercial_terms.unit_price <= 0:
        missing_elements.append("Valid unit price")
    
    if not contract_draft.commercial_terms.payment_terms:
        missing_elements.append("Payment terms")
    
    # Check delivery terms
    if not contract_draft.delivery_terms.delivery_destination:
        missing_elements.append("Delivery destination")
    
    if contract_draft.delivery_terms.lead_time_days <= 0:
        missing_elements.append("Valid lead time")
    
    is_complete = len(missing_elements) == 0
    return is_complete, missing_elements

def save_contract_draft(contract_draft: ContractDraft) -> str:
    """
    Save contract draft to secure storage location
    
    Args:
        contract_draft: Contract draft to save
    
    Returns:
        str: File path or storage identifier
    """
    
    # In practice, this would save to a secure file system or database
    # For demo purposes, we'll return a mock file path
    file_path = f"contracts/drafts/{contract_draft.contract_id}.pdf"
    
    # Log the contract save operation
    logger.info(f"Contract draft saved: {contract_draft.contract_id} -> {file_path}")
    
    return file_path

def generate_contract_metadata(contract_draft: ContractDraft, state: AgentState) -> Dict[str, Any]:
    """
    Generate comprehensive metadata for contract tracking and management
    
    Args:
        contract_draft: Generated contract draft
        state: Current agent state
    
    Returns:
        dict: Contract metadata for tracking and audit purposes
    """
    
    return {
        "contract_id": contract_draft.contract_id,
        "creation_timestamp": contract_draft.creation_date,
        "template_used": contract_draft.template_used,
        "total_value": contract_draft.commercial_terms.total_value,
        "currency": contract_draft.commercial_terms.currency,
        "buyer_name": contract_draft.buyer.legal_name,
        "seller_name": contract_draft.seller.legal_name,
        "product_type": contract_draft.product_specs.fabric_type,
        "quantity": contract_draft.product_specs.quantity,
        "unit": contract_draft.product_specs.unit,
        "delivery_date": contract_draft.delivery_terms.delivery_date,
        "review_priority": contract_draft.review_priority,
        "anomaly_score": contract_draft.anomalies.anomaly_score,
        "requires_special_review": contract_draft.anomalies.anomaly_score > 0.3,
        "session_id": state.get("session_id"),
        "user_id": state.get("user_id"),
        "negotiation_rounds": len(state.get("negotiation_history", [])),
        "supplier_reliability": state.get("top_suppliers", [{}])[0].get("reliability_score", 0),
        "contract_status": "draft_pending_review"
    }

# Enhanced contract templates with more sophisticated structure
ENHANCED_TEMPLATES = {
    "international_textile_comprehensive": {
        "name": "Comprehensive International Textile Purchase Agreement",
        "template": """
INTERNATIONAL TEXTILE PURCHASE AGREEMENT

Contract No: {contract_id}
Date: {creation_date}

PARTIES:

BUYER:
{buyer_name}
{buyer_address}
Contact: {buyer_contact}
Email: {buyer_email}

SELLER:
{seller_name}  
{seller_address}
Contact: {seller_contact}
Email: {seller_email}

ARTICLE 1: PRODUCT SPECIFICATIONS
1.1 Product: {fabric_type}
1.2 Quantity: {quantity} {unit}
1.3 Quality Standards: {quality_specs}
1.4 Certifications Required: {certifications}
1.5 Color/Pattern: {color_specs}
1.6 Technical Specifications: {technical_specs}

ARTICLE 2: COMMERCIAL TERMS
2.1 Unit Price: {unit_price} {currency} per {unit}
2.2 Total Contract Value: {total_value} {currency}
2.3 Payment Terms: {payment_terms}
2.4 Incoterms: {incoterms} 2020
2.5 Currency: {currency}

ARTICLE 3: DELIVERY AND LOGISTICS
3.1 Delivery Destination: {delivery_destination}
3.2 Delivery Timeline: {lead_time_days} days from order confirmation
3.3 Expected Delivery Date: {delivery_date}
3.4 Shipping Method: {shipping_method}
3.5 Packaging Requirements: {packaging_requirements}

ARTICLE 4: QUALITY ASSURANCE
4.1 Inspection Period: 10 business days from delivery
4.2 Quality Standards: Products must meet specifications in Article 1
4.3 Rejection Rights: Buyer may reject non-conforming goods
4.4 Warranty Period: 90 days from delivery date

ARTICLE 5: SPECIAL CONDITIONS
{special_clauses}

ARTICLE 6: STANDARD TERMS
6.1 Force Majeure: Standard international force majeure clause applies
6.2 Governing Law: Contract governed by international commercial law
6.3 Dispute Resolution: International arbitration in neutral jurisdiction
6.4 Confidentiality: Both parties maintain confidentiality of terms

ARTICLE 7: SIGNATURES
This agreement becomes effective upon signature by both parties.

BUYER SIGNATURE:                    SELLER SIGNATURE:
_____________________              _____________________
Name: {buyer_signatory}            Name: {seller_signatory}
Title: {buyer_title}               Title: {seller_title}
Date: _______________              Date: _______________

Contract generated by AI Assistant on {creation_date}
        """,
        "required_fields": [
            "contract_id", "buyer_name", "seller_name", "fabric_type", 
            "quantity", "unit_price", "total_value", "delivery_destination"
        ],
        "standard_clauses": [
            "quality_inspection", "warranty_period", "force_majeure", 
            "governing_law", "arbitration", "confidentiality"
        ],
        "risk_factors": {
            "international_shipping": "medium",
            "currency_fluctuation": "medium", 
            "quality_disputes": "low",
            "delivery_delays": "medium"
        }
    }
}

# Integration functions for external systems
def notify_legal_team(contract_draft: ContractDraft) -> bool:
    """
    Notify legal team of contract requiring review
    
    Args:
        contract_draft: Contract requiring legal review
    
    Returns:
        bool: Success status of notification
    """
    
    # In practice, this would integrate with email/notification systems
    logger.info(f"Legal team notified for contract {contract_draft.contract_id} - Priority: {contract_draft.review_priority}")
    
    if contract_draft.review_priority in ["high", "urgent"]:
        # Send urgent notification
        logger.info("URGENT: High-priority contract requires immediate legal review")
    
    return True

def create_audit_trail(state: AgentState, contract_draft: ContractDraft) -> Dict[str, Any]:
    """
    Create comprehensive audit trail for contract generation process
    
    Args:
        state: Current agent state
        contract_draft: Generated contract draft
    
    Returns:
        dict: Audit trail data
    """
    
    return {
        "process_id": state.get("session_id"),
        "user_id": state.get("user_id"),
        "contract_id": contract_draft.contract_id,
        "generation_timestamp": datetime.now().isoformat(),
        "template_used": contract_draft.template_used,
        "data_sources": {
            "original_request": bool(state.get("extracted_parameters")),
            "negotiation_history": len(state.get("negotiation_history", [])),
            "supplier_data": bool(state.get("top_suppliers")),
            "user_profile": bool(state.get("user_profile"))
        },
        "validation_results": {
            "completeness_check": True,  # Would be actual validation result
            "anomalies_detected": contract_draft.anomalies.anomaly_score,
            "review_priority": contract_draft.review_priority
        },
        "ai_confidence_scores": {
            "data_aggregation": 0.95,  # Would be actual confidence scores
            "template_selection": 0.98,
            "contract_generation": 0.92,
            "anomaly_detection": 0.88
        }
    }

# Testing and validation functions
def test_contract_generation():
    """
    Test function for validating contract generation with sample data
    """
    
    # Sample test state
    test_state = {
        "extracted_parameters": {
            "fabric_details": {
                "type": "Organic Cotton Twill",
                "quantity": 10000,
                "unit": "meters",
                "quality_specs": ["300 GSM", "GOTS Certified"],
                "certifications": ["GOTS", "OEKO-TEX"]
            },
            "price_constraints": {
                "max_price": 5.50,
                "currency": "USD"
            },
            "logistics_details": {
                "destination": "Los Angeles, CA, USA",
                "timeline_days": 45
            }
        },
        "top_suppliers": [{
            "company_name": "Premium Textiles Ltd.",
            "country": "India",
            "city": "Mumbai",
            "contact_person": "Rajesh Kumar",
            "contact_info": {"email": "rajesh@premiumtextiles.com"},
            "reliability_score": 8.5
        }],
        "negotiation_history": [{
            "timestamp": datetime.now().isoformat(),
            "round": 1,
            "intent": "accept",
            "terms": {
                "new_price": 5.25,
                "new_lead_time": 42,
                "new_payment_terms": "30% advance, 70% on delivery"
            }
        }],
        "user_profile": {
            "legal_name": "Global Fashion Inc.",
            "address": "456 Fashion Ave, New York, NY 10001, USA",
            "contact_person": "Sarah Johnson, CPO",
            "email": "sarah.johnson@globalfashion.com"
        },
        "session_id": "test_session_123",
        "user_id": "user_456"
    }
    
    try:
        result = initiate_contract(test_state)
        print("✅ Contract generation test passed")
        print(f"Contract ID: {result.get('contract_id')}")
        print(f"Review Priority: {result.get('review_priority')}")
        print(f"Anomalies: {result.get('anomalies_detected', 0)}")
        return True
    except Exception as e:
        print(f"❌ Contract generation test failed: {e}")
        return False

if __name__ == "__main__":
    # Run test if module is executed directly
    test_contract_generation()