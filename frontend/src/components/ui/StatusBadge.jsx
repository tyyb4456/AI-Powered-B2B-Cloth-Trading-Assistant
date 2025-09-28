// components/ui/StatusBadge.jsx
import React from 'react';
import { CheckCircle, Clock, AlertCircle, XCircle } from 'lucide-react';

export function StatusBadge({ status, children }) {
    const getStatusStyles = (status) => {
        switch (status) {
            case 'success':
            case 'completed':
                return {
                    bg: 'bg-green-100',
                    text: 'text-green-800',
                    icon: CheckCircle
                };
            case 'pending':
            case 'processing':
                return {
                    bg: 'bg-yellow-100',
                    text: 'text-yellow-800',
                    icon: Clock
                };
            case 'error':
            case 'failed':
                return {
                    bg: 'bg-red-100',
                    text: 'text-red-800',
                    icon: XCircle
                };
            case 'warning':
                return {
                    bg: 'bg-orange-100',
                    text: 'text-orange-800',
                    icon: AlertCircle
                };
            default:
                return {
                    bg: 'bg-blue-100',
                    text: 'text-blue-800',
                    icon: Clock
                };
        }
    };

    const styles = getStatusStyles(status);
    const Icon = styles.icon;

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles.bg} ${styles.text}`}>
            <Icon size={12} className="mr-1" />
            {children || status}
        </span>
    );
}
