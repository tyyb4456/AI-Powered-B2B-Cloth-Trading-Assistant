from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
import uuid
from state import AgentState
from models.quotedetail import GeneratedQuote,SupplierQuoteOption, LogisticsCost
# from app.models.supplierdetail import Supplier
from dotenv import load_dotenv

load_dotenv()


# Initialize the model
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
structured_model = model.with_structured_output(GeneratedQuote)

def calculate_logistics_costs(supplier: Dict, destination: str, quantity: float, fabric_type: str) -> LogisticsCost:
    """
    Calculate comprehensive logistics costs for a supplier
    
    Args:
        supplier: Supplier dictionary with location and other details
        destination: Destination country/region
        quantity: Order quantity
        fabric_type: Type of fabric for customs classification
    
    Returns:
        LogisticsCost: Detailed breakdown of logistics expenses
    """
    
    supplier_country = supplier.get('country', supplier.get('location', 'Unknown'))
    
    # Base shipping rates per kg (simplified model - in production, use shipping APIs)
    shipping_rates = {
        ('China', 'Bangladesh'): 0.85,
        ('India', 'Bangladesh'): 0.45,
        ('Pakistan', 'Bangladesh'): 0.35,
        ('Turkey', 'Bangladesh'): 1.20,
        ('Vietnam', 'Bangladesh'): 0.75,
        # Default rates for unlisted routes
        'default_regional': 0.60,
        'default_international': 1.00
    }
    
    # Estimate fabric weight (kg per meter for different fabric types)
    fabric_weights = {
        'cotton': 0.15,
        'silk': 0.08,
        'denim': 0.45,
        'linen': 0.18,
        'polyester': 0.12,
        'wool': 0.25,
        'default': 0.20
    }
    
    # Calculate total weight
    fabric_key = next((key for key in fabric_weights.keys() if key in fabric_type.lower()), 'default')
    total_weight_kg = quantity * fabric_weights[fabric_key]
    
    # Get shipping rate
    route_key = (supplier_country, destination)
    if route_key in shipping_rates:
        rate_per_kg = shipping_rates[route_key]
    elif 'asia' in supplier_country.lower() and 'asia' in destination.lower():
        rate_per_kg = shipping_rates['default_regional']
    else:
        rate_per_kg = shipping_rates['default_international']
    
    # Calculate individual cost components
    shipping_cost = total_weight_kg * rate_per_kg
    insurance_cost = shipping_cost * 0.05  # 5% of shipping value
    
    # Customs duties (simplified - varies by country and trade agreements)
    material_value = supplier.get('avg_price', supplier.get('price_per_unit', 5.0)) * quantity
    customs_rate = 0.08 if 'organic' in fabric_type.lower() else 0.12  # Organic fabrics often have lower duties
    customs_duties = material_value * customs_rate
    
    # Handling fees (flat rate based on order size)
    if quantity > 50000:
        handling_fees = 500
    elif quantity > 20000:
        handling_fees = 300
    elif quantity > 5000:
        handling_fees = 150
    else:
        handling_fees = 75
    
    total_logistics = shipping_cost + insurance_cost + customs_duties + handling_fees
    
    return LogisticsCost(
        shipping_cost=round(shipping_cost, 2),
        insurance_cost=round(insurance_cost, 2),
        customs_duties=round(customs_duties, 2),
        handling_fees=round(handling_fees, 2),
        total_logistics=round(total_logistics, 2)
    )

