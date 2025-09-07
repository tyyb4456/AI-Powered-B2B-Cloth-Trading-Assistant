from typing import Literal, Optional, Dict, Any
from state import AgentState
import logging

# Configure logging for debugging conditional edge decisions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_negotiation_status(state: AgentState) -> Literal[
    "draft_negotiation_message", 
    "initiate_contract", 
    # "notify_user_of_failure",
    # "provide_clarification",
    # "schedule_follow_up",
    # "escalate_to_human",
    # "handle_error"
]:
    """
    Conditional Edge: evaluate_negotiation_status - Negotiation workflow traffic controller
    
    Purpose:
    - Examine the classified supplier intent from analyze_supplier_response
    - Route the workflow to appropriate next steps based on negotiation outcome
    - Control the negotiation loop continuation or termination
    - Maintain workflow coherence through state-preserved routing
    
    This edge function acts as the decision brain that determines whether:
    - The negotiation continues (loop back to draft_negotiation_message)
    - The negotiation succeeds (move to contract initiation)  
    - The negotiation fails (notify user of failure)
    - Additional actions are needed (clarification, follow-up, escalation)
    
    Args:
        state: Current agent state containing supplier_intent classification
    
    Returns:
        str: Name of the next node to execute in the workflow
    """
    
    try:
        # Step 1: Extract the supplier intent from state
        supplier_intent_data = state.get('supplier_intent', {})
        
        if not supplier_intent_data:
            logger.error("No supplier_intent found in state - routing to error handler")
            return "handle_error"
        
        # Extract the primary intent classification
        intent = supplier_intent_data.get('intent')
        intent_confidence = supplier_intent_data.get('confidence', 0.0)
        
        if not intent:
            logger.error("Intent classification missing - routing to error handler")
            return "handle_error"
        
        # Step 2: Extract additional context for enhanced routing decisions
        negotiation_round = get_negotiation_round(state)
        
        # Log the routing decision context
        logger.info(f"Evaluating negotiation status - Intent: {intent}, Confidence: {intent_confidence:.2f}, Round: {negotiation_round}")
        
        # Step 3: Core routing logic based on supplier intent
        
        if intent == "accept":
            """
            PATHWAY 1: SUCCESS - Supplier accepts terms
            
            Supplier has agreed to the proposed terms unconditionally.
            Negotiation has concluded successfully.
            
            Next Step: Move to contract formalization
            """
            logger.info("🎉 SUCCESS: Supplier accepted terms - routing to contract initiation")
            return "initiate_contract"
        
        elif intent == "counteroffer":
            """
            PATHWAY 2: CONTINUE NEGOTIATION - Supplier proposes new terms
            
            Supplier engaged with proposal but modified terms.
            Shows willingness to continue negotiating.
            
            State Preservation Critical: The draft_negotiation_message node will have
            access to complete history including the new counteroffer terms.
            
            Next Step: Loop back to message drafting with enriched context
            """
            
            # Enhanced routing logic for counteroffers
            # routing_decision = handle_counteroffer_routing(state, negotiation_round, intent_confidence)
            logger.info(f"📈 COUNTEROFFER: Continuing negotiation - routing to draft_negotiation_message")
            return 'draft_negotiation_message'
        
        # elif intent == "reject":
        #     """
        #     PATHWAY 3: FAILURE - Supplier definitively rejects
            
        #     Supplier declined offer without viable alternatives.
        #     Negotiation has failed for this supplier.
            
        #     Next Step: Handle failure scenario and suggest alternatives
        #     """
        #     logger.info("❌ REJECTION: Supplier rejected terms - routing to failure handler")
        #     return "notify_user_of_failure"
        
        # elif intent == "clarification_request":
        #     """
        #     PATHWAY 4: INFORMATION NEEDED - Supplier needs more details
            
        #     Supplier shows interest but requires additional information
        #     before proceeding with negotiation.
            
        #     Next Step: Provide requested clarification
        #     """
        #     logger.info("❓ CLARIFICATION: Supplier needs more info - routing to clarification handler")
        #     return "provide_clarification"
        
        # elif intent == "delay":
        #     """
        #     PATHWAY 5: WAIT REQUIRED - Supplier needs time
            
        #     Supplier interested but needs more time for decision.
        #     Shows continued engagement but requires patience.
            
        #     Next Step: Schedule appropriate follow-up
        #     """
        #     logger.info("⏰ DELAY: Supplier needs time - routing to follow-up scheduler")
        #     return "schedule_follow_up"
        
        # else:
        #     """
        #     PATHWAY 6: UNKNOWN/ERROR - Unrecognized intent
            
        #     Intent classification resulted in unexpected value.
        #     Fail-safe routing to prevent workflow breakdown.
            
        #     Next Step: Error handling with human escalation option
        #     """
        #     logger.error(f"⚠️ UNKNOWN INTENT: Unrecognized intent '{intent}' - routing to error handler")
        #     return "handle_error"
    
    except KeyError as e:
        logger.error(f"Missing required state key: {e} - routing to error handler")
        return "handle_error"
    
    except Exception as e:
        logger.error(f"Unexpected error in negotiation status evaluation: {e} - routing to error handler")
        return "handle_error"

