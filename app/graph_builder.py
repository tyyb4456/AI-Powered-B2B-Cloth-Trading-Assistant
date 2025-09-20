import os
import uuid
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from nodes.receive_input_node import receive_input
from nodes.classify_intent_node import classify_intent, branch_route
from nodes.extract_parameters_node import extract_parameters

from nodes.supplier_sourcing_node import supplier_sourcing
from nodes.generate_quote_node import generate_quote
from nodes.send_output_to_user_node import send_output_to_user, tools_list

from nodes.draft_negotiation_message_node import draft_negotiation_message
from nodes.share_draft_message_node import share_draft_message, custom_tool_node
from nodes.analyze_supplier_response_node import analyze_supplier_response

from nodes.routing_with_human_intervention_node import routing_with_human_intervention
from nodes.initiate_contract_node import initiate_contract

from nodes.provide_clarification_node import provide_clarification
from nodes.schedule_follow_up_node import schedule_follow_up
from nodes.notify_user_and_suggest_next_steps_node import notify_user_and_suggest_next_steps

from state import AgentState

# Configuration
class Config:
    """Configuration management for the negotiation graph"""
    DEFAULT_THREAD_ID = os.getenv("GRAPH_THREAD_ID", str(uuid.uuid4()))
    ENABLE_DEBUG = os.getenv("GRAPH_DEBUG", "false").lower() == "true"
    DEFAULT_NEGOTIATION_INPUT = os.getenv("DEFAULT_NEGOTIATION_INPUT", '''
        Can you improve the lead time from 60 to 45 days?,
        The quoted price is too high, can we discuss?,
        Need better payment terms than 100% advance,
        Your competitor quoted 10% lower, can you match?
    ''')
    DEFAULT_GET_QUOTE_INPUT = os.getenv("DEFAULT_GET_QUOTE_INPUT" , '''
            I need a quote for 5,000 meters of organic cotton canvas,
            What's your price for 10k yards of denim fabric?,
            Cost for cotton poplin 120gsm, GOTS certified?,
            Price check: polyester blend, 50/50, 150gsm, quantity 20,000m
''')

