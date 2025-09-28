import React from 'react';
import { useToast } from '../context/AppContext';
import { Toast } from './ui/Toast';

export default function ToastContainer() {
    const { toast, hideToast } = useToast();
    
    if (!toast) return null;
    
    return (
        <Toast
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={hideToast}
        />
    );
}