def handle_counteroffer_routing(
    state: AgentState, 
    negotiation_round: int, 
    intent_confidence: float
) -> Literal["draft_negotiation_message", "escalate_to_human"]:
    """
    Enhanced routing logic for counteroffer scenarios
    
    Determines whether to continue automated negotiation or escalate
    based on negotiation complexity, round count, and confidence levels.
    
    Args:
        state: Current agent state
        negotiation_round: Current round number
        intent_confidence: Confidence in intent classification
    
    Returns:
        str: Routing decision for counteroffer handling
    """
    
    # Extract analysis confidence and risk factors
    analysis_data = state.get('negotiation_analysis', {})
    analysis_confidence = analysis_data.get('confidence_score', 1.0)
    risk_factors = analysis_data.get('risk_factors', [])
    
    # Check for escalation triggers
    
    # Trigger 1: Too many negotiation rounds (potential deadlock)
    if negotiation_round >= 5:
        logger.warning(f"Escalation trigger: Round {negotiation_round} - potential deadlock")
        return "escalate_to_human"
    
    # Trigger 2: Low confidence in analysis
    if intent_confidence < 0.6 or analysis_confidence < 0.6:
        logger.warning("Escalation trigger: Low confidence in analysis")
        return "escalate_to_human"
    
    # Trigger 3: High-risk factors identified
    if len(risk_factors) >= 3:
        logger.warning(f"Escalation trigger: Multiple risk factors - {len(risk_factors)} risks identified")
        return "escalate_to_human"
    
    # Trigger 4: Complex terms that may need human judgment
    extracted_terms = state.get('extracted_terms', {})
    if extracted_terms and has_complex_terms(extracted_terms):
        logger.warning("Escalation trigger: Complex terms detected")
        return "escalate_to_human"
    
    # Default: Continue automated negotiation
    return "draft_negotiation_message"

def has_complex_terms(extracted_terms: Dict[str, Any]) -> bool:
    """
    Identify if extracted terms contain complex conditions requiring human judgment
    
    Args:
        extracted_terms: Terms extracted from supplier response
    
    Returns:
        bool: True if terms are complex and may need human oversight
    """
    
    complexity_indicators = [
        # Multiple new conditions
        len(extracted_terms.get('additional_conditions', [])) >= 3,
        
        # Payment terms changed to complex arrangements
        extracted_terms.get('new_payment_terms') and 
        any(term in str(extracted_terms.get('new_payment_terms', '')).lower() 
            for term in ['letter of credit', 'bank guarantee', 'escrow', 'installment']),
        
        # Quality specifications modified
        extracted_terms.get('quality_adjustments') is not None,
        
        # Incoterms changed (significant logistics impact)
        extracted_terms.get('new_incoterms') is not None,
        
        # Large quantity adjustments (>50% change)
        extracted_terms.get('new_minimum_quantity') and 
        extracted_terms.get('new_minimum_quantity') > 50000  # Configurable threshold
    ]
    
    return any(complexity_indicators)

