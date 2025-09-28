import React from 'react';
import { Menu, Bell, User, Settings } from 'lucide-react';

export default function Header({ sidebarOpen, setSidebarOpen }) {
    return (
        <header className="bg-gray-800 border-b border-gray-700 fixed w-full top-0 z-30">
            <div className="flex items-center justify-between h-16 px-4">
                {/* Left side */}
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    >
                        <Menu size={20} />
                    </button>
                    
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">TP</span>
                        </div>
                        <h1 className="text-xl font-semibold text-gray-900">
                            Textile Procurement
                        </h1>
                    </div>
                </div>

                {/* Right side */}
                <div className="flex items-center space-x-4">
                    {/* Notification bell */}
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md relative">
                        <Bell size={20} />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                    </button>

                    {/* Settings */}
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                        <Settings size={20} />
                    </button>

                    {/* User profile */}
                    <div className="flex items-center space-x-3">
                        <div className="text-right">
                            <div className="text-sm font-medium text-gray-900">
                                John Doe
                            </div>
                            <div className="text-xs text-gray-500">
                                Procurement Manager
                            </div>
                        </div>
                        <button className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full">
                            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                <User size={16} />
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}