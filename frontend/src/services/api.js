// services/api.js - API service layer for backend communication

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    // Utility method for handling fetch responses
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}`);
        }
        return response.json();
    }

    // Start new workflow session
    async startWorkflow(userInput, inputType = 'quote') {
        const url = new URL(`${this.baseUrl}/api/workflow/start`);
        url.searchParams.append('user_input', userInput);
        url.searchParams.append('input_type', inputType);

        return fetch(url.toString());
    }


    // Replay workflow with different input - NOW RETURNS STREAMING RESPONSE
    async replayWorkflow(sessionId, newInput) {
        const url = new URL(`${this.baseUrl}/api/workflow/replay/${sessionId}`);
        url.searchParams.append('new_input_type', newInput);
        
        // Return raw response for streaming - DON'T call handleResponse
        return fetch(url.toString());
    }

    // Continue existing workflow session
    async continueWorkflow(sessionId, supplierResponse) {
        const url = new URL(`${this.baseUrl}/api/workflow/continue/${sessionId}`);
        url.searchParams.append('supplier_response', supplierResponse);

        return fetch(url.toString());
    }

    // Get workflow state
    async getWorkflowState(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/state/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get workflow history
    async getWorkflowHistory(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/history/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get top suppliers for a session
    async getTopSuppliers(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/top_suppliers/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get generated quotes for a session
    async getGeneratedQuotes(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/quotes/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get drafted negotiation message
    async getDraftedMessage(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/get_drafted_message/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get supplier response analysis
    async getSupplierAnalysis(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/analyze_response/${sessionId}`);
        return this.handleResponse(response);
    }

    // Get drafted contract
    async getDraftedContract(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/drafted_contract/${sessionId}`);
        return this.handleResponse(response);
    }


    // List all active sessions
    async listSessions() {
        const response = await fetch(`${this.baseUrl}/api/workflow/sessions`);
        return this.handleResponse(response);
    }

    // Delete a session
    async deleteSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/workflow/session/${sessionId}`, {
            method: 'DELETE'
        });
        return this.handleResponse(response);
    }
}

// Create singleton instance
export const apiService = new ApiService();

// Export individual methods for convenience
export const {
    startWorkflow,
    continueWorkflow,
    getWorkflowState,
    getWorkflowHistory,
    getTopSuppliers,
    getGeneratedQuotes,
    getDraftedMessage,
    getSupplierAnalysis,
    getDraftedContract,
    replayWorkflow,
    listSessions,
    deleteSession
} = apiService;

export default apiService;