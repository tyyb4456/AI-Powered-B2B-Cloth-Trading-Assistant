// components/ui/EmptyState.jsx
import React from 'react';

export function EmptyState({ 
    icon: Icon, 
    title, 
    description, 
    action,
    className = '' 
}) {
    return (
        <div className={`text-center py-12 ${className}`}>
            {Icon && (
                <div className="mx-auto w-12 h-12 text-gray-400 mb-4">
                    <Icon size={48} />
                </div>
            )}
            <h3 className="text-lg font-medium text-gray-900 mb-2">
                {title}
            </h3>
            <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                {description}
            </p>
            {action && (
                <div>
                    {action}
                </div>
            )}
        </div>
    );
}