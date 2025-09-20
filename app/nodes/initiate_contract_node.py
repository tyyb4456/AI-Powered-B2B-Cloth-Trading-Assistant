from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from models.contract_model import DraftedContract, ContractTerms, ContractMetadata
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import json

load_dotenv()


def extract_negotiation_context(state: AgentState) -> Dict[str, Any]:
    """
    Extract comprehensive context from the negotiation process
    
    This function analyzes the entire negotiation history and extracts
    the final agreed terms, supplier information, and contract requirements.
    """
    
    # Extract negotiated terms from the negotiation analysis
    extracted_terms = state.get('extracted_terms') or {}
    negotiation_analysis = state.get('negotiation_analysis', {})
    supplier_intent = state.get('supplier_intent', {})
    
    # Get original request parameters
    extracted_params = state.get('extracted_parameters', {})
    
    # Get supplier information
    supplier_data = state.get('top_suppliers', [])
    active_supplier = supplier_data[0] if supplier_data else {}
    
    # Get negotiation history for context
    negotiation_history = state.get('negotiation_history', [])
    
    # Extract final agreed terms
    final_terms = {}
    
    # Fabric specifications (from original + any modifications)
    if isinstance(extracted_params, dict):
        fabric_details = extracted_params.get('fabric_details', {})
        final_terms['fabric_specifications'] = {
            'fabric_type': fabric_details.get('type') or 'Not specified',
            'quality_grade': 'Standard',
            'gsm': 'As per specification',
            'composition': fabric_details.get('composition') or 'As per specification',
            'color': fabric_details.get('color') or 'As per buyer requirement',
            'width': fabric_details.get('width') or 'Standard width',
            'finish': fabric_details.get('finish') or 'Standard finish',
        }
        
        # Quantity (from original or negotiated)
        original_quantity = fabric_details.get('quantity') or 1000
        final_terms['quantity'] = original_quantity
        
        # Pricing (from negotiation or quote)
        generated_quote = state.get('generated_quote', {})
        if isinstance(generated_quote, dict):
            original_price = generated_quote.get('unit_price', 10.0)
        else:
            original_price = 10.0
            
        negotiated_price = extracted_terms.get('new_price', original_price)
        final_terms['unit_price'] = negotiated_price
        final_terms['total_value'] = final_terms['quantity'] * final_terms['unit_price']
        final_terms['currency'] = 'USD'
        
        # Delivery terms
        logistics_details = extracted_params.get('logistics_details', {})
        final_terms['delivery_terms'] = {
            'delivery_timeline': '45-60 days',
            'shipping_method': 'Sea freight',
            'incoterms': 'FOB',
            'delivery_location': 'Buyer warehouse',
            'partial_shipments': 'Allowed with prior notice'
        }
        
        # Payment terms
        final_terms['payment_terms'] = {
            'advance_percentage': 30,
            'payment_method': 'Bank transfer',
            'balance_terms': 'Against delivery documents',
            'currency': final_terms['currency'],
            'late_payment_penalty': '2% per month'
        }
        
        # Quality standards
        final_terms['quality_standards'] = {
            'quality_control': 'Pre-shipment inspection required',
            'testing_standards': 'International textile standards',
            'defect_tolerance': '2% maximum',
            'sampling_procedure': 'Random sampling as per AQL standards',
            'certification': extracted_params.get('certifications', [])
        }
    
    # Contract metadata - Convert dictionaries to strings
    buyer_company_dict = {
        'name': 'Buyer Company Name',
        'address': 'Buyer Company Address',
        'contact_person': 'Procurement Manager',
        'email': state.get('recipient_email', 'buyer@company.com'),
        'phone': '+1-XXX-XXX-XXXX'
    }
    
    supplier_company_dict = {
        'name': active_supplier.get('name', 'Supplier Company'),
        'address': active_supplier.get('address', 'Supplier Address'),
        'location': active_supplier.get('location', 'Unknown'),
        'contact_person': active_supplier.get('contact_person', 'Sales Manager'),
        'email': active_supplier.get('email', 'supplier@company.com'),
        'phone': active_supplier.get('phone', '+X-XXX-XXX-XXXX'),
        'reliability_score': active_supplier.get('reliability_score', 5.0)
    }
    
    contract_metadata = {
        'buyer_company': json.dumps(buyer_company_dict),  # Convert to JSON string
        'supplier_company': json.dumps(supplier_company_dict),  # Convert to JSON string
        'contract_urgency': extracted_params.get('urgency_level', 'medium') if isinstance(extracted_params, dict) else 'medium',
        'negotiation_rounds': len(negotiation_history),
        'agreement_confidence': negotiation_analysis.get('confidence_score', 0.8) if isinstance(negotiation_analysis, dict) else 0.8
    }
    
    return {
        'final_terms': final_terms,
        'contract_metadata': contract_metadata,
        'negotiation_context': {
            'total_rounds': len(negotiation_history),
            'supplier_intent': supplier_intent.get('intent') if isinstance(supplier_intent, dict) else 'accept',
            'key_concessions': 'concessions_made',
            'remaining_issues': negotiation_analysis.get('remaining_concerns', []) if isinstance(negotiation_analysis, dict) else []
        }
    }


