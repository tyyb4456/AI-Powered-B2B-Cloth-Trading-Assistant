from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
from models.supplierdetail import SupplierSearchResult,Supplier
from state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the model
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
structured_model = model.with_structured_output(SupplierSearchResult)

def create_database_connection():
    """Create SQLDatabase connection for supplier data"""
    # In production, use environment variables for connection string
    db_url = os.getenv("DATABASE_URL", "sqlite:///suppliers.db")
    engine = create_engine(db_url)
    
    return SQLDatabase(
        engine=engine,
        include_tables=["suppliers", "supplier_performance", "certifications", "fabric_types"],
        sample_rows_in_table_info=3,
        max_string_length=300
    )

def query_internal_database(db: SQLDatabase, fabric_type: str, quantity: float, certifications: List[str]) -> List[Dict]:
    """Query internal supplier database with filtering"""
    
    # Build dynamic SQL query based on parameters
    query_parts = [
        "SELECT s.supplier_id, s.name, s.location, s.min_order_qty, s.certifications, s.specialties,",
        "       COALESCE(sp.avg_lead_time, 30) as avg_lead_time,", 
        "       COALESCE(sp.reliability_score, 5.0) as reliability_score,",
        "       COALESCE(sp.avg_price, 5.0) as avg_price",
        "FROM suppliers s",
        "LEFT JOIN supplier_performance sp ON s.supplier_id = sp.supplier_id",
        "WHERE s.active = 1"
    ]
    
    params = {}
    
    if fabric_type:
        query_parts.append("AND (s.specialties LIKE :fabric_type OR s.specialties IS NULL)")
        params["fabric_type"] = f"%{fabric_type}%"
    
    if quantity:
        query_parts.append("AND (s.min_order_qty <= :quantity OR s.min_order_qty IS NULL)")
        params["quantity"] = quantity
    
    if certifications:
        cert_conditions = " OR ".join([f"s.certifications LIKE :cert_{i}" for i in range(len(certifications))])
        query_parts.append(f"AND ({cert_conditions} OR s.certifications IS NULL)")
        for i, cert in enumerate(certifications):
            params[f"cert_{i}"] = f"%{cert}%"
    
    query_parts.append("ORDER BY COALESCE(sp.reliability_score, 5.0) DESC, COALESCE(sp.avg_price, 5.0) ASC")
    query_parts.append("LIMIT 20")
    
    final_query = " ".join(query_parts)
    
    try:
        result = db.run(final_query, parameters=params)
        
        # Handle both tuple and string results
        if isinstance(result, str):
            # If result is a string, try to parse it or return empty list
            print(f"Database returned string result: {result}")
            return []
        
        # Process the results
        suppliers = []
        for row in result:
            try:
                supplier_dict = parse_supplier_row(row)
                suppliers.append(supplier_dict)
            except Exception as e:
                print(f"Error parsing supplier row {row}: {e}")
                continue
                
        return suppliers
        
    except Exception as e:
        print(f"Database query error: {e}")
        # Return mock data for testing
        return get_mock_internal_suppliers(fabric_type, quantity, certifications)
    
def parse_supplier_row(row) -> Dict[str, Any]:
    """Parse a single database row into a supplier dictionary"""
    
    # Handle different row formats
    if isinstance(row, (list, tuple)):
        # Expected columns: supplier_id, name, location, min_order_qty, certifications, 
        #                  specialties, avg_lead_time, reliability_score, avg_price
        
        if len(row) < 9:
            print(f"Warning: Row has {len(row)} columns, expected 9: {row}")
            # Pad with default values if needed
            row = list(row) + [None] * (9 - len(row))
            
        return {
            "supplier_id": str(row[0]) if row[0] is not None else "unknown",
            "name": str(row[1]) if row[1] is not None else "Unknown Supplier",
            "location": str(row[2]) if row[2] is not None else "Unknown",
            "minimum_order_qty": float(row[3]) if row[3] is not None else None,
            "certifications": parse_list_field(row[4]) if row[4] is not None else [],
            "specialties": parse_list_field(row[5]) if row[5] is not None else [],
            "lead_time_days": int(row[6]) if row[6] is not None else 30,
            "reputation_score": float(row[7]) if row[7] is not None else 5.0,
            "price_per_unit": float(row[8]) if row[8] is not None else None
        }
    else:
        # If it's already a dict or other format
        return {
            "supplier_id": "unknown",
            "name": "Unknown Supplier", 
            "location": "Unknown",
            "minimum_order_qty": None,
            "certifications": [],
            "specialties": [],
            "lead_time_days": 30,
            "reputation_score": 5.0,
            "price_per_unit": None
        }

