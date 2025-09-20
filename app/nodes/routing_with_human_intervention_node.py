from state import AgentState
from typing import Literal


# Improved routing function for better human intervention handling
def routing_with_human_intervention(state: AgentState) -> Literal[
    "draft_negotiation_message", 
    "initiate_contract", 
    "notify_user_and_suggest_next_steps",
    "provide_clarification",
    "schedule_follow_up",
]:
    """
    Enhanced routing with comprehensive human intervention support
    
    This function replaces evaluate_negotiation_status with improved logic
    for handling human interventions, escalations, and error recovery.
    """
    
    try:
        # Check for error conditions first
        # if state.get('error') or state.get('status') == 'error':
        #     return "handle_error"
        
        # Check for explicit escalation requirements
        # if state.get('escalation_required') or should_escalate_to_human(state):
        #     return "escalate_to_human"
        
        # Extract supplier intent for routing decisions
        supplier_intent_data = state.get('supplier_intent', {})
        intent = supplier_intent_data.get('intent')
        
        # if not intent:
        #     return "handle_error"
        
        # Route based on supplier intent with enhanced logic
        if intent == "accept":
            return "initiate_contract"
        
        # elif intent == "counteroffer":
            # Enhanced counteroffer routing with escalation checks
            # if should_escalate_to_human(state):
            #     return "escalate_to_human"
            # else:
            #     return "draft_negotiation_message"
        
        elif intent == "reject":
            return "notify_user_and_suggest_next_steps"
        
        elif intent == "clarification_request":
            return "provide_clarification"
        
        elif intent == "delay":
            return "schedule_follow_up"
        
        else:
            return "draft_negotiation_message"
    
    except Exception as e:
        print(f"Error in enhanced_routing_with_human_intervention: {e}")
        return "draft_negotiation_message" # Fallback action
    
# def should_escalate_to_human(state: AgentState) -> bool:
#     """
#     Determine if current state requires human escalation
    
#     Escalation triggers:
#     - Multiple negotiation rounds without progress (>= 4 rounds)
#     - Low confidence in AI analysis (< 0.6)
#     - High-risk factors detected (>= 3 risk factors)
#     - Complex terms requiring human judgment
#     - Explicit escalation flags in state

#     Args:
#         state: Current agent state
        
#     Returns:
#         bool: True if escalation is needed
#     """

#     # Check for explicit escalation requests
#     if state.get('escalation_required') or state.get('requires_human_review'):
#         return True
    
#     # Check negotiation round count
#     negotiation_history = state.get('negotiation_history', [])
#     if len(negotiation_history) >= 4:
#         return True
    
#     # Check confidence levels
#     supplier_intent = state.get('supplier_intent', {})
#     negotiation_analysis = state.get('negotiation_analysis', {})
    
#     intent_confidence = supplier_intent.get('confidence', 1.0)
#     analysis_confidence = negotiation_analysis.get('confidence_score', 1.0)
    
#     if intent_confidence < 0.6 or analysis_confidence < 0.6:
#         return True
    
#     # Check risk factors
#     risk_factors = negotiation_analysis.get('risk_factors', [])
#     if len(risk_factors) >= 3:
#         return True

#     # Check for complex terms
#     extracted_terms = state.get('extracted_terms', {})
#     if extracted_terms and has_complex_terms(extracted_terms):
#         return True
    
#     return False

# def has_complex_terms(extracted_terms: dict) -> bool:
#     """
#     Check if extracted terms contain complex conditions requiring human judgment
    
#     Args:
#         extracted_terms: Terms extracted from supplier response
        
#     Returns:
#         bool: True if terms are complex
#     """
    
#     complexity_indicators = [
#         # Multiple additional conditions
#         len(extracted_terms.get('additional_conditions', [])) >= 3,
        
#         # Complex payment terms
#         extracted_terms.get('new_payment_terms') and 
#         any(term in str(extracted_terms.get('new_payment_terms', '')).lower() 
#             for term in ['letter of credit', 'bank guarantee', 'escrow', 'installment']),
        
#         # Quality specifications modified
#         extracted_terms.get('quality_adjustments') is not None,
        
#         # Incoterms changed
#         extracted_terms.get('new_incoterms') is not None,
        
#         # Large quantity changes
#         extracted_terms.get('new_minimum_quantity') and 
#         extracted_terms.get('new_minimum_quantity') > 50000
#     ]
    
#     return any(complexity_indicators)