def create_contract_terms_prompt():
    """Create prompt for extracting and structuring contract terms"""
    
    system_prompt = """You are an expert legal AI assistant specializing in B2B textile procurement contracts. Your task is to analyze negotiated terms and structure them into a comprehensive contract terms format.

**EXPERTISE AREAS:**
- International textile trade contracts
- B2B procurement legal frameworks
- Supply chain contract structuring
- Risk assessment and mitigation clauses
- Compliance with international trade laws

**CONTRACT STRUCTURING PRINCIPLES:**

1. **Completeness**: Ensure all negotiated terms are captured accurately
2. **Legal Soundness**: Include necessary protective clauses for both parties
3. **Risk Mitigation**: Identify and address potential risks through appropriate clauses
4. **Industry Standards**: Apply textile industry best practices and standards
5. **Enforceability**: Structure terms for legal enforceability across jurisdictions

**KEY COMPONENTS TO STRUCTURE:**

**Fabric Specifications:**
- Technical specifications with measurable parameters
- Quality standards and testing requirements
- Acceptable variance ranges
- Certification requirements

**Commercial Terms:**
- Precise pricing structure with currency
- Quantity specifications with tolerance levels
- Total contract value calculations
- Price escalation/de-escalation clauses if applicable

**Delivery & Logistics:**
- Clear delivery timelines with milestone dates
- Shipping terms and responsibilities (Incoterms)
- Partial shipment conditions
- Delivery acceptance criteria

**Payment Structure:**
- Payment schedule with specific percentages
- Payment methods and currency
- Late payment penalties
- Security arrangements (if any)

**Quality & Compliance:**
- Quality control procedures
- Inspection and testing protocols
- Defect handling procedures
- Compliance certifications required

**Risk Management:**
- Force majeure provisions
- Penalty clauses for delays or quality issues
- Insurance requirements
- Dispute resolution mechanisms

Analyze the negotiation context and structure comprehensive contract terms that protect both parties while reflecting the agreed-upon conditions."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Structure the following negotiated terms into comprehensive contract terms:

**NEGOTIATED FINAL TERMS:**
{final_terms}

**SUPPLIER INFORMATION:**
{supplier_info}

**NEGOTIATION CONTEXT:**
- Negotiation rounds: {negotiation_rounds}
- Supplier intent: {supplier_intent}
- Key concessions made: {key_concessions}
- Agreement confidence: {agreement_confidence}

**CONTRACT REQUIREMENTS:**
- Urgency level: {urgency_level}
- Industry: Textile procurement
- Contract type: Supply agreement

Please structure these terms into a comprehensive ContractTerms format with all necessary details, protective clauses, and industry-standard provisions.""")
    ])