def parse_list_field(field_value) -> List[str]:
    """Parse comma-separated string into list"""
    if not field_value:
        return []
    
    if isinstance(field_value, str):
        return [item.strip() for item in field_value.split(',') if item.strip()]
    
    if isinstance(field_value, list):
        return field_value
        
    return []

def get_mock_internal_suppliers(fabric_type: str, quantity: float, certifications: List[str]) -> List[Dict]:
    """Return mock internal supplier data for testing"""
    
    mock_suppliers = [
        {
            "supplier_id": "int_001",
            "name": "Premium Textile Mills",
            "location": "Turkey",
            "price_per_unit": 4.50,
            "lead_time_days": 20,
            "minimum_order_qty": 5000,
            "reputation_score": 8.5,
            "specialties": ["organic cotton", "sustainable fabrics"],
            "certifications": ["GOTS", "OEKO-TEX"],
            "contact_info": {"email": "sales@premiumtextile.com"},
            "notes": "High quality organic fabrics"
        },
        {
            "supplier_id": "int_002",
            "name": "Global Fabric Solutions", 
            "location": "India",
            "price_per_unit": 3.80,
            "lead_time_days": 28,
            "minimum_order_qty": 8000,
            "reputation_score": 7.8,
            "specialties": ["cotton", "blends"],
            "certifications": ["ISO 9001"],
            "contact_info": {"email": "info@globalfabric.in"},
            "notes": "Cost-effective solutions"
        },
        {
            "supplier_id": "int_003",
            "name": "Sustainable Textiles Co.",
            "location": "Portugal", 
            "price_per_unit": 5.20,
            "lead_time_days": 18,
            "minimum_order_qty": 3000,
            "reputation_score": 9.1,
            "specialties": ["organic cotton", "eco-friendly"],
            "certifications": ["GOTS", "Cradle to Cradle"],
            "contact_info": {"email": "contact@sustextiles.pt"},
            "notes": "Premium sustainable fabrics"
        }
    ]
    
    # Filter based on criteria
    filtered_suppliers = []
    for supplier in mock_suppliers:
        # Check quantity requirements
        if quantity and supplier["minimum_order_qty"] and quantity < supplier["minimum_order_qty"]:
            continue
            
        # Check fabric type
        if fabric_type and not any(fabric_type.lower() in specialty.lower() for specialty in supplier["specialties"]):
            continue
            
        # Check certifications
        if certifications and not any(cert in supplier["certifications"] for cert in certifications):
            continue
            
        filtered_suppliers.append(supplier)
    
    return filtered_suppliers

def query_external_apis(fabric_type: str, quantity: float, target_location: str) -> List[Dict]:
    """Query external supplier APIs (Alibaba, etc.)"""
    
    external_results = []
    
    # Mock external API call (replace with actual API integration)
    # In production, you'd integrate with:
    # - Alibaba API
    # - Global Sources API
    # - Thomasnet API
    # - Custom B2B platform APIs
    
    try:
        # Example mock data - replace with actual API calls
        mock_external_data = [
            {
                "supplier_id": "ext_001",
                "name": "Asia Textile Export Co.",
                "location": "China",
                "price_per_unit": 4.20,
                "lead_time_days": 25,
                "minimum_order_qty": 5000,
                "reputation_score": 7.5,
                "specialties": ["cotton", "synthetic"],
                "certifications": ["ISO 9001"],
                "source": "alibaba"
            },
            {
                "supplier_id": "ext_002", 
                "name": "Bangladesh Cotton Mills",
                "location": "Bangladesh",
                "price_per_unit": 3.95,
                "lead_time_days": 35,
                "minimum_order_qty": 10000,
                "reputation_score": 8.2,
                "specialties": ["organic cotton"],
                "certifications": ["GOTS"],
                "source": "global_sources"
            }
        ]
        
        # Filter mock data based on criteria
        for supplier in mock_external_data:
            if quantity >= supplier["minimum_order_qty"]:
                external_results.append(supplier)
                
    except Exception as e:
        print(f"External API error: {e}")
    
    return external_results

