import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiService } from '../services/api';

// Initial state
const initialState = {
    // Session management
    currentSession: null,
    sessions: [],
    
    // UI state
    loading: false,
    error: null,
    toast: null,
    
    // Workflow state
    workflowStatus: 'idle', // idle, processing, completed, error
    
    // Data state
    suppliers: [],
    quotes: [],
    negotiations: [],
    contracts: [],
    
    // User preferences
    preferences: {
        theme: 'light',
        notifications: true,
        autoSave: true
    }
};

// Action types
const ActionTypes = {
    // Session actions
    SET_CURRENT_SESSION: 'SET_CURRENT_SESSION',
    UPDATE_SESSIONS: 'UPDATE_SESSIONS',
    
    // UI actions
    SET_LOADING: 'SET_LOADING',
    SET_ERROR: 'SET_ERROR',
    SHOW_TOAST: 'SHOW_TOAST',
    HIDE_TOAST: 'HIDE_TOAST',
    
    // Workflow actions
    SET_WORKFLOW_STATUS: 'SET_WORKFLOW_STATUS',
    
    // Data actions
    SET_SUPPLIERS: 'SET_SUPPLIERS',
    SET_QUOTES: 'SET_QUOTES',
    SET_NEGOTIATIONS: 'SET_NEGOTIATIONS',
    SET_CONTRACTS: 'SET_CONTRACTS',
    
    // Preference actions
    UPDATE_PREFERENCES: 'UPDATE_PREFERENCES'
};

// Reducer function
function appReducer(state, action) {
    switch (action.type) {
        case ActionTypes.SET_CURRENT_SESSION:
            return {
                ...state,
                currentSession: action.payload
            };
            
        case ActionTypes.UPDATE_SESSIONS:
            return {
                ...state,
                sessions: action.payload
            };
            
        case ActionTypes.SET_LOADING:
            return {
                ...state,
                loading: action.payload
            };
            
        case ActionTypes.SET_ERROR:
            return {
                ...state,
                error: action.payload
            };
            
        case ActionTypes.SHOW_TOAST:
            return {
                ...state,
                toast: action.payload
            };
            
        case ActionTypes.HIDE_TOAST:
            return {
                ...state,
                toast: null
            };
            
        case ActionTypes.SET_WORKFLOW_STATUS:
            return {
                ...state,
                workflowStatus: action.payload
            };
            
        case ActionTypes.SET_SUPPLIERS:
            return {
                ...state,
                suppliers: action.payload
            };
            
        case ActionTypes.SET_QUOTES:
            return {
                ...state,
                quotes: action.payload
            };
            
        case ActionTypes.SET_NEGOTIATIONS:
            return {
                ...state,
                negotiations: action.payload
            };
            
        case ActionTypes.SET_CONTRACTS:
            return {
                ...state,
                contracts: action.payload
            };
            
        case ActionTypes.UPDATE_PREFERENCES:
            return {
                ...state,
                preferences: {
                    ...state.preferences,
                    ...action.payload
                }
            };
            
        default:
            return state;
    }
}

// Create context
const AppContext = createContext();