def get_negotiation_round(state: AgentState) -> int:
    """Extract current negotiation round from state"""
    
    negotiation_history = state.get('negotiation_history', [])
    if negotiation_history:
        return len(negotiation_history)
    
    # Fallback: Count negotiation-related messages
    messages = state.get('messages', [])
    negotiation_count = 0
    for message in messages:
        if isinstance(message, dict):
            content = message.get('content', '')
        elif isinstance(message, tuple) and len(message) == 2:
            content = message[1]
        else:
            content = str(message)
        
        if any(keyword in content.lower() for keyword in ['negotiate', 'counter', 'offer', 'terms']):
            negotiation_count += 1
    
    return max(1, negotiation_count // 2)  # Each round involves back-and-forth

def get_urgency_level(state: AgentState) -> str:
    """Extract urgency level from original request parameters"""
    
    extracted_params = state.get('extracted_parameters', {})
    return extracted_params.get('urgency_level', 'medium')

def validate_routing_decision(
    intent: str, 
    routing_decision: str, 
    state: AgentState
) -> tuple[bool, str]:
    """
    Validate that the routing decision is appropriate for the given intent and state
    
    Args:
        intent: Classified supplier intent
        routing_decision: Proposed next node
        state: Current state for context validation
    
    Returns:
        tuple: (is_valid, validation_message)
    """
    
    # Define valid routing combinations
    valid_routes = {
        "accept": ["initiate_contract"],
        "counteroffer": ["draft_negotiation_message", "escalate_to_human"],
        "reject": ["notify_user_of_failure"],
        "clarification_request": ["provide_clarification"],
        "delay": ["schedule_follow_up"]
    }
    
    expected_routes = valid_routes.get(intent, [])
    
    if routing_decision not in expected_routes:
        return False, f"Invalid route: {intent} should not route to {routing_decision}"
    
    # Additional state-based validations
    if routing_decision == "initiate_contract":
        # Ensure we have terms to create contract with
        if not state.get('extracted_terms') and not state.get('negotiation_history'):
            return False, "Cannot initiate contract without agreed terms"
    
    return True, "Routing decision validated"

# Utility function for debugging and monitoring
def log_routing_metrics(state: AgentState, routing_decision: str) -> None:
    """
    Log metrics about routing decisions for monitoring and optimization
    
    Args:
        state: Current agent state
        routing_decision: The routing decision made
    """
    
    metrics = {
        "routing_decision": routing_decision,
        "negotiation_round": get_negotiation_round(state),
        "intent": state.get('supplier_intent', {}).get('intent'),
        "intent_confidence": state.get('supplier_intent', {}).get('confidence'),
        "analysis_confidence": state.get('negotiation_analysis', {}).get('confidence_score'),
        "risk_factors_count": len(state.get('negotiation_analysis', {}).get('risk_factors', [])),
        "urgency_level": get_urgency_level(state)
    }
    
    logger.info(f"Routing metrics: {metrics}")

# Example usage and testing function
def test_routing_scenarios():
    """
    Test function to validate routing logic with various scenarios
    This would be used during development and testing
    """
    
    test_cases = [
        {
            "name": "Accept scenario",
            "state": {"supplier_intent": {"intent": "accept", "confidence": 0.9}},
            "expected": "initiate_contract"
        },
        {
            "name": "Counteroffer scenario",  
            "state": {"supplier_intent": {"intent": "counteroffer", "confidence": 0.8}},
            "expected": "draft_negotiation_message"
        },
        {
            "name": "Reject scenario",
            "state": {"supplier_intent": {"intent": "reject", "confidence": 0.9}},
            "expected": "notify_user_of_failure"
        },
        {
            "name": "High round escalation",
            "state": {
                "supplier_intent": {"intent": "counteroffer", "confidence": 0.8},
                "negotiation_history": [{"round": i} for i in range(6)]  # 6 rounds
            },
            "expected": "escalate_to_human"
        }
    ]
    
    for test_case in test_cases:
        result = evaluate_negotiation_status(test_case["state"])
        success = result == test_case["expected"]
        print(f"Test '{test_case['name']}': {'PASS' if success else 'FAIL'} - Got: {result}, Expected: {test_case['expected']}")

if __name__ == "__main__":
    # Run tests if module is executed directly
    test_routing_scenarios()