def create_contract_drafting_prompt():
    """Create prompt for drafting the complete contract document"""
    
    system_prompt = """You are a senior legal counsel and contract drafting specialist with extensive experience in international B2B textile procurement agreements. Your expertise covers:

- International commercial law and trade regulations
- Textile industry contract standards and best practices
- Cross-border procurement legal frameworks
- Risk management and dispute resolution
- Contract enforcement across multiple jurisdictions

**CONTRACT DRAFTING PRINCIPLES:**

1. **Professional Structure**: Follow standard commercial contract format
2. **Legal Precision**: Use precise legal language while maintaining clarity
3. **Balanced Protection**: Protect both buyer and supplier interests fairly
4. **Industry Compliance**: Incorporate textile industry standards and regulations
5. **Practical Enforceability**: Ensure terms are practically enforceable

**STANDARD CONTRACT STRUCTURE:**

**1. PREAMBLE**
- Party identification with complete legal details
- Contract purpose and background
- Recitals establishing context

**2. DEFINITIONS**
- Key terms and their precise meanings
- Technical specifications definitions
- Commercial terms definitions

**3. SCOPE OF SUPPLY**
- Detailed product specifications
- Quantity and measurement units
- Quality standards and requirements

**4. COMMERCIAL TERMS**
- Pricing and payment structure
- Currency and exchange rate provisions
- Invoicing and payment procedures

**5. DELIVERY & LOGISTICS**
- Delivery timelines and milestones
- Shipping terms and responsibilities
- Risk transfer points

**6. QUALITY ASSURANCE**
- Quality control procedures
- Testing and inspection protocols
- Acceptance and rejection criteria

**7. LEGAL & COMPLIANCE**
- Governing law and jurisdiction
- Dispute resolution mechanisms
- Regulatory compliance requirements

**8. RISK MANAGEMENT**
- Force majeure provisions
- Limitation of liability clauses
- Insurance and indemnification

**9. GENERAL PROVISIONS**
- Contract modification procedures
- Termination conditions
- Confidentiality obligations

**10. EXECUTION**
- Signature blocks for authorized representatives
- Date and place of execution
- Witness requirements (if applicable)

**DRAFTING GUIDELINES:**
- Use clear, unambiguous language
- Avoid legal jargon where possible
- Include specific dates, amounts, and measurable criteria
- Ensure mutual obligations are balanced
- Incorporate appropriate industry standards
- Include practical dispute resolution mechanisms

Generate a complete, professional contract document that reflects the negotiated terms while providing comprehensive legal protection for both parties."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Draft a complete B2B textile procurement contract based on these structured terms:

**CONTRACT TERMS:**
{contract_terms}

**CONTRACT METADATA:**
- Contract ID: {contract_id}
- Buyer: {buyer_company}
- Supplier: {supplier_company}
- Contract Type: {contract_type}
- Governing Law: {governing_law}
- Creation Date: {creation_date}

**CONTEXT:**
- Negotiation History: {negotiation_rounds} rounds completed
- Agreement Confidence: {agreement_confidence}
- Urgency Level: {urgency_level}

**REQUIREMENTS:**
- Professional legal document format
- Comprehensive protective clauses
- Industry-standard terms and conditions
- Clear obligations for both parties
- Practical enforcement mechanisms

Please generate:
1. Complete contract title
2. Professional preamble with party details
3. Comprehensive terms and conditions
4. Appropriate schedules/annexures (if needed)
5. Formal signature block

The contract should be ready for legal review and execution.""")
    ])


# Initialize models and prompts
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
terms_model = model.with_structured_output(ContractTerms)
contract_model = model.with_structured_output(DraftedContract)

terms_prompt = create_contract_terms_prompt()
contract_prompt = create_contract_drafting_prompt()


