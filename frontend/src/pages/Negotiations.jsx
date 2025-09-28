
// pages/Negotiations.jsx
import React from 'react';
import { useParams } from 'react-router-dom';

export default function Negotiations() {
    const { sessionId } = useParams();
    
    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
                Negotiation Center
            </h1>
            {sessionId && (
                <p className="text-gray-600 mb-4">
                    Session ID: {sessionId}
                </p>
            )}
            <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500">
                    Negotiation center coming soon...
                </p>
                <p className="text-sm text-gray-400 mt-2">
                    Handle negotiations with AI-powered assistance
                </p>
            </div>
        </div>
    );
}