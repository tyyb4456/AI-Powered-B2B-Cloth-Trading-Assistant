from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from graph_builder import graph, Config, process_events
from starlette.responses import StreamingResponse
import json
import uuid

router = APIRouter()

# Store active sessions
workflow_sessions = {}

def serialize_message(msg):
    """Convert AIMessage/HumanMessage/etc. to plain text"""
    if hasattr(msg, "content"):
        return msg.content
    return str(msg)


@router.get("/start")
def start_workflow(
    user_input: str = Query(None, description="User input for the workflow"),
    thread_id: Optional[str] = Query(None, description="Thread ID for the session"),
    # input_type: str = Query("quote", description="Type of input: 'quote' or 'negotiate'")
):
    """
    GET endpoint to start the workflow - triggers the initial graph execution
    Based on graph_builder.py run_workflow function
    """
    try:
        # Use provided thread_id or generate new one
        session_thread_id = thread_id or str(uuid.uuid4())
        
            
        config = {"configurable": {"thread_id": session_thread_id}}
        
        # Initial state setup matching graph_builder.py
        initial_state = {
            "user_input": user_input, 
            "msgs": ['I want to get the response of the supplier, send the email to the specific supplier'],
            "messages": ['please convert the document content into PDF and send it to the specific user, the email address is given'],
            "status": "starting",
            "session_id": session_thread_id
        }
        
        # Execute the workflow
        # events = list(graph.stream(initial_state, config))

        def event_stream():
            """Plain generator for StreamingResponse (sync)."""
            final_state = {}
            messages_log = []

            try:
                # graph.stream is a normal (blocking) generator here
                for events in graph.stream(initial_state, config):
                    for step_name, step_data in events.items():
                        final_state.update(step_data)

                        if "messages1" in step_data and step_data["messages1"]:
                            last_msg = serialize_message(step_data["messages1"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        if "messages" in step_data and step_data["messages"]:
                            last_msg = serialize_message(step_data["messages"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        if "msgs" in step_data and step_data["msgs"]:
                            last_msg = serialize_message(step_data["msgs"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"


                # send final summary when graph finishes
                summary = {
                    "session_id": session_thread_id,
                    "status": final_state.get("status", "completed"),
                    "intent": final_state.get("intent"),
                    "workflow_completed": True,
                    "extracted_parameters": final_state.get("extracted_parameters"),
                    "intent_confidence": final_state.get("intent_confidence"),
                    "intent_reasoning": final_state.get("intent_reasoning"),
                }
                workflow_sessions[session_thread_id] = {
                    "config": config,
                    "final_state": final_state,
                    "messages_log": messages_log,
                }
                yield f"event: done\ndata: {json.dumps(summary)}\n\n"

            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        # StreamingResponse will call event_stream synchronously
        return StreamingResponse(event_stream(), media_type="text/event-stream")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow start failed: {str(e)}")
    
@router.get("/top_suppliers/{session_id}")
def get_top_suppliers(session_id: str):
    """
    Retrieve top suppliers for a given session
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    final_state = workflow_sessions[session_id]["final_state"]
    
    if "top_suppliers" not in final_state or not final_state["top_suppliers"]:
        raise HTTPException(status_code=404, detail="No suppliers found for this session")
        
    return {
        "session_id": session_id,
        "top_suppliers": final_state["top_suppliers"],
        "search_confidence": final_state.get("search_confidence"),
        "market_insights": final_state.get("market_insights"),
        "alternative_suggestions": final_state.get("alternative_suggestions")
    }

    
@router.get("/quotes/{session_id}")
def get_generated_quotes(session_id: str):
    """
    Retrieve generated quotes for a given session
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    final_state = workflow_sessions[session_id]["final_state"]
    
    if "generated_quote" not in final_state or not final_state["generated_quote"]:
        raise HTTPException(status_code=404, detail="No quotes found for this session")
        
    return {
        "session_id": session_id,
        "generated_quote": final_state["generated_quote"],
        "quote_document": final_state.get("quote_document"),
        "quote_id": final_state.get("quote_id"),
        "supplier_options": final_state.get("supplier_options"),
        "estimated_savings": final_state.get("estimated_savings")
    }


    
@router.get("/replay/{session_id}")
def replay_workflow(
    session_id: str,
    new_input_type: str = Query(None, description="New input type for replay")
):
    """
    Replay workflow with different input - NOW WITH STREAMING
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    config = workflow_sessions[session_id]["config"]
    
    # Get state history to find replay point
    state_history = list(graph.get_state_history(config))
    
    to_replay = None
    for state in state_history:
        if len(state.values.get("messages1", [])) == 2:
            to_replay = state
            break
            
    if not to_replay:
        raise HTTPException(status_code=400, detail="No suitable replay state found")
    
    try:
        replay_state = {
            "user_input": new_input_type, 
            "msgs": ['I want to get the response of the supplier, send the email to the specific supplier'],
            "messages": ['please convert the document content into PDF and send it to the specific user, the email address is given'],
            "status": "starting"
        }
        
        # STREAMING VERSION - Like start and continue endpoints
        def event_stream():
            """Stream replay events like start/continue endpoints"""
            final_state = {}
            messages_log = []

            try:
                # Execute replay with streaming
                for events in graph.stream(replay_state, to_replay.config):
                    for step_name, step_data in events.items():
                        final_state.update(step_data)

                        # Stream messages1
                        if "messages1" in step_data and step_data["messages1"]:
                            last_msg = serialize_message(step_data["messages1"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        # Stream messages
                        if "messages" in step_data and step_data["messages"]:
                            last_msg = serialize_message(step_data["messages"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        # Stream msgs
                        if "msgs" in step_data and step_data["msgs"]:
                            last_msg = serialize_message(step_data["msgs"][-1])
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                # Send final summary when replay finishes
                summary = {
                    "session_id": session_id,
                    "status": final_state.get("status", "replayed"),
                    "intent": final_state.get("intent"),
                    "replay_completed": True,
                    "new_input_type": new_input_type,
                    "workflow_completed": True,
                    "extracted_parameters": final_state.get("extracted_parameters"),
                    "intent_confidence": final_state.get("intent_confidence"),
                }
                
                # Update session with replayed data
                workflow_sessions[session_id]["final_state"] = final_state
                workflow_sessions[session_id]["messages_log"] = messages_log
                
                yield f"event: done\ndata: {json.dumps(summary)}\n\n"

            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        # Return StreamingResponse like other endpoints
        return StreamingResponse(event_stream(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Replay failed: {str(e)}")
    
@router.get("/get_drafted_message/{session_id}")
def get_drafted_message(session_id: str):
    """
    Retrieve drafted negotiation message for a given session
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    final_state = workflow_sessions[session_id]["final_state"]
    
    if "drafted_message" not in final_state or not final_state["drafted_message"]:
        raise HTTPException(status_code=404, detail="No drafted message found for this session")
        
    return {
        "session_id": session_id,
        "drafted_message": final_state["drafted_message"],
        "negotiation_strategy": final_state.get("negotiation_strategy"),
        "message_id": final_state.get("message_id"),
        "message_ready": final_state.get("message_ready"),
        "last_message_confidence": final_state.get("last_message_confidence"),
    }


    
    
@router.get("/continue/{session_id}")
def continue_workflow(
    session_id: str,
    supplier_response: str = Query(..., description="Supplier response to continue workflow")
):
    """
    Continue an existing workflow session and stream messages1
    to the client as each node finishes.
    """

    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = workflow_sessions[session_id]
        config = session_data["config"]
        final_state = session_data["final_state"].copy()
        messages_log = session_data["messages_log"].copy()

        # Update state with supplier response before resuming
        graph.update_state(config, {"supplier_response": supplier_response})

        def event_stream():
            try:
                # Resume the graph and yield updates as they occur
                for events in graph.stream(None, config):
                    for step_name, step_data in events.items():
                        final_state.update(step_data)

                        if "messages1" in step_data and step_data["messages1"]:
                            last_msg = step_data["messages1"][-1]
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        if 'messages' in step_data and step_data['messages']:
                            last_msg = step_data['messages'][-1]
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                        if 'msgs' in step_data and step_data['msgs']:
                            last_msg = step_data['msgs'][-1]
                            messages_log.append({"step": step_name, "message": last_msg})
                            yield f"data: {json.dumps({'step': step_name, 'message': last_msg})}\n\n"

                # send final summary when done
                summary = {
                    "session_id": session_id,
                    "status": final_state.get("status", "continued"),
                    "supplier_response": supplier_response,
                    "analysis_complete": True,
                    "negotiation_status": final_state.get("negotiation_status"),
                    "next_action": final_state.get("next_step"),
                    "contract_ready": final_state.get("contract_ready", False),
                }

                # persist updated state
                workflow_sessions[session_id]["final_state"] = final_state
                workflow_sessions[session_id]["messages_log"] = messages_log

                yield f"event: done\ndata: {json.dumps(summary)}\n\n"

            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow continuation failed: {str(e)}")
    

@router.get("/analyze_response/{session_id}")
def analyze_supplier_response(session_id: str):
    """
    Retrieve analysis of supplier response for a given session
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    final_state = workflow_sessions[session_id]["final_state"]
    
    if "supplier_intent" not in final_state or not final_state["supplier_intent"]:
        raise HTTPException(status_code=404, detail="No supplier response analysis found for this session")
        
    return {
        "session_id": session_id,
        "supplier_intent": final_state["supplier_intent"],
        "extracted_terms": final_state.get("extracted_terms"),
        "negotiation_analysis": final_state.get("negotiation_analysis"),
        "negotiation_status": final_state.get("negotiation_status"),
        "next_step": final_state.get("next_step"),
        "escalation_required": final_state.get("escalation_required", False),
        "escalation_summary": final_state.get("escalation_summary")
    }

@router.get("/drafted_contract/{session_id}")
def get_drafted_contract(session_id: str):
    """
    Retrieve drafted contract for a given session
    """
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    final_state = workflow_sessions[session_id]["final_state"]
    
    if "drafted_contract" not in final_state or not final_state["drafted_contract"]:
        raise HTTPException(status_code=404, detail="No drafted contract found for this session")
        
    return {
        "session_id": session_id,
        "drafted_contract": final_state["drafted_contract"],
        "contract_ready": final_state.get("contract_ready", False)
    }



# @router.get("/continue/{session_id}")
# def continue_workflow(
#     session_id: str,
#     supplier_response: str = Query(..., description="Supplier response to continue workflow")
# ):
#     """
#     GET endpoint to continue workflow from existing state
#     Based on graph_builder.py Phase 2 implementation
#     """
#     try:
#         if session_id not in workflow_sessions:
#             raise HTTPException(status_code=404, detail="Session not found")
            
#         session_data = workflow_sessions[session_id]
#         config = session_data["config"]
        
#         # Update state with supplier response (matching graph_builder.py)
#         graph.update_state(config, {"supplier_response": supplier_response})
        
#         # Continue workflow execution
#         events = list(graph.stream(None, config))
        
#         # Process continuation events
#         final_state = session_data["final_state"].copy()
#         messages_log = session_data["messages_log"].copy()
        
#         for event in events:
#             for step_name, step_data in event.items():
#                 # Update final state
#                 final_state.update(step_data)
                
#                 # Log new messages
#                 if "messages1" in step_data and step_data["messages1"]:
#                     messages_log.append({
#                         "step": step_name,
#                         "message": step_data["messages1"][-1]
#                     })
        
#         # Update stored session
#         workflow_sessions[session_id]["final_state"] = final_state
#         workflow_sessions[session_id]["messages_log"] = messages_log
        
#         return {
#             "session_id": session_id,
#             "status": final_state.get("status", "continued"),
#             "supplier_response": supplier_response,
#             "analysis_complete": True,
#             "negotiation_status": final_state.get("negotiation_status"),
#             "next_action": final_state.get("next_step"),
#             "messages_log": messages_log[-3:],  # Last 3 messages
#             "contract_ready": final_state.get("contract_ready", False),
#             "escalation_required": final_state.get("escalation_required", False)
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Workflow continuation failed: {str(e)}")





@router.get("/state/{session_id}")
def get_workflow_state(session_id: str):
    """
    Get current state of workflow session
    """
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session_data = workflow_sessions[session_id]
        final_state = session_data["final_state"]
        
        return {
            "session_id": session_id,
            "status": final_state.get("status"),
            "intent": final_state.get("intent"),
            "intent_confidence": final_state.get("intent_confidence"),
            "next_step": final_state.get("next_step"),
            "extracted_parameters": final_state.get("extracted_parameters"),
            "supplier_search_results": final_state.get("supplier_search_results"),
            "generated_quote": final_state.get("generated_quote"),
            "negotiation_status": final_state.get("negotiation_status"),
            "contract_ready": final_state.get("contract_ready", False),
            "escalation_summary": final_state.get("escalation_summary"),
            "messages_count": len(session_data["messages_log"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get state: {str(e)}")


@router.get("/history/{session_id}")
def get_workflow_history(session_id: str):
    """
    Get full message history for workflow session
    """
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session_data = workflow_sessions[session_id]
        
        return {
            "session_id": session_id,
            "messages_log": session_data["messages_log"],
            "negotiation_history": session_data["final_state"].get("negotiation_history", []),
            "total_messages": len(session_data["messages_log"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")





@router.delete("/session/{session_id}")
def delete_session(session_id: str):
    """
    Clean up workflow session
    """
    if session_id in workflow_sessions:
        del workflow_sessions[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions")
def list_sessions():
    """
    List all active workflow sessions
    """
    return {
        "active_sessions": list(workflow_sessions.keys()),
        "total_sessions": len(workflow_sessions)
    }