def route_from_draft_message(state: AgentState) -> str:
    """Route based on message content and state"""
    # Priority 1: If we have supplier response, go directly to analysis
    if state.get('supplier_response'):
        return 'analyze_supplier_response'
    
    # Priority 2: Check if we have messages and if the last message has tool calls
    if "msgs" in state and state["msgs"]:
        last_message = state["msgs"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools_b"
    
    return END


graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node('receive_input', receive_input)
graph_builder.add_node('classify_intent', classify_intent)
graph_builder.add_node('extract_parameters', extract_parameters)

# branch a nodes

graph_builder.add_node('supplier_sourcing' , supplier_sourcing)
graph_builder.add_node('generate_quote' , generate_quote)
graph_builder.add_node('send_output_to_user' , send_output_to_user)

tool_node = ToolNode(tools_list)
graph_builder.add_node("tools", tool_node) # branch a tools

# branch b nodes

graph_builder.add_node('draft_negotiation_message', draft_negotiation_message)
graph_builder.add_node('share_draft_message', share_draft_message)
graph_builder.add_node('analyze_supplier_response', analyze_supplier_response)


graph_builder.add_node("tools_b", custom_tool_node) # branch b tools

graph_builder.add_node('initiate_contract' , initiate_contract)

graph_builder.add_node('provide_clarification', provide_clarification)
graph_builder.add_node('schedule_follow_up', schedule_follow_up)
graph_builder.add_node('notify_user_and_suggest_next_steps', notify_user_and_suggest_next_steps)



# Add sequential edges for main workflow

graph_builder.add_edge(START, 'receive_input')
graph_builder.add_edge('receive_input', 'classify_intent')
graph_builder.add_edge('classify_intent', 'extract_parameters')

graph_builder.add_conditional_edges(
    'extract_parameters',
    branch_route
)

# branch a edges

graph_builder.add_edge('supplier_sourcing' , 'generate_quote')
graph_builder.add_edge('generate_quote', 'send_output_to_user')
graph_builder.add_conditional_edges("send_output_to_user", tools_condition)
graph_builder.add_edge("tools", "send_output_to_user")

# branch b edges

graph_builder.add_edge('draft_negotiation_message', 'share_draft_message')

graph_builder.add_conditional_edges(
    'share_draft_message',
    route_from_draft_message,
    {
        "tools_b": "tools_b",
        'analyze_supplier_response': 'analyze_supplier_response',
        END: END
    }
)

graph_builder.add_edge('tools_b', 'share_draft_message')

graph_builder.add_conditional_edges(
    'analyze_supplier_response',
    routing_with_human_intervention,
    {
        "draft_negotiation_message": "draft_negotiation_message",
        "initiate_contract": "initiate_contract",
        "notify_user_and_suggest_next_steps": "notify_user_and_suggest_next_steps",
        "provide_clarification": "provide_clarification",
        "schedule_follow_up": "schedule_follow_up",
    }
)


graph_builder.add_edge('provide_clarification', 'share_draft_message') 
graph_builder.add_edge('schedule_follow_up', END)
graph_builder.add_edge('notify_user_and_suggest_next_steps', END) 

# Contract initiation
graph_builder.add_edge('initiate_contract', END)  



def process_events(events, phase=""):
    """Process and display graph events in a consistent format"""
    for event in events:
        step_name = list(event.keys())[0] if event.keys() else "unknown"
        
        for value in event.values():
            if "messages1" in value and value["messages1"]:
                print(f"📋 Step: {step_name}")
                print(f"🤖 Assistant: {value['messages1'][-1]}")

            if "messages" in value and value["messages"]:
                last_message = value["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    print(f"🤖 System: {last_message.content}")
            if "msgs" in value and value["msgs"]:
                last_message = value["msgs"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    print(f"🤖 Negotiation: {last_message.content}")
            # Escalation and error tracking
            if "escalation_required" in value and value['escalation_required']:
                print(f"🚨 Escalation Required: {value.get('escalation_reason', 'Unknown reason')}")

            print('-' * 20)
            if "messages" in value and value["messages"]:
                print(value['messages'])

            # Status tracking
            if "status" in value and value['status']:
                status_emoji = {
                    'awaiting_human_input': '⏳',
                    'human_intervention_requested': '🆘',
                    'escalation_error': '❌',
                    'follow_up_scheduled': '📅',
                    'clarification_prepared': '❓',
                    'failure_analyzed_alternatives_provided': '🔄',
                    'contract_initiated': '📋',
                    'error_handled': '✅'
                }.get(value['status'], '📊')
                print(f"{status_emoji} Status: {value['status']}")
            
            # Intent and analysis tracking
            if "supplier_intent" in value and value['supplier_intent']:
                intent_data = value['supplier_intent']
                if isinstance(intent_data, dict):
                    intent = intent_data.get('intent', 'unknown')
                    confidence = intent_data.get('confidence', 0.0)
                    print(f"🎯 Supplier Intent: {intent} (confidence: {confidence:.2f})")
                else:
                    print(f"🎯 Supplier Intent: {intent_data}")
            
            # Workflow progress tracking
            if "next_step" in value and value['next_step']:
                print(f"➡️ Next Step: {value['next_step']}")
                
            print()  # Add spacing between events

# Compile graph
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def run_workflow(user_input_text: Optional[str] = None, thread_id: Optional[str] = None):
    """Run the complete negotiation workflow"""
    # Use configuration defaults
    thread_id = thread_id or Config.DEFAULT_THREAD_ID
    quote_input_text = Config.DEFAULT_GET_QUOTE_INPUT
    nagotiate_input_text = Config.DEFAULT_NEGOTIATION_INPUT
    
    config = {"configurable": {"thread_id": thread_id}}
    
    if Config.ENABLE_DEBUG:
        print(f"DEBUG: Using thread_id: {thread_id}")
    
    # Initialize the graph with proper state structure
    initial_state = {
        "user_input": quote_input_text, 
        "msgs": ['I want to get the response of the supplier, send the email to the specific supplier'],
        "messages" : ['please convert the document content into PDF and send it to the specific user, the email address is given'],
        "status": "starting"
    }
    
    # Phase 1: Initial workflow execution
    print("=== Phase 1: Processing quote generation request ===")
    events = graph.stream(initial_state, config)
    process_events(events)

    if initial_state['user_input'] != nagotiate_input_text:
        print("\n=== Replaying with negotiation input ===")

        replay_state = {
            "user_input": nagotiate_input_text, 
            "msgs": ['I want to get the response of the supplier, send the email to the specific supplier'],
            "messages" : ['please convert the document content into PDF and send it to the specific user, the email address is given'],
            "status": "starting"
        }


        to_replay = None
        for state in graph.get_state_history(config):
            print("Num Messages: ", len(state.values["messages1"]), "Next: ", state.next)
            print("-" * 80)
            if len(state.values["messages1"]) == 2:
                to_replay = state

        if to_replay is not None:
            print(to_replay.next)
            print(to_replay.config)
        else:
            print("No suitable state found (to_replay is None).")


        events = graph.stream(replay_state, to_replay.config)
        process_events(events)


    # Phase 2: Get supplier response
    supplier_response = input('\nsupplier_response: ')
    
    # Update state with supplier response
    graph.update_state(config, {"supplier_response": supplier_response})
    
    # Phase 3: Analyze supplier response
    print("\n=== Phase 2: Analyzing supplier response ===")
    events = graph.stream(None, config)
    process_events(events, phase="analysis")

# Main execution block
if __name__ == "__main__":
    run_workflow()