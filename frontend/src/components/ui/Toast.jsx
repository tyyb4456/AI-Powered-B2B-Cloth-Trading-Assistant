import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';

export function Toast({ 
    message, 
    type = 'info', 
    duration = 5000, 
    onClose 
}) {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(false);
            onClose && onClose();
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    if (!isVisible) return null;

    const getToastStyles = (type) => {
        switch (type) {
            case 'success':
                return {
                    bg: 'bg-green-50',
                    border: 'border-green-200',
                    text: 'text-green-800',
                    icon: CheckCircle,
                    iconColor: 'text-green-400'
                };
            case 'error':
                return {
                    bg: 'bg-red-50',
                    border: 'border-red-200',
                    text: 'text-red-800',
                    icon: XCircle,
                    iconColor: 'text-red-400'
                };
            case 'warning':
                return {
                    bg: 'bg-yellow-50',
                    border: 'border-yellow-200',
                    text: 'text-yellow-800',
                    icon: AlertCircle,
                    iconColor: 'text-yellow-400'
                };
            default:
                return {
                    bg: 'bg-blue-50',
                    border: 'border-blue-200',
                    text: 'text-blue-800',
                    icon: AlertCircle,
                    iconColor: 'text-blue-400'
                };
        }
    };

    const styles = getToastStyles(type);
    const Icon = styles.icon;

    return (
        <div className={`fixed top-20 right-4 max-w-sm w-full ${styles.bg} border ${styles.border} rounded-lg shadow-lg p-4 z-50 fade-in`}>
            <div className="flex items-start">
                <Icon size={20} className={`${styles.iconColor} mt-0.5`} />
                <div className="ml-3 flex-1">
                    <p className={`text-sm ${styles.text}`}>
                        {message}
                    </p>
                </div>
                <button
                    onClick={() => {
                        setIsVisible(false);
                        onClose && onClose();
                    }}
                    className={`ml-4 ${styles.text} hover:opacity-70`}
                >
                    <X size={16} />
                </button>
            </div>
        </div>
    );
}