'use client';

import { useEffect } from 'react';
import { Loader2, X } from 'lucide-react';

interface AnalysisProgressModalProps {
    isOpen: boolean;
    progress: number;
    status: string;
    companyName: string;
    onClose?: () => void;
}

export function AnalysisProgressModal({
    isOpen,
    progress,
    status,
    companyName,
    onClose,
}: AnalysisProgressModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Analyzing {companyName}</h2>
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    )}
                </div>

                {/* Progress Bar */}
                <div className="mb-6">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>{status}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                {/* Status Message */}
                <div className="flex items-center gap-3 text-sm text-gray-600">
                    <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                    <p>This usually takes 30-60 seconds. Please wait...</p>
                </div>
            </div>
        </div>
    );
}
