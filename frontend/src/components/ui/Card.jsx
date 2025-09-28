// components/ui/Card.jsx
import React from 'react';

export function Card({ children, className = '', padding = 'p-6' }) {
    return (
        <div className={`bg-white rounded-lg border border-gray-200 ${padding} ${className}`}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className = '' }) {
    return (
        <div className={`pb-4 border-b border-gray-200 mb-4 ${className}`}>
            {children}
        </div>
    );
}

export function CardTitle({ children, className = '' }) {
    return (
        <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>
            {children}
        </h3>
    );
}

export function CardContent({ children, className = '' }) {
    return (
        <div className={className}>
            {children}
        </div>
    );
}