def initiate_contract(state: AgentState):
    """
    Node: initiate_contract - Contract Drafting Agent
    
    Purpose:
    - Analyze complete negotiation history and final agreed terms
    - Extract structured contract terms from negotiation outcomes
    - Generate comprehensive preliminary contract document
    - Prepare contract for legal review and execution
    - Ensure compliance with industry standards and legal requirements
    
    Process Flow:
    1. Extract negotiation context and final agreed terms
    2. Structure terms into comprehensive contract format
    3. Generate professional contract document
    4. Perform quality validation and compliance checks
    5. Prepare for legal review and next steps
    
    Args:
        state: Current agent state with negotiation history and outcomes
    
    Returns:
        dict: State updates with drafted contract and metadata
    """
    
    try:
        print("📄 Initiating contract drafting process...")
        
        # Step 1: Extract comprehensive negotiation context
        negotiation_context = extract_negotiation_context(state)
        final_terms = negotiation_context['final_terms']
        metadata = negotiation_context['contract_metadata']
        
        # Generate unique contract ID
        contract_id = f"CTXT_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
        
        print(f"📋 Generated Contract ID: {contract_id}")
        print(f"💼 Supplier: {json.loads(metadata['supplier_company'])['name']}")
        print(f"📦 Quantity: {final_terms['quantity'] or 'N/A'} meters")
        print(f"💰 Total Value: {final_terms['currency'] or 'USD'} {final_terms['total_value'] or 'N/A'}")

            
        # Step 2: Structure negotiated terms using AI
        print("🔍 Structuring contract terms...")
        terms_formatted_prompt = terms_prompt.invoke({
            "final_terms": str(final_terms),
            "supplier_info": metadata['supplier_company'],
            "negotiation_rounds": metadata['negotiation_rounds'],
            "supplier_intent": negotiation_context['negotiation_context']['supplier_intent'],
            "key_concessions": str(negotiation_context['negotiation_context']['key_concessions']),
            "agreement_confidence": metadata['agreement_confidence'],
            "urgency_level": metadata['contract_urgency']
        })
        
        # Get structured contract terms from AI
        structured_terms: ContractTerms = terms_model.invoke(terms_formatted_prompt)
        
        # Step 3: Create contract metadata with proper string conversion
        contract_metadata = ContractMetadata(
            contract_id=contract_id,
            contract_type="textile_procurement_agreement",
            contract_version="1.0",
            buyer_company=metadata['buyer_company'],  # Already a JSON string
            supplier_company=metadata['supplier_company'],  # Already a JSON string
            creation_date=datetime.now().isoformat(),  # Convert datetime to ISO string
            effective_date=None,
            expiry_date=None,
            governing_law="International Commercial Law",
            jurisdiction=None
        )
        
        # Step 4: Generate complete contract document using AI
        print("📝 Drafting complete contract document...")
        contract_formatted_prompt = contract_prompt.invoke({
            "contract_terms": structured_terms.model_dump(),
            "contract_id": contract_id,
            "buyer_company": json.loads(metadata['buyer_company'])['name'],
            "supplier_company": json.loads(metadata['supplier_company'])['name'],
            "contract_type": "Textile Procurement Agreement",
            "governing_law": "International Commercial Law",
            "creation_date": datetime.now().strftime("%B %d, %Y"),
            "negotiation_rounds": metadata['negotiation_rounds'],
            "agreement_confidence": f"{metadata['agreement_confidence']:.2f}",
            "urgency_level": metadata['contract_urgency']
        })
        
        # Get complete drafted contract from AI
        drafted_contract: DraftedContract = contract_model.invoke(contract_formatted_prompt)
        
        # Step 5: Enhance contract with metadata and validation
        drafted_contract.contract_id = contract_id
        drafted_contract.contract_terms_summary = str(structured_terms.model_dump())
        drafted_contract.contract_metadata_summary = str(contract_metadata.model_dump())
        drafted_contract.generation_timestamp = datetime.now().isoformat()
        
        # Step 6: Perform quality validation
        validation_results = validate_contract_quality(drafted_contract, negotiation_context)
        
        # Step 7: Generate recommendations and next steps
        recommended_actions = generate_contract_recommendations(
            drafted_contract, 
            negotiation_context, 
            validation_results
        )
        
        drafted_contract.recommended_actions = recommended_actions
        
        # Step 8: Create assistant response message
        supplier_name = json.loads(metadata['supplier_company'])['name']
        contract_value = final_terms['total_value'] or 'TBD'
        currency = final_terms['currency'] or 'USD'
        
        assistant_message = f"""📋 **Contract Successfully Drafted**

**Contract Details:**
• **Contract ID:** {contract_id}
• **Parties:** Your Company ↔ {supplier_name}
• **Contract Value:** {currency} {contract_value:,.2f}
• **Contract Type:** Textile Procurement Agreement
• **Status:** Draft - Ready for Review

**Contract Summary:**
• **Product:** {final_terms['fabric_specifications']['fabric_type'] or 'Textile products'}
• **Quantity:** {final_terms['quantity'] or 'TBD':,} meters
• **Unit Price:** {currency} {final_terms['unit_price'] or 'TBD'}/meter
• **Delivery:** {final_terms['delivery_terms']['delivery_timeline'] or 'As agreed'}

**Quality Assessment:**
• **Completeness:** {validation_results['completeness_score']:.1%}
• **Legal Soundness:** {validation_results['legal_soundness']:.1%}
• **Risk Coverage:** {validation_results['risk_coverage']:.1%}
• **Overall Confidence:** {drafted_contract.confidence_score:.1%}

**Next Steps:**
{chr(10).join(f'• {action}' for action in recommended_actions[:3])}

**⚖️ Legal Review Required:** This contract requires legal review before execution."""
        
        # Step 9: Prepare state updates
        state_updates = {
            "drafted_contract": drafted_contract.model_dump(),
            "contract_terms": structured_terms.model_dump(),
            "contract_metadata": contract_metadata.model_dump(),
            "contract_id": contract_id,
            "contract_ready": True,
            "contract_confidence": drafted_contract.confidence_score,
            "requires_legal_review": drafted_contract.legal_review_required,
            "contract_generation_timestamp": datetime.now(),
            "next_step": "legal_review_required",
            "messages1": [assistant_message],
            "status": "contract_drafted"
        }
        
        print(f"✅ Contract drafting completed successfully!")
        print(f"📊 Contract confidence: {drafted_contract.confidence_score:.1%}")
        print(f"📋 Next step: {state_updates['next_step']}")
        
        return state_updates
            
    except Exception as e:
        error_message = f"❌ Error in contract drafting: {str(e)}"
        print(error_message)
        return {
            "error": str(e),
            "messages1": [error_message],
            "next_step": "handle_error",
            "status": "contract_drafting_error"
        }