def create_quote_generation_prompt():
    """Create the prompt template for quote generation"""
    
    system_prompt = """You are an expert B2B textile procurement specialist generating professional quotes.

Your task is to create a comprehensive, strategic quote document that demonstrates deep market knowledge and provides clear value to the client.

QUOTE STRUCTURE REQUIREMENTS:

1. **Client Summary**: Acknowledge their specific requirements in business language
2. **Supplier Analysis**: Present options as strategic choices, not just data dumps
3. **Market Intelligence**: Provide insights about current market conditions, pricing trends, and supply chain factors
4. **Strategic Recommendations**: Give clear guidance on the best choice and why
5. **Risk Assessment**: Highlight potential risks and mitigation strategies
6. **Negotiation Insights**: Suggest where there might be room for negotiation

BUSINESS TONE GUIDELINES:
- Professional but approachable
- Confident and knowledgeable
- Focus on value and strategic insights
- Acknowledge trade-offs honestly
- Position yourself as a trusted advisor, not just a price comparison tool

CRITICAL DETAILS TO INCLUDE:
- Clear total landed costs (material + logistics)
- Lead time comparisons with business impact
- Reliability scores with context
- Certification compliance status
- Payment term recommendations
- Delivery risk factors

Remember: This quote represents your expertise and market intelligence. Make it valuable enough that clients would want to work with you based on the insights provided, not just the prices."""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Generate a professional B2B textile quote for the following request:

CLIENT REQUEST:
- Fabric Type: {fabric_type}
- Quantity: {quantity} {unit}
- Quality Specs: {quality_specs}
- Certifications: {certifications}
- Destination: {destination}
- Timeline: {timeline}
- Urgency Level: {urgency}

SUPPLIER OPTIONS:
{supplier_options}

MARKET CONTEXT:
{market_insights}

Create a comprehensive quote that positions you as a knowledgeable trading partner.""")
    ])

# Initialize prompt template
quote_prompt = create_quote_generation_prompt()

def prepare_supplier_options_text(suppliers: List[Dict], logistics_costs: Dict[str, LogisticsCost]) -> str:
    """Format supplier data for prompt inclusion"""
    
    options_text = []
    
    for i, supplier in enumerate(suppliers[:4], 1):  # Max 4 options
        supplier_id = supplier.get('supplier_id', f'supplier_{i}')
        logistics = logistics_costs.get(supplier_id, LogisticsCost(
            shipping_cost=0, insurance_cost=0, customs_duties=0, handling_fees=0, total_logistics=0
        ))
        
        material_cost = supplier.get('avg_price', 5.0) * supplier.get('quantity', 1000)
        total_cost = material_cost + logistics.total_logistics
        
        option_text = f"""
Option {i}: {supplier.get('company_name', 'Unknown Supplier')}
- Location: {supplier.get('country', 'Unknown')}
- Unit Price: ${supplier.get('avg_price', 0):.2f}
- Material Cost: ${material_cost:,.2f}
- Logistics Cost: ${logistics.total_logistics:,.2f}
- Total Landed Cost: ${total_cost:,.2f}
- Lead Time: {supplier.get('lead_time_days', 'N/A')} days
- Reliability Score: {supplier.get('reliability_score', 'N/A')}/10
- Specialties: {supplier.get('specialties', 'N/A')}
- Certifications: {supplier.get('certifications', 'N/A')}
"""
        options_text.append(option_text)
    
    return "\n".join(options_text)

def generate_terms_and_conditions() -> str:
    """Generate standard terms and conditions for the quote"""
    
    return """
TERMS AND CONDITIONS:
1. Quote Validity: This quote is valid for 30 days from the date of issue
2. Payment Terms: 30% advance, 70% against shipping documents (negotiable)
3. Delivery Terms: FOB supplier's port unless otherwise specified
4. Quality Assurance: Pre-shipment inspection recommended for orders >$50,000
5. Force Majeure: Standard force majeure clauses apply
6. Currency: All prices quoted in USD unless specified otherwise
7. Minimum Order: Subject to supplier's minimum order quantity requirements
8. Pricing: Prices subject to confirmation at time of order placement