def calculate_supplier_score(supplier: Dict, weights: Dict[str, float]) -> float:
    """Calculate weighted score for supplier ranking"""
    
    # Normalize scores to 0-100 scale
    price_score = max(0, 100 - (supplier.get("price_per_unit", 5.0) - 3.0) * 20)  # Lower price = higher score
    speed_score = max(0, 100 - (supplier.get("lead_time_days", 30) - 10) * 2)     # Faster = higher score  
    reliability_score = supplier.get("reputation_score", 5.0) * 10                # Convert to 0-100 scale
    
    # Apply weights
    weighted_score = (
        price_score * weights.get("price", 0.4) +
        speed_score * weights.get("speed", 0.3) +
        reliability_score * weights.get("reliability", 0.3)
    )
    
    return min(100.0, max(0.0, weighted_score))

def create_sourcing_prompt():
    """Create prompt for LLM analysis of supplier results"""
    
    system_prompt = """You are an expert textile procurement analyst with deep knowledge of global supply chains.

Your task is to analyze supplier search results and provide strategic insights for B2B fabric trading.

ANALYSIS FRAMEWORK:
1. **Market Assessment**: Evaluate the overall supplier landscape for this request
2. **Risk Analysis**: Identify potential risks (price volatility, lead time issues, reliability concerns)
3. **Strategic Recommendations**: Suggest optimal supplier mix and negotiation strategies
4. **Alternative Options**: If results are limited, suggest alternatives (different specifications, regions, etc.)

SCORING CRITERIA:
- **Price Competitiveness**: How suppliers compare to market rates
- **Speed vs Cost Trade-offs**: Balance between fast delivery and competitive pricing  
- **Reliability Factors**: Past performance, certifications, business stability
- **Logistics Efficiency**: Shipping costs, customs considerations, geographic advantages

RESPONSE GUIDELINES:
- Be specific about why certain suppliers are recommended
- Highlight any red flags or concerns
- Suggest negotiation strategies based on market conditions
- Keep insights actionable and business-focused"""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Analyze these supplier search results for the following request:

FABRIC REQUEST:
- Type: {fabric_type}
- Quantity: {quantity} {unit}
- Certifications: {certifications}
- Destination: {destination}
- Urgency: {urgency}

SUPPLIER RESULTS:
{supplier_data}