// Provider component
export function AppProvider({ children }) {
    const [state, dispatch] = useReducer(appReducer, initialState);
    
    // Load initial data on mount
    useEffect(() => {
        loadInitialData();
    }, []);
    
    // Action creators
    const actions = {
        // Session management
        setCurrentSession: (session) => {
            dispatch({ type: ActionTypes.SET_CURRENT_SESSION, payload: session });
        },
        
        updateSessions: (sessions) => {
            dispatch({ type: ActionTypes.UPDATE_SESSIONS, payload: sessions });
        },
        
        // UI actions
        setLoading: (loading) => {
            dispatch({ type: ActionTypes.SET_LOADING, payload: loading });
        },
        
        setError: (error) => {
            dispatch({ type: ActionTypes.SET_ERROR, payload: error });
        },
        
        showToast: (message, type = 'info', duration = 5000) => {
            dispatch({ 
                type: ActionTypes.SHOW_TOAST, 
                payload: { message, type, duration } 
            });
        },
        
        hideToast: () => {
            dispatch({ type: ActionTypes.HIDE_TOAST });
        },
        
        // Workflow actions
        setWorkflowStatus: (status) => {
            dispatch({ type: ActionTypes.SET_WORKFLOW_STATUS, payload: status });
        },
        
        // Data actions
        setSuppliers: (suppliers) => {
            dispatch({ type: ActionTypes.SET_SUPPLIERS, payload: suppliers });
        },
        
        setQuotes: (quotes) => {
            dispatch({ type: ActionTypes.SET_QUOTES, payload: quotes });
        },
        
        setNegotiations: (negotiations) => {
            dispatch({ type: ActionTypes.SET_NEGOTIATIONS, payload: negotiations });
        },
        
        setContracts: (contracts) => {
            dispatch({ type: ActionTypes.SET_CONTRACTS, payload: contracts });
        },
        
        // Preference actions
        updatePreferences: (preferences) => {
            dispatch({ type: ActionTypes.UPDATE_PREFERENCES, payload: preferences });
            // Persist to localStorage
            localStorage.setItem('procurement_preferences', JSON.stringify({
                ...state.preferences,
                ...preferences
            }));
        },
        
        // API integration actions
        async loadSessionData(sessionId) {
            try {
                actions.setLoading(true);
                
                // Load session state
                const sessionState = await apiService.getWorkflowState(sessionId);
                actions.setCurrentSession(sessionState);
                
                // Load related data based on session state
                if (sessionState.supplier_search_results) {
                    const suppliers = await apiService.getTopSuppliers(sessionId);
                    actions.setSuppliers(suppliers.top_suppliers || []);
                }
                
                if (sessionState.generated_quote) {
                    const quotes = await apiService.getGeneratedQuotes(sessionId);
                    actions.setQuotes([quotes.generated_quote]);
                }
                
            } catch (error) {
                console.error('Error loading session data:', error);
                actions.setError(error.message);
                actions.showToast('Failed to load session data', 'error');
            } finally {
                actions.setLoading(false);
            }
        },
        
        async loadAllSessions() {
            try {
                const sessions = await apiService.listSessions();
                actions.updateSessions(sessions.active_sessions || []);
            } catch (error) {
                console.error('Error loading sessions:', error);
                actions.showToast('Failed to load sessions', 'error');
            }
        }
    };
    
    // Load initial data
    async function loadInitialData() {
        try {
            // Load preferences from localStorage
            const savedPreferences = localStorage.getItem('procurement_preferences');
            if (savedPreferences) {
                const preferences = JSON.parse(savedPreferences);
                actions.updatePreferences(preferences);
            }
            
            // Load active sessions
            await actions.loadAllSessions();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    const value = {
        state,
        actions,
        // Computed values
        computed: {
            hasActiveSessions: state.sessions.length > 0,
            isSessionActive: !!state.currentSession,
            canStartNewSession: state.workflowStatus === 'idle' || state.workflowStatus === 'completed',
            hasError: !!state.error,
            isLoading: state.loading
        }
    };
    
    return (
        <AppContext.Provider value={value}>
            {children}
        </AppContext.Provider>
    );
}

// Custom hook to use the context
export function useApp() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
}

// Selector hooks for specific data
export function useCurrentSession() {
    const { state } = useApp();
    return state.currentSession;
}

export function useSuppliers() {
    const { state } = useApp();
    return state.suppliers;
}

export function useQuotes() {
    const { state } = useApp();
    return state.quotes;
}

export function useNegotiations() {
    const { state } = useApp();
    return state.negotiations;
}

export function useContracts() {
    const { state } = useApp();
    return state.contracts;
}

export function useToast() {
    const { state, actions } = useApp();
    return {
        toast: state.toast,
        showToast: actions.showToast,
        hideToast: actions.hideToast
    };
}

export { ActionTypes };