NOTE: This quote is based on current market conditions and supplier availability. 
Final pricing and terms subject to confirmation upon order placement.
"""

def calculate_estimated_savings(supplier_options: List[SupplierQuoteOption]) -> Optional[float]:
    """Calculate potential savings vs market average"""
    
    if len(supplier_options) < 2:
        return None
    
    # Use highest price as baseline
    max_cost = max(option.total_landed_cost for option in supplier_options)
    min_cost = min(option.total_landed_cost for option in supplier_options)
    
    savings_amount = max_cost - min_cost
    savings_percentage = (savings_amount / max_cost) * 100
    
    return round(savings_percentage, 1)

def generate_quote(state: AgentState) -> dict:
    """
    Node 5a: generate_quote - Professional quote generation with market intelligence
    
    Purpose:
    - Aggregate supplier data and calculate total landed costs
    - Generate comprehensive cost analysis including logistics
    - Create professional quote document with strategic insights
    - Provide market intelligence and negotiation recommendations
    
    Args:
        state: Current agent state with supplier results and extracted parameters
    
    Returns:
        dict: State updates with generated quote document and next routing
    """
    
    # try:
    # Extract data from state
    extracted_params = state.get('extracted_parameters', {})
    top_suppliers = state.get('top_suppliers', [])
    market_insights = state.get('market_insights', '')
    
    if not top_suppliers:
        return {
            "error": "No suppliers found for quote generation",
            "messages": [("assistant", "Unable to generate quote - no suppliers available")],
            "next_step": "handle_error",
            "status": "error"
        }
    
    # Extract key parameters
    fabric_details = extracted_params.get('fabric_details', {})
    logistics_details = extracted_params.get('logistics_details', {})
    
    fabric_type = fabric_details.get('type', 'fabric')
    quantity = fabric_details.get('quantity', 1000)
    unit = fabric_details.get('unit', 'meters')
    quality_specs = fabric_details.get('quality_specs', [])
    certifications = fabric_details.get('certifications', [])
    destination = logistics_details.get('destination', 'Unknown')
    timeline = logistics_details.get('timeline', 'Standard')
    urgency = extracted_params.get('urgency_level', 'medium')
    
    # Step 1: Calculate logistics costs for each supplier
    logistics_costs = {}
    for supplier in top_suppliers[:4]:  # Max 4 options for quote
        supplier_id = supplier.get('supplier_id', str(uuid.uuid4()))
        logistics_costs[supplier_id] = calculate_logistics_costs(
            supplier, destination, quantity, fabric_type
        )
    
    # Step 2: Create supplier quote options
    supplier_options = []
    for supplier in top_suppliers[:4]:
        supplier_id = supplier.get('supplier_id', str(uuid.uuid4()))
        logistics = logistics_costs[supplier_id]
        
        unit_price = supplier.get('avg_price', supplier.get('price_per_unit', 5.0))
        material_cost = unit_price * quantity
        total_landed_cost = material_cost + logistics.total_logistics
        
        # Generate advantages and risks for each supplier
        advantages = []
        risks = []
        
        # Analyze advantages
        if supplier.get('reliability_score', 5) >= 8:
            advantages.append("High reliability track record")
        if supplier.get('lead_time_days', 30) <= 20:
            advantages.append("Fast delivery capability")
        if unit_price <= min(s.get('avg_price', 10) for s in top_suppliers):
            advantages.append("Most competitive pricing")
        if 'organic' in supplier.get('certifications', []):
            advantages.append("Organic certification available")
        
        # Analyze risks
        if supplier.get('reliability_score', 5) < 7:
            risks.append("Lower reliability score - monitor closely")
        if supplier.get('lead_time_days', 30) > 45:
            risks.append("Extended lead time may impact project timeline")
        if supplier.get('min_order_qty', 0) > quantity:
            risks.append("Minimum order quantity exceeds request")
        
        supplier_option = SupplierQuoteOption(
            supplier_name=supplier.get('company_name', 'Unknown Supplier'),
            supplier_location=supplier.get('country', 'Unknown'),
            unit_price=round(unit_price, 2),
            material_cost=round(material_cost, 2),
            logistics_cost=logistics,
            total_landed_cost=round(total_landed_cost, 2),
            lead_time_days=supplier.get('lead_time_days', 30),
            reliability_score=supplier.get('reliability_score', 5.0),
            overall_score=supplier.get('overall_score', 50.0),
            key_advantages=advantages if advantages else ["Competitive option"],
            potential_risks=risks if risks else ["Standard supplier risks apply"]
        )
        supplier_options.append(supplier_option)
    
    # Step 3: Prepare data for LLM prompt
    supplier_options_text = prepare_supplier_options_text(top_suppliers, logistics_costs)
    
    formatted_prompt = quote_prompt.invoke({
        "fabric_type": fabric_type,
        "quantity": f"{quantity:,.0f}",
        "unit": unit,
        "quality_specs": ", ".join(quality_specs) if quality_specs else "Standard",
        "certifications": ", ".join(certifications) if certifications else "None specified",
        "destination": destination,
        "timeline": timeline,
        "urgency": urgency,
        "supplier_options": supplier_options_text,
        "market_insights": market_insights
    })
    
    # Step 4: Generate structured quote using LLM
    quote_result: GeneratedQuote = structured_model.invoke(formatted_prompt)
    
    # Override some fields with our calculated data
    quote_result.supplier_options = supplier_options
    quote_result.quote_id = f"QT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    quote_result.total_options_count = len(supplier_options)
    quote_result.estimated_savings = calculate_estimated_savings(supplier_options)
    quote_result.terms_and_conditions = generate_terms_and_conditions()
    
    # Step 5: Generate quote document (markdown format for now)
    quote_document = generate_quote_document(quote_result, extracted_params)

    print('-----------')
    print(quote_document)
    print('-----------')
    
    # Step 6: Create assistant response
    best_supplier = supplier_options[0] if supplier_options else None
    
    if best_supplier:
        assistant_message = f"""Quote generated successfully! 
        