def validate_contract_quality(drafted_contract: DraftedContract, context: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the quality and completeness of the drafted contract"""
    
    validation_results = {
        "completeness_score": 0.0,
        "legal_soundness": 0.0,
        "risk_coverage": 0.0,
        "issues": [],
        "recommendations": []
    }
    
    # Check completeness
    completeness_checks = [
        len(drafted_contract.preamble) > 100,
        len(drafted_contract.terms_and_conditions) > 500,
        drafted_contract.contract_terms_summary and len(drafted_contract.contract_terms_summary) > 100,
        len(drafted_contract.signature_block) > 50
    ]
    
    validation_results["completeness_score"] = sum(completeness_checks) / len(completeness_checks)
    
    # Check legal soundness
    legal_checks = [
        "governing law" in drafted_contract.terms_and_conditions.lower(),
        "dispute resolution" in drafted_contract.terms_and_conditions.lower(),
        "force majeure" in drafted_contract.terms_and_conditions.lower(),
        drafted_contract.legal_review_required
    ]
    
    validation_results["legal_soundness"] = sum(legal_checks) / len(legal_checks)
    
    # Check risk coverage
    risk_checks = [
        "insurance" in drafted_contract.terms_and_conditions.lower() or "liability" in drafted_contract.terms_and_conditions.lower(),
        "termination" in drafted_contract.terms_and_conditions.lower(),
        "quality" in drafted_contract.terms_and_conditions.lower()
    ]
    
    validation_results["risk_coverage"] = sum(risk_checks) / len(risk_checks)
    
    # Identify issues
    if validation_results["completeness_score"] < 0.8:
        validation_results["issues"].append("Contract may be missing key sections")
    
    if validation_results["legal_soundness"] < 0.7:
        validation_results["issues"].append("Contract may need additional legal provisions")
    
    if validation_results["risk_coverage"] < 0.6:
        validation_results["issues"].append("Risk mitigation clauses may be insufficient")
    
    return validation_results


def generate_contract_recommendations(drafted_contract: DraftedContract, context: Dict[str, Any], validation: Dict[str, Any]) -> List[str]:
    """Generate recommendations for contract execution and next steps"""
    
    recommendations = []
    
    # Always recommend legal review for contracts
    recommendations.append("Conduct comprehensive legal review with qualified counsel")
    
    # Compliance recommendations
    recommendations.append("Verify compliance with applicable trade regulations and standards")
    
    # Quality-based recommendations
    if validation["completeness_score"] < 0.9:
        recommendations.append("Review contract for completeness and add any missing standard clauses")
    
    if validation["risk_coverage"] < 0.8:
        recommendations.append("Strengthen risk mitigation and penalty clauses")
    
    # Context-based recommendations
    urgency = context['contract_metadata']['contract_urgency']
    if urgency == "urgent":
        recommendations.append("Expedite legal review due to urgent timeline requirements")
    
    agreement_confidence = context['contract_metadata']['agreement_confidence']
    if agreement_confidence < 0.8:
        recommendations.append("Consider additional negotiation rounds to improve terms clarity")
    
    # Standard recommendations
    recommendations.extend([
        "Obtain internal approvals from authorized signatories",
        "Schedule contract execution meeting with supplier",
        "Prepare contract management and monitoring procedures",
        "Set up delivery and payment milestone tracking"
    ])
    
    return recommendations[:8]  # Return top 8 recommendations


def determine_contract_complexity(final_terms: Dict[str, Any]) -> str:
    """Determine contract complexity level"""
    
    complexity_factors = 0
    
    # Value-based complexity
    total_value = final_terms.get('total_value', 0)
    if total_value > 1000000:  # > $1M
        complexity_factors += 2
    elif total_value > 100000:  # > $100K
        complexity_factors += 1
    
    # Terms complexity
    if len(final_terms.get('quality_standards', {})) > 3:
        complexity_factors += 1
    
    # Payment complexity
    payment_terms = final_terms.get('payment_terms', {})
    if payment_terms.get('advance_percentage', 30) != 30:  # Non-standard advance
        complexity_factors += 1
    
    if complexity_factors >= 4:
        return "high"
    elif complexity_factors >= 2:
        return "medium"
    else:
        return "low"