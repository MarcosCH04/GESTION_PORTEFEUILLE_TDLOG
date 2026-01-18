// frontend/src/components/Toast.jsx

/* Displays temporary success/error messages that appear in the top-right corner */
import React, { useEffect } from 'react';

function Toast({ message, type = 'error', onClose }) {
    // Auto-dismiss the toast after 5 seconds 
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 5000); 

        return () => clearTimeout(timer);
    }, [onClose]);

    const bgColor = type === 'error' ? 'bg-red-500' : 'bg-green-500';

    return (
        <div className={`toast ${bgColor} text-white px-6 py-4 rounded-xl shadow-2xl max-w-md`}>
            <div className="flex items-start gap-3">
                <span className="text-2xl">
                    {type === 'error' ? '⚠️' : '✅'}
                </span>
                <div className="flex-1">
                    <p className="font-semibold mb-1">
                        {type === 'error' ? 'Error' : 'Success'}
                    </p>
                    <p className="text-sm opacity-90">{message}</p>
                </div>
                <button 
                    onClick={onClose}
                    className="text-white hover:text-gray-200 text-xl"
                >
                    ×
                </button>
            </div>
        </div>
    );
}

export default Toast;