Quote ID: {quote_result.quote_id}
Best Option: {best_supplier.supplier_name} - ${best_supplier.total_landed_cost:,.2f} total cost
Delivery: {best_supplier.lead_time_days} days
Reliability: {best_supplier.reliability_score}/10

{quote_result.strategic_analysis.recommendation_reasoning}

The complete quote document has been prepared with {len(supplier_options)} supplier options."""
    else:
        assistant_message = "Quote generated but no suppliers meet all requirements."
    
    # Step 7: Return state updates
    return {
        "generated_quote": quote_result.model_dump(),
        "quote_document": quote_document,
        "quote_id": quote_result.quote_id,
        "supplier_options": [option.model_dump() for option in supplier_options],
        "estimated_savings": quote_result.estimated_savings,
        "messages": [{"role": "assistant", "content": assistant_message}],
        "next_step": "send_output_to_user",
        "status": "quote_generated"
    }
        
    # except Exception as e:
    #     error_message = f"Error generating quote: {str(e)}"
    #     return {
    #         "error": str(e),
    #         "messages": [{"role": "assistant", "content": error_message}],
    #         "next_step": "handle_error",
    #         "status": "error"
    #     }
    

def generate_quote_document(quote: GeneratedQuote, extracted_params: Dict) -> str:
    """
    Generate formatted quote document in markdown
    
    Args:
        quote: Generated quote structure
        extracted_params: Original extracted parameters
    
    Returns:
        str: Formatted quote document in markdown
    """
    
    fabric_details = extracted_params.get('fabric_details', {})
    logistics_details = extracted_params.get('logistics_details', {})
    
    # Calculate validity date
    validity_date = (datetime.now() + timedelta(days=quote.validity_days)).strftime("%B %d, %Y")
    
    document = f"""
# TEXTILE PROCUREMENT QUOTE

**Quote ID:** {quote.quote_id}  
**Date:** {quote.quote_date.strftime("%B %d, %Y")}  
**Valid Until:** {validity_date}

---

## CLIENT REQUIREMENTS SUMMARY

{quote.client_summary}

**Specifications:**
- **Fabric Type:** {fabric_details.get('type', 'Not specified')}
- **Quantity:** {fabric_details.get('quantity', 'Not specified'):,.0f} {fabric_details.get('unit', 'units')}
- **Quality Requirements:** {', '.join(fabric_details.get('quality_specs', [])) or 'Standard'}
- **Certifications:** {', '.join(fabric_details.get('certifications', [])) or 'None specified'}
- **Delivery Destination:** {logistics_details.get('destination', 'Not specified')}
- **Timeline:** {logistics_details.get('timeline', 'Standard')}