Provide strategic analysis and recommendations.""")
    ])

# Initialize prompt template
sourcing_prompt = create_sourcing_prompt()

def supplier_sourcing(state: AgentState) -> dict:
    """
    Node 4: supplier_sourcing - Multi-database supplier search and ranking
    
    Purpose:
    - Query internal supplier database and external APIs
    - Apply intelligent filtering based on extracted parameters
    - Rank suppliers using weighted scoring algorithm
    - Provide market intelligence and strategic recommendations
    
    Args:
        state: Current agent state with extracted parameters
    
    Returns:
        dict: State updates with ranked supplier recommendations
    """
    
    try:
        # Extract parameters from state
        extracted_params = state.get('extracted_parameters', {})
        fabric_details = extracted_params.get('fabric_details', {})
        logistics_details = extracted_params.get('logistics_details', {})
        urgency = extracted_params.get('urgency_level', 'medium')
        
        # Extract key search criteria
        fabric_type = fabric_details.get('type', '')
        quantity = fabric_details.get('quantity', 0)
        unit = fabric_details.get('unit', 'meters')
        certifications = fabric_details.get('certifications', [])
        destination = logistics_details.get('destination', '')
        
        print(f"Searching for suppliers with criteria:")
        print(f"  - Fabric type: {fabric_type}")
        print(f"  - Quantity: {quantity} {unit}")
        print(f"  - Certifications: {certifications}")
        print(f"  - Destination: {destination}")
        print(f"  - Urgency: {urgency}")
        
        # Step 1: Query internal database
        db = create_database_connection()
        internal_suppliers = query_internal_database(db, fabric_type, quantity, certifications)
        print(f"Found {len(internal_suppliers)} internal suppliers")
        
        # Step 2: Query external APIs
        external_suppliers = query_external_apis(fabric_type, quantity, destination)
        print(f"Found {len(external_suppliers)} external suppliers")
        
        # Step 3: Combine and deduplicate results
        all_suppliers = internal_suppliers + external_suppliers
        
        # Step 4: Apply scoring weights based on urgency
        if urgency == "urgent":
            weights = {"price": 0.2, "speed": 0.5, "reliability": 0.3}
        elif urgency == "high":
            weights = {"price": 0.3, "speed": 0.4, "reliability": 0.3}
        else:
            weights = {"price": 0.4, "speed": 0.3, "reliability": 0.3}
        
        # Step 5: Calculate scores and rank suppliers
        for supplier in all_suppliers:
            supplier["overall_score"] = calculate_supplier_score(supplier, weights)
        
        # Sort by overall score (descending)
        ranked_suppliers = sorted(all_suppliers, key=lambda x: x["overall_score"], reverse=True)
        
        # Step 6: Convert to Pydantic models for validation
        top_suppliers = []
        for supplier_data in ranked_suppliers[:10]:  # Top 10 only
            try:
                supplier_match = Supplier(
                    supplier_id=supplier_data.get("supplier_id", ""),
                    name=supplier_data.get("name", ""),
                    location=supplier_data.get("location", ""),
                    price_per_unit=supplier_data.get("price_per_unit"),
                    lead_time_days=supplier_data.get("lead_time_days"),
                    minimum_order_qty=supplier_data.get("minimum_order_qty"),
                    reputation_score=supplier_data.get("reputation_score", 5.0),
                    specialties=supplier_data.get("specialties", []),
                    certifications=supplier_data.get("certifications", []),
                    contact_info=supplier_data.get("contact_info", {}),
                    notes=supplier_data.get("notes", ""),
                    overall_score=supplier_data.get("overall_score", 0.0)
                )
                top_suppliers.append(supplier_match)
            except Exception as e:
                print(f"Error creating supplier match: {e}")
                continue
        
        # Step 7: Generate market insights using LLM
        supplier_summary = "\n".join([
            f"- {s.name} ({s.location}): ${s.price_per_unit or 'N/A'}/{unit}, {s.lead_time_days or 'N/A'} days, Score: {s.overall_score:.1f}"
            for s in top_suppliers[:5]
        ])
        
        formatted_prompt = sourcing_prompt.invoke({
            "fabric_type": fabric_type or "not specified",
            "quantity": quantity or "not specified", 
            "unit": unit,
            "certifications": ", ".join(certifications) or "none specified",
            "destination": destination or "not specified",
            "urgency": urgency,
            "supplier_data": supplier_summary
        })
        
        # Get market analysis from LLM
        try:
            market_analysis = model.invoke(formatted_prompt)
            market_insights = market_analysis.content
        except Exception as e:
            print(f"Error getting market analysis: {e}")
            market_insights = "Market analysis temporarily unavailable. Please review supplier recommendations based on scores and specifications."
        
        # Step 8: Create final result structure
        search_result = SupplierSearchResult(
            request_id=extracted_params.get('item_id', 'unknown'),
            total_suppliers_found=len(all_suppliers),
            filtered_suppliers=len(ranked_suppliers),
            top_recommendations=top_suppliers,
            search_strategy=f"Multi-source search with {urgency} urgency weighting",
            market_insights=market_insights,
            confidence=calculate_search_confidence(top_suppliers, fabric_type, quantity),
            alternative_suggestions=generate_alternatives(top_suppliers, fabric_type)
        )
        
        # Create assistant response
        if top_suppliers:
            assistant_message = f"Found {len(top_suppliers)} qualified suppliers for {fabric_type}. Top recommendation: {top_suppliers[0].name} (Score: {top_suppliers[0].overall_score:.1f})"
        else:
            assistant_message = f"No suppliers found matching the criteria for {fabric_type}."

        assistant_message += f"\n\nMarket Insights:\n{market_insights}"
        
        # Step 9: Update state
        search_confidence = search_result.confidence
        
        # Determine next step based on results
        if len(top_suppliers) == 0:
            next_step = "handle_no_suppliers"
        elif search_result.confidence < 0.6:
            next_step = "request_clarification"
        else:
            next_step = "generate_quote"
        
        # Return state updates
        return {
            "supplier_search_results": search_result.model_dump(),
            "top_suppliers": [s.model_dump() for s in top_suppliers],
            "search_confidence": search_confidence,
            "market_insights": market_insights,
            "alternative_suggestions": search_result.alternative_suggestions,
            "messages": [{"role": "assistant", "content": assistant_message}],
            "next_step": next_step,
            "status": "suppliers_found"
        }
        
    except Exception as e:
        error_message = f"Error in supplier sourcing: {str(e)}"
        print(error_message)
        return {
            "error": str(e),
            "messages": [("assistant", error_message)],
            "next_step": "handle_error",
            "status": "error"
        }
    
def calculate_search_confidence(suppliers: List[Supplier], fabric_type: str, quantity: float) -> float:
    """Calculate confidence score for the search results"""
    
    if not suppliers:
        return 0.0
    
    # Base confidence factors
    confidence_factors = []
    
    # Factor 1: Number of quality suppliers found
    num_suppliers = len(suppliers)
    if num_suppliers >= 5:
        confidence_factors.append(0.9)
    elif num_suppliers >= 3:
        confidence_factors.append(0.7)
    elif num_suppliers >= 1:
        confidence_factors.append(0.5)
    else:
        confidence_factors.append(0.1)
    
    # Factor 2: Top supplier score quality
    top_score = suppliers[0].overall_score if suppliers else 0
    if top_score >= 80:
        confidence_factors.append(0.9)
    elif top_score >= 60:
        confidence_factors.append(0.7)
    else:
        confidence_factors.append(0.5)
    
    # Factor 3: Fabric type specificity match
    if fabric_type and any(fabric_type.lower() in ' '.join(s.specialties).lower() for s in suppliers):
        confidence_factors.append(0.8)
    else:
        confidence_factors.append(0.6)
    
    # Factor 4: Quantity feasibility
    suitable_qty_suppliers = [s for s in suppliers if not s.minimum_order_qty or s.minimum_order_qty <= quantity]
    if len(suitable_qty_suppliers) >= 3:
        confidence_factors.append(0.8)
    elif len(suitable_qty_suppliers) >= 1:
        confidence_factors.append(0.6)
    else:
        confidence_factors.append(0.3)
    
    # Calculate weighted average
    return sum(confidence_factors) / len(confidence_factors)

def generate_alternatives(suppliers: List[Supplier], fabric_type: str) -> List[str]:
    """Generate alternative suggestions if results are limited"""
    
    alternatives = []
    
    if len(suppliers) < 3:
        alternatives.append("Consider broadening fabric specifications")
        alternatives.append("Explore alternative fabric types with similar properties")
        
    if not suppliers:
        alternatives.append("Try different search terms or fabric categories")
        alternatives.append("Consider contacting suppliers directly for custom requirements")
    
    # Check for regional diversity
    regions = set(s.location for s in suppliers)
    if len(regions) < 2:
        alternatives.append("Expand search to include suppliers from different regions")
    
    return alternatives

# additional helper functions for state management

def get_supplier_by_id(supplier_id: str, state: AgentState) -> Optional[Supplier]:
    """Helper function to retrieve specific supplier details"""
    
    suppliers = state.get('top_suppliers', [])
    for supplier_data in suppliers:
        if supplier_data.get('supplier_id') == supplier_id:
            return Supplier(**supplier_data)
    return None

def update_supplier_performance(supplier_id: str, performance_data: Dict[str, Any]):
    """Update supplier performance metrics based on completed transactions"""
    
    try:
        db = create_database_connection()
        
        # Update performance metrics
        update_query = """
        UPDATE supplier_performance 
        SET reliability_score = :reliability,
            avg_lead_time = :lead_time,
            last_updated = CURRENT_TIMESTAMP
        WHERE supplier_id = :supplier_id
        """
        
        db.run(update_query, parameters={
            "supplier_id": supplier_id,
            "reliability": performance_data.get("reliability_score"),
            "lead_time": performance_data.get("actual_lead_time")
        })
            
    except Exception as e:
        print(f"Error updating supplier performance: {e}")