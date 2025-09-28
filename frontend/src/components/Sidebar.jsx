import React from 'react';
import {NavLink } from 'react-router-dom';
import { 
    LayoutDashboard, 
    MessageCircle, 
    Users, 
    FileText, 
    Handshake, 
    FileSignature,  // ✅ replacing FileContract
    ChevronLeft
} from 'lucide-react';


export default function Sidebar({ isOpen, setSidebarOpen }) {
    const navItems = [
        {
            name: 'Dashboard',
            path: '/',
            icon: LayoutDashboard,
            description: 'Overview & Analytics'
        },
        {
            name: 'Chat',
            path: '/chat',
            icon: MessageCircle,
            description: 'AI Assistant Chat'
        },
        {
            name: 'Suppliers',
            path: '/suppliers',
            icon: Users,
            description: 'Supplier Management'
        },
        {
            name: 'Quotes',
            path: '/quotes',
            icon: FileText,
            description: 'Quote Generation'
        },
        {
            name: 'Negotiations',
            path: '/negotiations',
            icon: Handshake,
            description: 'Negotiation Center'
        },
        {
            name: 'Contracts',
            path: '/contracts',
            icon: FileSignature,
            description: 'Contract Management'
        }
    ];

    return (
        <aside className={`bg-white border-r border-gray-200 fixed left-0 top-16 h-full transition-all duration-300 z-20 ${
            isOpen ? 'w-64' : 'w-16'
        }`}>
            {/* Sidebar header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
                {isOpen && (
                    <h2 className="text-lg font-semibold text-gray-900">
                        Navigation
                    </h2>
                )}
                <button
                    onClick={() => setSidebarOpen(!isOpen)}
                    className="p-1 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                >
                    <ChevronLeft 
                        size={16} 
                        className={`transform transition-transform ${!isOpen ? 'rotate-180' : ''}`} 
                    />
                </button>
            </div>

            {/* Navigation items */}
            <nav className="p-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center px-3 py-3 rounded-lg transition-colors group ${
                                isActive
                                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                            }`
                        }
                        end={item.path === '/'}
                    >
                        <item.icon 
                            size={20} 
                            className={`${isOpen ? 'mr-3' : 'mx-auto'}`} 
                        />
                        
                        {isOpen && (
                            <div className="flex-1">
                                <div className="font-medium">
                                    {item.name}
                                </div>
                                <div className="text-xs text-gray-500 mt-0.5">
                                    {item.description}
                                </div>
                            </div>
                        )}
                        
                        {/* Tooltip for collapsed sidebar */}
                        {!isOpen && (
                            <div className="absolute left-16 bg-gray-900 text-white px-2 py-1 rounded text-sm opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                                {item.name}
                                <div className="text-xs text-gray-300">
                                    {item.description}
                                </div>
                            </div>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* Bottom section */}
            <div className="absolute bottom-4 left-4 right-4">
                {isOpen && (
                    <div className="bg-blue-50 rounded-lg p-3">
                        <div className="text-sm font-medium text-blue-900">
                            Need Help?
                        </div>
                        <div className="text-xs text-blue-700 mt-1">
                            Check our documentation or contact support
                        </div>
                    </div>
                )}
            </div>
        </aside>
    );
}