---

## SUPPLIER OPTIONS & PRICING

"""
    
    # Add supplier options table
    for i, option in enumerate(quote.supplier_options, 1):
        document += f"""
### Option {i}: {option.supplier_name}
**Location:** {option.supplier_location}

| Component | Cost |
|-----------|------|
| Material Cost ({option.unit_price}/unit) | ${option.material_cost:,.2f} |
| Shipping & Freight | ${option.logistics_cost.shipping_cost:,.2f} |
| Insurance | ${option.logistics_cost.insurance_cost:,.2f} |
| Customs & Duties | ${option.logistics_cost.customs_duties:,.2f} |
| Handling Fees | ${option.logistics_cost.handling_fees:,.2f} |
| **TOTAL LANDED COST** | **${option.total_landed_cost:,.2f}** |

**Delivery:** {option.lead_time_days} days | **Reliability:** {option.reliability_score}/10 | **Score:** {option.overall_score:.1f}/100

**Key Advantages:**
{chr(10).join(f"- {advantage}" for advantage in option.key_advantages)}

**Considerations:**
{chr(10).join(f"- {risk}" for risk in option.potential_risks)}

---
"""
    
    # Add strategic analysis
    document += f"""
## MARKET ANALYSIS & RECOMMENDATIONS

### Our Recommendation: {quote.strategic_analysis.recommended_supplier}

{quote.strategic_analysis.recommendation_reasoning}

### Market Assessment
{quote.strategic_analysis.market_assessment}

### Risk Factors to Consider
{chr(10).join(f"- {risk}" for risk in quote.strategic_analysis.risk_factors)}

### Negotiation Opportunities
{chr(10).join(f"- {opportunity}" for opportunity in quote.strategic_analysis.negotiation_opportunities)}

"""
    
    if quote.estimated_savings:
        document += f"""
### Potential Savings
By choosing our recommended option, you could save up to **{quote.estimated_savings}%** compared to the highest-cost alternative.

"""
    
    # Add alternative strategies if needed
    if quote.strategic_analysis.alternative_strategies:
        document += f"""
### Alternative Strategies
{chr(10).join(f"- {strategy}" for strategy in quote.strategic_analysis.alternative_strategies)}

"""
    
    # Add terms and conditions
    document += f"""
---

## TERMS AND CONDITIONS

{quote.terms_and_conditions}

---

*This quote is generated by AI-powered market analysis. All pricing and terms subject to final confirmation with suppliers.*
"""
    
    return document

def validate_quote_data(quote: GeneratedQuote) -> bool:
    """Validate the generated quote for completeness and accuracy"""
    
    # Check if we have supplier options
    if not quote.supplier_options:
        return False
    
    # Validate each supplier option
    for option in quote.supplier_options:
        if option.total_landed_cost <= 0:
            return False
        if option.lead_time_days <= 0:
            return False
        if not option.supplier_name or option.supplier_name.strip() == "":
            return False
    
    # Check if strategic analysis is present
    if not quote.strategic_analysis.recommended_supplier:
        return False
    
    if not quote.strategic_analysis.recommendation_reasoning:
        return False
    
    return True

def get_quote_summary(quote: GeneratedQuote) -> Dict[str, Any]:
    """Generate a summary of the quote for quick reference"""
    
    if not quote.supplier_options:
        return {"error": "No supplier options available"}
    
    best_option = quote.supplier_options[0]
    
    return {
        "quote_id": quote.quote_id,
        "total_options": len(quote.supplier_options),
        "best_supplier": best_option.supplier_name,
        "best_price": best_option.total_landed_cost,
        "best_lead_time": best_option.lead_time_days,
        "estimated_savings": quote.estimated_savings,
        "validity_date": (quote.quote_date + timedelta(days=quote.validity_days)).isoformat(),
        "confidence_level": "high" if len(quote.supplier_options) >= 3 else "medium"
    }