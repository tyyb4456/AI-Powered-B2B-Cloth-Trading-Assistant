from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from nodes.recieve_user_input import receive_input
from nodes.intent_classify_node import classify_intent
from nodes.extract_parameters_node import extract_parameters
from nodes.supplier_sourcing_node import supplier_sourcing
from nodes.generate_quote_node import generate_quote
from nodes.send_output_to_user_node import document_sender
from nodes.send_output_to_user_node import tool_s

from state import AgentState

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

tools_list = tool_s()

graph_builder = StateGraph(AgentState)

graph_builder.add_node('receive_input' , receive_input)
graph_builder.add_node('classify_intent' , classify_intent)
graph_builder.add_node('extract_parameters' , extract_parameters)
graph_builder.add_node('supplier_sourcing' , supplier_sourcing)
graph_builder.add_node('generate_quote' , generate_quote)
graph_builder.add_node('document_sender' , document_sender)
tool_node = ToolNode(tools_list)  # <---- use composio tools directly
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START , 'receive_input')
graph_builder.add_edge('receive_input' , 'classify_intent')
graph_builder.add_edge('classify_intent' , 'extract_parameters')
graph_builder.add_edge('extract_parameters' , 'supplier_sourcing')
graph_builder.add_edge('supplier_sourcing' , 'generate_quote')
graph_builder.add_edge('generate_quote' , 'document_sender')

graph_builder.add_conditional_edges(
    'document_sender',
    tools_condition
)

graph_builder.add_edge('tools' , 'document_sender')

# graph_builder.add_edge('document_sender' , END)

workflow = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "2"}}

def create_initial_state(user_input_text: str, user_id: str = "test_user", channel: str = "api") -> dict:
    """Create properly structured initial state"""
    
    import uuid
    
    return {
        'user_id': user_id,
        'session_id': str(uuid.uuid4()),
        'channel': channel,
        'messages': [],
        'user_input': user_input_text,
        'next_step': 'receive_input'
    }

initial_state = create_initial_state(
    user_input_text="""
    I need 10,000 meters of organic cotton fabric in white for Los Angeles delivery within 30 days,
    Looking for high-quality denim, around 500 rolls, budget is $8 per meter,
    Need cotton fabric urgently,
    Get me a quote for 5000 meters of 200 GSM cotton poplin, GOTS certified, ship to Bangladesh in 45 days under $4.50/meter
    """,
    user_id="trader_001",
    channel="web_portal"
)

for event in workflow.stream(initial_state, config):
    for value in event.values():
        # print(json.dumps(value, indent=2, ensure_ascii=False))
        if 'messages' in value and value['messages']:
            print(f"Step: {list(event.keys())[0]}")
            print(f"Message: {value['messages'][-1]}")
            print("-" * 50) 