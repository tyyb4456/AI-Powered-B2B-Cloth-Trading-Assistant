import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
    Send, 
    Paperclip, 
    Plus, 
    Download, 
    MoreVertical,
    Bot,
    User,
    AlertCircle,
    CheckCircle,
    RefreshCw,
    MessageCircle,
    X
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';

export default function Chat() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);
    const { state, actions } = useApp();
    
    const [messages, setMessages] = useState([
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I\'m your textile procurement assistant. I can help you with:\n\n• Getting quotes for fabric purchases\n• Finding suppliers\n• Negotiating terms\n• Generating contracts\n\nWhat would you like to work on today?',
            timestamp: new Date(Date.now() - 60000),
            type: 'greeting'
        }
    ]);
    
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPostActions, setShowPostActions] = useState(false);
    const [actionMode, setActionMode] = useState(null); // null, 'replay', 'supplier_response'
    const [workflowPhase, setWorkflowPhase] = useState('initial'); // 'initial', 'awaiting_supplier'
    const [sessionInfo, setSessionInfo] = useState({
        id: sessionId || 'new',
        status: 'active',
        intent: null,
        confidence: null
    });

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (sessionId && sessionId !== 'new' && sessionInfo.id !== sessionId) {
            loadSessionHistory();
        }
    }, [sessionId]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const loadSessionHistory = async () => {
        try {
            setIsLoading(true);
            const history = await apiService.getWorkflowHistory(sessionId);
            
            if (history.messages_log && history.messages_log.length > 0) {
                const historyMessages = history.messages_log.map((msg, index) => ({
                    id: `history_${index}`,
                    role: 'assistant',
                    content: msg.message,
                    timestamp: new Date(Date.now() - (history.messages_log.length - index) * 60000),
                    step: msg.step,
                    type: 'response'
                }));
                setMessages(prev => [...prev, ...historyMessages]);
                
                // Check if we should be in supplier response mode
                const lastMessage = historyMessages[historyMessages.length - 1];
                if (lastMessage && (lastMessage.content.toLowerCase().includes('supplier') || 
                    lastMessage.content.toLowerCase().includes('quote') ||
                    lastMessage.content.toLowerCase().includes('negotiat'))) {
                    setWorkflowPhase('awaiting_supplier');
                }
                
                setTimeout(() => setShowPostActions(true), 500);
            }
            
            const sessionState = await apiService.getWorkflowState(sessionId);
            setSessionInfo({
                id: sessionId,
                status: sessionState.status,
                intent: sessionState.intent,
                confidence: sessionState.intent_confidence
            });
            
            actions.setCurrentSession(sessionState);
            
        } catch (error) {
            console.error('Error loading session history:', error);
            actions.showToast('Failed to load session history', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: inputMessage,
            timestamp: new Date(),
            type: actionMode || 'user_input'
        };

        setMessages(prev => [...prev, userMessage]);
        const currentInput = inputMessage;
        setInputMessage('');
        setIsLoading(true);
        setShowPostActions(false);
        actions.setWorkflowStatus('processing');

        try {
            if (actionMode === 'replay') {
                await replayWorkflow(currentInput);
            } else if (actionMode === 'supplier_response' || workflowPhase === 'awaiting_supplier') {
                await continueWorkflow(sessionInfo.id, currentInput);
            } else if (sessionInfo.id === 'new') {
                await startNewWorkflow(currentInput);
            } else {
                await continueWorkflow(sessionInfo.id, currentInput);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addSystemMessage('Sorry, there was an error processing your message. Please try again.', 'error');
            actions.showToast('Failed to process message', 'error');
        } finally {
            setIsLoading(false);
            setActionMode(null);
            actions.setWorkflowStatus('idle');
        }
    };

    const startNewWorkflow = async (userInput) => {
        try {
            const response = await apiService.startWorkflow(userInput, 'quote');
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            await processStreamingResponse(response, true);

        } catch (error) {
            console.error('Error starting workflow:', error);
            addSystemMessage(`Failed to start workflow: ${error.message}`, 'error');
            actions.showToast('Failed to start workflow', 'error');
        }
    };

    const continueWorkflow = async (sessionId, supplierResponse) => {
        try {
            const response = await apiService.continueWorkflow(sessionId, supplierResponse);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            await processStreamingResponse(response, false);

        } catch (error) {
            console.error('Error continuing workflow:', error);
            addSystemMessage(`Failed to continue workflow: ${error.message}`, 'error');
            actions.showToast('Failed to continue workflow', 'error');
        }
    };

    const replayWorkflow = async (newInput) => {
        try {
            const response = await apiService.replayWorkflow(sessionInfo.id, newInput);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            // After replay, we'll be waiting for supplier response
            setWorkflowPhase('awaiting_supplier');
            await processStreamingResponse(response, false);

        } catch (error) {
            console.error('Error replaying workflow:', error);
            addSystemMessage(`Failed to replay workflow: ${error.message}`, 'error');
            actions.showToast('Failed to replay workflow', 'error');
        }
    };

    const processStreamingResponse = async (response, isNewWorkflow) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                const trimmedLine = line.trim();
                if (trimmedLine === '') continue;
                
                if (trimmedLine.startsWith('data: ')) {
                    const dataStr = trimmedLine.slice(6);
                    
                    try {
                        const data = JSON.parse(dataStr);
                        console.log('Received data:', data);
                        
                        if (data.message) {
                            addAssistantMessage(data.message, data.step);
                        }
                        
                        if (data.session_id && isNewWorkflow) {
                            setSessionInfo({
                                id: data.session_id,
                                status: data.status,
                                intent: data.intent,
                                confidence: data.intent_confidence
                            });
                            
                            navigate(`/chat/${data.session_id}`, { replace: true });
                            actions.setCurrentSession(data);
                            actions.showToast(`Session started! Intent: ${data.intent}`, 'success');
                        }
                        
                    } catch (parseError) {
                        console.warn('Failed to parse SSE data:', dataStr);
                    }
                }
                else if (trimmedLine.startsWith('event: done')) {
                    // Determine what to show after completion
                    setTimeout(() => {
                        if (workflowPhase === 'awaiting_supplier') {
                            // Show supplier response input
                            setActionMode('supplier_response');
                            actions.showToast('Enter supplier response to continue workflow', 'info');
                        } else {
                            // Show normal actions
                            setShowPostActions(true);
                        }
                    }, 1000);
                }
            }
        }
    };

    const addAssistantMessage = (content, step) => {
        const message = {
            id: Date.now().toString() + Math.random(),
            role: 'assistant',
            content,
            timestamp: new Date(),
            step,
            type: 'response'
        };
        setMessages(prev => [...prev, message]);
    };

    const addSystemMessage = (content, type = 'info') => {
        const message = {
            id: Date.now().toString() + Math.random(),
            role: 'system',
            content,
            timestamp: new Date(),
            type
        };
        setMessages(prev => [...prev, message]);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const startNewChat = () => {
        setMessages([
            {
                id: '1',
                role: 'assistant',
                content: 'Hello! I\'m your textile procurement assistant. I can help you with quotes, supplier sourcing, negotiations, and contracts. What would you like to work on today?',
                timestamp: new Date(),
                type: 'greeting'
            }
        ]);
        setSessionInfo({ id: 'new', status: 'active', intent: null, confidence: null });
        setShowPostActions(false);
        setActionMode(null);
        setWorkflowPhase('initial');
        actions.setCurrentSession(null);
        navigate('/chat', { replace: true });
        actions.showToast('New chat started', 'info');
    };

    const handleReplayWorkflow = () => {
        setShowPostActions(false);
        setActionMode('replay');
        setWorkflowPhase('initial');
        actions.showToast('Enter new input for replay workflow', 'info');
    };

    const cancelAction = () => {
        setActionMode(null);
        if (workflowPhase === 'awaiting_supplier') {
            setActionMode('supplier_response');
        } else {
            setShowPostActions(true);
        }
        setInputMessage('');
    };

    const exportConversation = () => {
        const conversationData = {
            sessionId: sessionInfo.id,
            messages: messages,
            sessionInfo: sessionInfo,
            exportedAt: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(conversationData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `conversation_${sessionInfo.id}_${new Date().getTime()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        actions.showToast('Conversation exported successfully', 'success');
    };

    const getMessageIcon = (role, type) => {
        switch (role) {
            case 'user':
                return <User size={16} className="text-blue-600" />;
            case 'assistant':
                return <Bot size={16} className="text-green-600" />;
            case 'system':
                if (type === 'error') return <AlertCircle size={16} className="text-red-600" />;
                if (type === 'success') return <CheckCircle size={16} className="text-green-600" />;
                return <AlertCircle size={16} className="text-blue-600" />;
            default:
                return <Bot size={16} className="text-gray-600" />;
        }
    };

    const getMessageStyles = (role, type) => {
        if (role === 'user') {
            return 'bg-blue-600 text-white ml-auto max-w-[80%]';
        } else if (role === 'system') {
            if (type === 'error') return 'bg-red-50 text-red-800 border-l-4 border-red-500';
            if (type === 'success') return 'bg-green-50 text-green-800 border-l-4 border-green-500';
            return 'bg-blue-50 text-blue-800 border-l-4 border-blue-500';
        }
        return 'bg-gray-100 text-gray-900 mr-auto max-w-[80%]';
    };

    const formatTimestamp = (timestamp) => {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        }).format(new Date(timestamp));
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'bg-green-400';
            case 'error':
                return 'bg-red-400';
            case 'processing':
                return 'bg-yellow-400';
            default:
                return 'bg-blue-400';
        }
    };

    const getInputPlaceholder = () => {
        switch (actionMode) {
            case 'replay':
                return 'Enter new input to replay the workflow (e.g., "I need silk fabric instead")';
            case 'supplier_response':
                return 'Enter supplier response (e.g., "We can offer $5.50 per meter with 30 days delivery")';
            default:
                if (workflowPhase === 'awaiting_supplier') {
                    return 'Enter supplier response to continue the workflow';
                }
                return 'Describe your textile procurement needs (e.g., "I need 5000 meters of organic cotton canvas")';
        }
    };

    const getActionModeTitle = () => {
        switch (actionMode) {
            case 'replay':
                return 'Replay Workflow Mode';
            case 'supplier_response':
                return 'Supplier Response Mode';
            default:
                return '';
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] bg-white rounded-lg border border-gray-200">
            {/* Chat Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Bot size={20} className="text-blue-600" />
                    </div>
                    <div>
                        <h2 className="font-semibold text-gray-900">
                            Procurement Assistant
                        </h2>
                        <div className="flex items-center space-x-2 text-sm">
                            <span className={`w-2 h-2 rounded-full ${
                                isLoading ? 'bg-yellow-400' : getStatusColor(sessionInfo.status)
                            }`}></span>
                            <span className="text-gray-500">
                                {sessionInfo.id !== 'new' ? `Session: ${sessionInfo.id.slice(0, 8)}...` : 'New Session'}
                            </span>
                            {sessionInfo.intent && (
                                <span className="text-blue-600 bg-blue-100 px-2 py-1 rounded text-xs">
                                    {sessionInfo.intent}
                                </span>
                            )}
                            {actionMode && (
                                <span className="text-purple-600 bg-purple-100 px-2 py-1 rounded text-xs">
                                    {actionMode === 'replay' ? 'Replay Mode' : 'Supplier Response Mode'}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                
                <div className="flex items-center space-x-2">
                    <button
                        onClick={startNewChat}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                        title="Start New Chat"
                    >
                        <Plus size={16} />
                    </button>
                    <button 
                        onClick={exportConversation}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                        title="Export Conversation"
                    >
                        <Download size={16} />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                        <MoreVertical size={16} />
                    </button>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                    <div key={message.id} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-1">
                            {getMessageIcon(message.role, message.type)}
                        </div>
                        
                        <div className="flex-1">
                            <div className={`p-3 rounded-lg ${getMessageStyles(message.role, message.type)}`}>
                                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                                    {message.content}
                                </div>
                                {message.step && (
                                    <div className="mt-2 text-xs opacity-75">
                                        Step: {message.step}
                                    </div>
                                )}
                            </div>
                            <div className="flex items-center justify-between mt-1">
                                <span className="text-xs text-gray-500">
                                    {formatTimestamp(message.timestamp)}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
                
                {isLoading && (
                    <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0 mt-1">
                            <Bot size={16} className="text-green-600" />
                        </div>
                        <div className="bg-gray-100 p-3 rounded-lg">
                            <div className="flex items-center space-x-2">
                                <div className="spinner"></div>
                                <span className="text-sm text-gray-600">
                                    {state.workflowStatus === 'processing' ? 'Processing your request...' : 'Typing...'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Post-Conversation Actions - Only show for initial phase */}
                {showPostActions && !isLoading && !actionMode && workflowPhase === 'initial' && (
                    <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-200">
                        <h3 className="text-sm font-medium text-gray-900 mb-3">What would you like to do next?</h3>
                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={startNewChat}
                                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                            >
                                <Plus size={16} className="mr-2" />
                                Start New Chat
                            </button>
                            <button
                                onClick={handleReplayWorkflow}
                                className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm"
                            >
                                <RefreshCw size={16} className="mr-2" />
                                Replay Workflow
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Replay workflow with different requirements, or start fresh
                        </p>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            {(!showPostActions || actionMode || workflowPhase === 'awaiting_supplier') && (
                <div className="border-t border-gray-200 p-4">
                    {/* Action Mode Header */}
                    {(actionMode || workflowPhase === 'awaiting_supplier') && (
                        <div className="flex items-center justify-between mb-3 p-2 bg-purple-50 rounded-lg">
                            <div className="flex items-center space-x-2">
                                {actionMode === 'replay' ? (
                                    <RefreshCw size={16} className="text-purple-600" />
                                ) : (
                                    <MessageCircle size={16} className="text-purple-600" />
                                )}
                                <span className="text-sm font-medium text-purple-700">
                                    {getActionModeTitle() || 'Awaiting Supplier Response'}
                                </span>
                            </div>
                            <button
                                onClick={cancelAction}
                                className="p-1 text-purple-600 hover:text-purple-800"
                                title="Cancel"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    )}

                    <div className="flex items-end space-x-3">
                        <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                            <Paperclip size={18} />
                        </button>
                        
                        <div className="flex-1">
                            <textarea
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={getInputPlaceholder()}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                rows={2}
                                disabled={isLoading}
                            />
                        </div>
                        
                        <button
                            onClick={handleSendMessage}
                            disabled={!inputMessage.trim() || isLoading}
                            className={`p-3 rounded-lg ${
                                inputMessage.trim() && !isLoading
                                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                            }`}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    
                    <div className="flex items-center justify-between mt-2">
                        <p className="text-xs text-gray-500">
                            Press Enter to send, Shift+Enter for new line
                        </p>
                        {sessionInfo.confidence && (
                            <span className="text-xs text-gray-500">
                                Confidence: {Math.round(sessionInfo.confidence * 100)}%
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}