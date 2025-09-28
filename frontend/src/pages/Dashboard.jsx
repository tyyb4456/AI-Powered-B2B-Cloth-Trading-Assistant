import React from 'react';
import { Link } from 'react-router-dom';
import { 
    Plus, 
    Clock, 
    CheckCircle, 
    AlertCircle,
    TrendingUp,
    MessageCircle,
    FileText,
    Handshake
} from 'lucide-react';

export default function Dashboard() {
    // Mock data - you'll replace this with real API calls
    const stats = [
        {
            title: 'Active Sessions',
            value: '5',
            icon: Clock,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
            change: '+2 from yesterday'
        },
        {
            title: 'Pending Negotiations',
            value: '3',
            icon: Handshake,
            color: 'text-orange-600',
            bgColor: 'bg-orange-50',
            change: '1 urgent response needed'
        },
        {
            title: 'Completed Quotes',
            value: '12',
            icon: FileText,
            color: 'text-green-600',
            bgColor: 'bg-green-50',
            change: '+4 this week'
        },
        {
            title: 'Success Rate',
            value: '87%',
            icon: TrendingUp,
            color: 'text-purple-600',
            bgColor: 'bg-purple-50',
            change: '+5% improvement'
        }
    ];

    const recentActivity = [
        {
            id: 1,
            type: 'quote',
            title: 'Quote sent to Premium Textile Mills',
            description: 'Quote #QT-20241221-A4B7C2F1 for organic cotton canvas',
            time: '2 hours ago',
            status: 'success'
        },
        {
            id: 2,
            type: 'negotiation',
            title: 'Negotiation in progress with Global Fabric Solutions',
            description: 'Discussing lead time reduction from 45 to 30 days',
            time: '4 hours ago',
            status: 'pending'
        },
        {
            id: 3,
            type: 'contract',
            title: 'Contract drafted for Sustainable Textiles Co.',
            description: 'Contract ready for legal review',
            time: '1 day ago',
            status: 'success'
        },
        {
            id: 4,
            type: 'supplier',
            title: 'New supplier evaluation completed',
            description: '8 suppliers found for denim fabric requirements',
            time: '2 days ago',
            status: 'info'
        }
    ];

    const getStatusColor = (status) => {
        switch (status) {
            case 'success':
                return 'text-green-600';
            case 'pending':
                return 'text-orange-600';
            case 'error':
                return 'text-red-600';
            default:
                return 'text-blue-600';
        }
    };

    const getActivityIcon = (type) => {
        switch (type) {
            case 'quote':
                return FileText;
            case 'negotiation':
                return Handshake;
            case 'contract':
                return FileText;
            case 'supplier':
                return MessageCircle;
            default:
                return MessageCircle;
        }
    };

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-600 mt-1">
                        Welcome back! Here's your procurement overview.
                    </p>
                </div>
                
                <div className="flex space-x-3">
                    <Link
                        to="/chat"
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                    >
                        <Plus size={16} />
                        <span>New Request</span>
                    </Link>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <div key={index} className="bg-white rounded-lg p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">
                                    {stat.title}
                                </p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">
                                    {stat.value}
                                </p>
                                <p className="text-sm text-gray-500 mt-1">
                                    {stat.change}
                                </p>
                            </div>
                            <div className={`p-3 rounded-full ${stat.bgColor}`}>
                                <stat.icon size={24} className={stat.color} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Quick Actions
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Link
                        to="/chat"
                        className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                    >
                        <MessageCircle className="text-blue-600 mr-3" size={20} />
                        <div>
                            <div className="font-medium text-gray-900">
                                Start New Chat
                            </div>
                            <div className="text-sm text-gray-500">
                                Begin a new procurement request
                            </div>
                        </div>
                    </Link>

                    <Link
                        to="/negotiations"
                        className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition-colors"
                    >
                        <Handshake className="text-orange-600 mr-3" size={20} />
                        <div>
                            <div className="font-medium text-gray-900">
                                Continue Negotiation
                            </div>
                            <div className="text-sm text-gray-500">
                                Resume pending negotiations
                            </div>
                        </div>
                    </Link>

                    <Link
                        to="/suppliers"
                        className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
                    >
                        <FileText className="text-green-600 mr-3" size={20} />
                        <div>
                            <div className="font-medium text-gray-900">
                                View Suppliers
                            </div>
                            <div className="text-sm text-gray-500">
                                Manage supplier relationships
                            </div>
                        </div>
                    </Link>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Recent Activity
                </h2>
                <div className="space-y-4">
                    {recentActivity.map((activity) => {
                        const Icon = getActivityIcon(activity.type);
                        return (
                            <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                                <div className="flex-shrink-0">
                                    <Icon 
                                        size={16} 
                                        className={getStatusColor(activity.status)} 
                                    />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-900">
                                        {activity.title}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                        {activity.description}
                                    </p>
                                </div>
                                <div className="flex-shrink-0">
                                    <p className="text-xs text-gray-400">
                                        {activity.time}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                    <Link 
                        to="/chat" 
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                        View all activity →
                    </Link>
                </div>
            </div>
        </div>
    );
}