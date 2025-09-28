import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
    FileText, 
    Download, 
    Share2, 
    Eye, 
    Edit, 
    Copy,
    Printer,
    Calendar,
    DollarSign,
    Package,
    Clock,
    User,
    Building,
    ChevronRight,
    ChevronDown,
    BarChart3,
    TrendingUp,
    MessageCircle,
    CheckCircle,
    AlertCircle,
    RefreshCw
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';

export default function Quotes() {
    const { sessionId } = useParams();
    const { state, actions } = useApp();
    
    const [quotes, setQuotes] = useState([]);
    const [selectedQuote, setSelectedQuote] = useState(null);
    const [loading, setLoading] = useState(false);
    const [viewMode, setViewMode] = useState('list'); // 'list', 'document', 'breakdown'
    const [expandedSections, setExpandedSections] = useState({
        items: true,
        pricing: true,
        terms: true
    });

    useEffect(() => {
        if (sessionId) {
            loadQuotes();
        } else {
            loadMockQuotes();
        }
    }, [sessionId]);

    const loadQuotes = async () => {
        try {
            setLoading(true);
            const response = await apiService.getGeneratedQuotes(sessionId);
            const quotesArray = Array.isArray(response.generated_quote) 
                ? response.generated_quote 
                : [response.generated_quote];
            setQuotes(quotesArray);
            if (quotesArray.length > 0) {
                setSelectedQuote(quotesArray[0]);
            }
        } catch (error) {
            console.error('Error loading quotes:', error);
            actions.showToast('Failed to load quotes', 'error');
            loadMockQuotes();
        } finally {
            setLoading(false);
        }
    };

    const loadMockQuotes = () => {
        const mockQuotes = [
            {
                id: 'QT-20241221-A4B7C2F1',
                version: '2.1',
                status: 'active',
                created_date: '2024-12-21',
                expiry_date: '2025-01-21',
                client: {
                    name: 'Fashion Forward Inc.',
                    contact: 'Sarah Johnson',
                    email: 'sarah@fashionforward.com',
                    company_address: '123 Style Street, New York, NY 10001'
                },
                supplier: {
                    name: 'Premium Textile Mills',
                    contact: 'Rajesh Kumar',
                    email: 'sales@premiumtextiles.com',
                    company_address: 'Sector 15, Mumbai, Maharashtra 400001'
                },
                items: [
                    {
                        id: 1,
                        description: 'Organic Cotton Canvas - GOTS Certified',
                        specifications: {
                            weight: '300 GSM',
                            width: '150 cm',
                            composition: '100% Organic Cotton',
                            color: 'Natural White',
                            finish: 'Plain Weave'
                        },
                        quantity: 5000,
                        unit: 'meters',
                        unit_price: 6.75,
                        total_price: 33750
                    },
                    {
                        id: 2,
                        description: 'Cotton Canvas - Standard Grade',
                        specifications: {
                            weight: '280 GSM',
                            width: '150 cm',
                            composition: '100% Cotton',
                            color: 'Off-White',
                            finish: 'Plain Weave'
                        },
                        quantity: 3000,
                        unit: 'meters',
                        unit_price: 4.25,
                        total_price: 12750
                    }
                ],
                pricing: {
                    subtotal: 46500,
                    shipping: 2850,
                    insurance: 465,
                    taxes: 0,
                    total: 49815,
                    currency: 'USD',
                    payment_terms: '30% advance, 70% against delivery',
                    price_validity: '30 days from quote date'
                },
                logistics: {
                    lead_time: '25-30 days',
                    shipping_method: 'Sea Freight (CIF)',
                    packaging: 'Roll packed in waterproof covers',
                    origin: 'Mumbai, India',
                    destination: 'New York, USA'
                },
                terms: [
                    'Prices are valid for 30 days from quote date',
                    'Payment: 30% advance, 70% against delivery',
                    'Lead time: 25-30 days from order confirmation',
                    'Quality control inspection included',
                    'GOTS certification provided for organic items',
                    'Force majeure clause applicable'
                ],
                notes: 'Special attention to packaging for ocean freight. Quality inspection report will be provided before shipment.',
                versions: [
                    { version: '2.1', date: '2024-12-21', changes: 'Updated shipping costs and lead time' },
                    { version: '2.0', date: '2024-12-20', changes: 'Added cotton canvas option' },
                    { version: '1.0', date: '2024-12-19', changes: 'Initial quote' }
                ]
            },
            {
                id: 'QT-20241220-B8E9F3A2',
                version: '1.0',
                status: 'expired',
                created_date: '2024-11-20',
                expiry_date: '2024-12-20',
                client: {
                    name: 'Urban Apparel Co.',
                    contact: 'Mike Chen',
                    email: 'mike@urbanapparel.com',
                    company_address: '456 Fashion Ave, Los Angeles, CA 90210'
                },
                supplier: {
                    name: 'Global Fabric Solutions',
                    contact: 'Mehmet Ozkan',
                    email: 'info@globalfabrics.com.tr',
                    company_address: 'Tekstil District, Istanbul, Turkey'
                },
                items: [
                    {
                        id: 1,
                        description: 'Premium Denim Fabric',
                        specifications: {
                            weight: '340 GSM',
                            width: '150 cm',
                            composition: '98% Cotton, 2% Elastane',
                            color: 'Indigo Blue',
                            finish: 'Sanforized'
                        },
                        quantity: 10000,
                        unit: 'yards',
                        unit_price: 5.80,
                        total_price: 58000
                    }
                ],
                pricing: {
                    subtotal: 58000,
                    shipping: 3200,
                    insurance: 580,
                    taxes: 0,
                    total: 61780,
                    currency: 'USD',
                    payment_terms: '50% advance, 50% against BL copy',
                    price_validity: '30 days from quote date'
                },
                logistics: {
                    lead_time: '20-25 days',
                    shipping_method: 'Sea Freight (FOB)',
                    packaging: 'Tube packed',
                    origin: 'Istanbul, Turkey',
                    destination: 'Los Angeles, USA'
                },
                terms: [
                    'Prices are valid for 30 days from quote date',
                    'Payment: 50% advance, 50% against BL copy',
                    'Lead time: 20-25 days from order confirmation',
                    'Pre-shipment inspection available',
                    'Sanforized treatment included'
                ],
                versions: [
                    { version: '1.0', date: '2024-11-20', changes: 'Initial quote' }
                ]
            }
        ];
        setQuotes(mockQuotes);
        if (mockQuotes.length > 0) {
            setSelectedQuote(mockQuotes[0]);
        }
    };

    const toggleSection = (section) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'active':
                return 'text-green-600 bg-green-100';
            case 'expired':
                return 'text-red-600 bg-red-100';
            case 'draft':
                return 'text-yellow-600 bg-yellow-100';
            case 'accepted':
                return 'text-blue-600 bg-blue-100';
            default:
                return 'text-gray-600 bg-gray-100';
        }
    };

    const formatCurrency = (amount, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const QuoteListItem = ({ quote }) => (
        <div 
            className={`bg-white rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedQuote?.id === quote.id ? 'ring-2 ring-blue-500 border-blue-200' : 'border-gray-200'
            }`}
            onClick={() => setSelectedQuote(quote)}
        >
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                            {quote.id}
                        </h3>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(quote.status)}`}>
                            {quote.status}
                        </span>
                        <span className="text-sm text-gray-500">v{quote.version}</span>
                    </div>
                    
                    <div className="mt-2 grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div className="flex items-center">
                            <Building size={14} className="mr-2" />
                            {quote.client.name}
                        </div>
                        <div className="flex items-center">
                            <Calendar size={14} className="mr-2" />
                            {formatDate(quote.created_date)}
                        </div>
                        <div className="flex items-center">
                            <DollarSign size={14} className="mr-2" />
                            {formatCurrency(quote.pricing.total, quote.pricing.currency)}
                        </div>
                        <div className="flex items-center">
                            <Clock size={14} className="mr-2" />
                            Expires {formatDate(quote.expiry_date)}
                        </div>
                    </div>
                </div>
                
                <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                        <Eye size={16} />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                        <Share2 size={16} />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
                        <Download size={16} />
                    </button>
                </div>
            </div>
        </div>
    );

    const QuoteDocument = ({ quote }) => {
        if (!quote) return null;

        return (
            <div className="bg-white rounded-lg border border-gray-200 p-8 max-w-4xl mx-auto">
                {/* Header */}
                <div className="border-b border-gray-200 pb-6 mb-6">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">QUOTATION</h1>
                            <p className="text-lg text-gray-600 mt-1">#{quote.id}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-600">Quote Date</p>
                            <p className="font-semibold">{formatDate(quote.created_date)}</p>
                            <p className="text-sm text-gray-600 mt-2">Valid Until</p>
                            <p className="font-semibold">{formatDate(quote.expiry_date)}</p>
                        </div>
                    </div>
                </div>

                {/* Company Info */}
                <div className="grid grid-cols-2 gap-8 mb-8">
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-3">FROM:</h3>
                        <div className="text-sm text-gray-600">
                            <p className="font-semibold text-gray-900">{quote.supplier.name}</p>
                            <p>{quote.supplier.contact}</p>
                            <p>{quote.supplier.email}</p>
                            <p className="mt-2">{quote.supplier.company_address}</p>
                        </div>
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-3">TO:</h3>
                        <div className="text-sm text-gray-600">
                            <p className="font-semibold text-gray-900">{quote.client.name}</p>
                            <p>{quote.client.contact}</p>
                            <p>{quote.client.email}</p>
                            <p className="mt-2">{quote.client.company_address}</p>
                        </div>
                    </div>
                </div>

                {/* Items Section */}
                <div className="mb-8">
                    <div 
                        className="flex items-center justify-between cursor-pointer p-3 bg-gray-50 rounded-lg mb-4"
                        onClick={() => toggleSection('items')}
                    >
                        <h3 className="text-lg font-semibold text-gray-900">Items & Specifications</h3>
                        {expandedSections.items ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </div>
                    
                    {expandedSections.items && (
                        <div className="overflow-x-auto">
                            <table className="min-w-full border border-gray-200 rounded-lg">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Item</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Specifications</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Quantity</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Unit Price</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Total</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {quote.items.map((item, index) => (
                                        <tr key={index} className="hover:bg-gray-50">
                                            <td className="px-4 py-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {item.description}
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="text-sm text-gray-600 space-y-1">
                                                    {Object.entries(item.specifications).map(([key, value]) => (
                                                        <div key={key} className="flex">
                                                            <span className="font-medium w-20 capitalize">{key}:</span>
                                                            <span>{value}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="text-sm text-gray-900">
                                                    {item.quantity.toLocaleString()} {item.unit}
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="text-sm text-gray-900">
                                                    {formatCurrency(item.unit_price, quote.pricing.currency)}
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {formatCurrency(item.total_price, quote.pricing.currency)}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Pricing Section */}
                <div className="mb-8">
                    <div 
                        className="flex items-center justify-between cursor-pointer p-3 bg-gray-50 rounded-lg mb-4"
                        onClick={() => toggleSection('pricing')}
                    >
                        <h3 className="text-lg font-semibold text-gray-900">Pricing & Payment</h3>
                        {expandedSections.pricing ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </div>
                    
                    {expandedSections.pricing && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Pricing Breakdown */}
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-900 mb-3">Cost Breakdown</h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span>Subtotal:</span>
                                        <span className="font-medium">{formatCurrency(quote.pricing.subtotal, quote.pricing.currency)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Shipping:</span>
                                        <span className="font-medium">{formatCurrency(quote.pricing.shipping, quote.pricing.currency)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Insurance:</span>
                                        <span className="font-medium">{formatCurrency(quote.pricing.insurance, quote.pricing.currency)}</span>
                                    </div>
                                    {quote.pricing.taxes > 0 && (
                                        <div className="flex justify-between">
                                            <span>Taxes:</span>
                                            <span className="font-medium">{formatCurrency(quote.pricing.taxes, quote.pricing.currency)}</span>
                                        </div>
                                    )}
                                    <div className="border-t border-gray-300 pt-2 mt-3">
                                        <div className="flex justify-between font-bold text-lg">
                                            <span>Total:</span>
                                            <span>{formatCurrency(quote.pricing.total, quote.pricing.currency)}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Payment & Logistics */}
                            <div className="space-y-4">
                                <div className="bg-blue-50 p-4 rounded-lg">
                                    <h4 className="font-semibold text-gray-900 mb-2">Payment Terms</h4>
                                    <p className="text-sm text-gray-700">{quote.pricing.payment_terms}</p>
                                    <p className="text-sm text-gray-600 mt-1">Valid: {quote.pricing.price_validity}</p>
                                </div>
                                
                                <div className="bg-green-50 p-4 rounded-lg">
                                    <h4 className="font-semibold text-gray-900 mb-2">Logistics</h4>
                                    <div className="text-sm text-gray-700 space-y-1">
                                        <p><strong>Lead Time:</strong> {quote.logistics.lead_time}</p>
                                        <p><strong>Shipping:</strong> {quote.logistics.shipping_method}</p>
                                        <p><strong>Packaging:</strong> {quote.logistics.packaging}</p>
                                        <p><strong>Route:</strong> {quote.logistics.origin} → {quote.logistics.destination}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Terms & Conditions */}
                <div className="mb-8">
                    <div 
                        className="flex items-center justify-between cursor-pointer p-3 bg-gray-50 rounded-lg mb-4"
                        onClick={() => toggleSection('terms')}
                    >
                        <h3 className="text-lg font-semibold text-gray-900">Terms & Conditions</h3>
                        {expandedSections.terms ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </div>
                    
                    {expandedSections.terms && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <ul className="list-disc list-inside space-y-2 text-sm text-gray-700">
                                {quote.terms.map((term, index) => (
                                    <li key={index}>{term}</li>
                                ))}
                            </ul>
                            
                            {quote.notes && (
                                <div className="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-400">
                                    <p className="text-sm font-medium text-yellow-800">Special Notes:</p>
                                    <p className="text-sm text-yellow-700 mt-1">{quote.notes}</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 pt-6 text-center text-sm text-gray-600">
                    <p>Thank you for your business consideration.</p>
                    <p className="mt-1">This quotation is computer generated and valid without signature.</p>
                </div>
            </div>
        );
    };

    const PriceBreakdownChart = ({ quote }) => {
        if (!quote) return null;

        const total = quote.pricing.total;
        const segments = [
            { label: 'Materials', value: quote.pricing.subtotal, color: 'bg-blue-500' },
            { label: 'Shipping', value: quote.pricing.shipping, color: 'bg-green-500' },
            { label: 'Insurance', value: quote.pricing.insurance, color: 'bg-yellow-500' },
            { label: 'Taxes', value: quote.pricing.taxes, color: 'bg-red-500' }
        ];

        return (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Breakdown Analysis</h3>
                
                {/* Bar Chart */}
                <div className="mb-6">
                    <div className="flex h-8 rounded-lg overflow-hidden">
                        {segments.map((segment, index) => {
                            const percentage = (segment.value / total) * 100;
                            if (percentage === 0) return null;
                            
                            return (
                                <div
                                    key={index}
                                    className={`${segment.color} flex items-center justify-center text-white text-sm font-medium`}
                                    style={{ width: `${percentage}%` }}
                                    title={`${segment.label}: ${formatCurrency(segment.value)} (${percentage.toFixed(1)}%)`}
                                >
                                    {percentage > 10 && `${percentage.toFixed(0)}%`}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Legend */}
                <div className="grid grid-cols-2 gap-4">
                    {segments.map((segment, index) => {
                        const percentage = (segment.value / total) * 100;
                        if (percentage === 0) return null;
                        
                        return (
                            <div key={index} className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className={`w-3 h-3 ${segment.color} rounded-full mr-2`}></div>
                                    <span className="text-sm text-gray-600">{segment.label}</span>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-medium">{formatCurrency(segment.value)}</div>
                                    <div className="text-xs text-gray-500">{percentage.toFixed(1)}%</div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Savings Potential */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">Cost Optimization Insights</h4>
                    <div className="text-sm text-blue-800 space-y-1">
                        <p>• Shipping represents {((quote.pricing.shipping / total) * 100).toFixed(1)}% of total cost</p>
                        <p>• Consider bulk ordering to reduce per-unit shipping costs</p>
                        <p>• Insurance coverage: ${quote.pricing.insurance.toFixed(2)} ({((quote.pricing.insurance / total) * 100).toFixed(1)}%)</p>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Quote Management</h1>
                    <p className="text-gray-600 mt-1">
                        {sessionId 
                            ? `Quotes for session ${sessionId.slice(0, 8)}...`
                            : 'Manage your textile procurement quotes'
                        }
                    </p>
                </div>
                
                <div className="flex items-center space-x-3">
                    {!sessionId && (
                        <Link
                            to="/chat"
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
                        >
                            <MessageCircle size={16} className="mr-2" />
                            Generate Quote
                        </Link>
                    )}
                </div>
            </div>

            {/* Loading State */}
            {loading && (
                <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="mt-2 text-gray-600">Loading quotes...</p>
                </div>
            )}

            {/* Main Content */}
            {!loading && (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Quotes List */}
                    <div className="lg:col-span-1">
                        <div className="bg-gray-50 rounded-lg p-4 mb-4">
                            <h2 className="font-semibold text-gray-900 mb-3">Quotes ({quotes.length})</h2>
                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={() => setViewMode('list')}
                                    className={`px-3 py-1 text-sm rounded-md ${
                                        viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-900'
                                    }`}
                                >
                                    List
                                </button>
                                <button
                                    onClick={() => setViewMode('document')}
                                    className={`px-3 py-1 text-sm rounded-md ${
                                        viewMode === 'document' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-900'
                                    }`}
                                >
                                    Document
                                </button>
                                <button
                                    onClick={() => setViewMode('breakdown')}
                                    className={`px-3 py-1 text-sm rounded-md ${
                                        viewMode === 'breakdown' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-900'
                                    }`}
                                >
                                    Analysis
                                </button>
                            </div>
                        </div>
                        
                        <div className="space-y-3">
                            {quotes.map((quote) => (
                                <QuoteListItem key={quote.id} quote={quote} />
                            ))}
                        </div>

                        {quotes.length === 0 && (
                            <div className="text-center py-8">
                                <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No quotes found</h3>
                                <p className="text-gray-500 mb-4">
                                    {sessionId 
                                        ? 'No quotes available for this session'
                                        : 'Start a procurement workflow to generate quotes'
                                    }
                                </p>
                                {!sessionId && (
                                    <Link
                                        to="/chat"
                                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                    >
                                        <MessageCircle size={16} className="mr-2" />
                                        Generate Quote
                                    </Link>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Quote Content */}
                    <div className="lg:col-span-3">
                        {selectedQuote ? (
                            <div className="space-y-4">
                                {/* Quote Actions */}
                                <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
                                    <div className="flex items-center space-x-4">
                                        <h2 className="text-xl font-semibold text-gray-900">
                                            {selectedQuote.id}
                                        </h2>
                                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedQuote.status)}`}>
                                            {selectedQuote.status}
                                        </span>
                                        <span className="text-sm text-gray-500">Version {selectedQuote.version}</span>
                                    </div>
                                    
                                    <div className="flex items-center space-x-2">
                                        <button className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50">
                                            <Edit size={14} className="mr-2" />
                                            Edit
                                        </button>
                                        <button className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50">
                                            <Copy size={14} className="mr-2" />
                                            Duplicate
                                        </button>
                                        <button className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50">
                                            <Share2 size={14} className="mr-2" />
                                            Share
                                        </button>
                                        <button className="flex items-center px-3 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700">
                                            <Download size={14} className="mr-2" />
                                            Export PDF
                                        </button>
                                        <button className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50">
                                            <Printer size={14} className="mr-2" />
                                            Print
                                        </button>
                                    </div>
                                </div>

                                {/* Version History */}
                                {selectedQuote.versions && selectedQuote.versions.length > 1 && (
                                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                                        <h3 className="text-sm font-semibold text-gray-900 mb-3">Version History</h3>
                                        <div className="space-y-2">
                                            {selectedQuote.versions.map((version, index) => (
                                                <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-md">
                                                    <div className="flex items-center space-x-3">
                                                        <span className={`px-2 py-1 text-xs rounded-md ${
                                                            version.version === selectedQuote.version 
                                                                ? 'bg-blue-100 text-blue-700' 
                                                                : 'bg-gray-100 text-gray-600'
                                                        }`}>
                                                            v{version.version}
                                                        </span>
                                                        <span className="text-sm text-gray-600">{formatDate(version.date)}</span>
                                                        <span className="text-sm text-gray-500">{version.changes}</span>
                                                    </div>
                                                    {version.version !== selectedQuote.version && (
                                                        <button className="text-xs text-blue-600 hover:text-blue-700">
                                                            Compare
                                                        </button>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Quote Content Based on View Mode */}
                                {viewMode === 'document' && <QuoteDocument quote={selectedQuote} />}
                                {viewMode === 'breakdown' && <PriceBreakdownChart quote={selectedQuote} />}
                                {viewMode === 'list' && (
                                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                            {/* Summary Cards */}
                                            <div className="bg-blue-50 p-4 rounded-lg">
                                                <div className="flex items-center">
                                                    <DollarSign size={20} className="text-blue-600 mr-2" />
                                                    <div>
                                                        <p className="text-sm text-blue-600 font-medium">Total Value</p>
                                                        <p className="text-xl font-bold text-blue-900">
                                                            {formatCurrency(selectedQuote.pricing.total, selectedQuote.pricing.currency)}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="bg-green-50 p-4 rounded-lg">
                                                <div className="flex items-center">
                                                    <Package size={20} className="text-green-600 mr-2" />
                                                    <div>
                                                        <p className="text-sm text-green-600 font-medium">Items</p>
                                                        <p className="text-xl font-bold text-green-900">
                                                            {selectedQuote.items.length} Products
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="bg-yellow-50 p-4 rounded-lg">
                                                <div className="flex items-center">
                                                    <Clock size={20} className="text-yellow-600 mr-2" />
                                                    <div>
                                                        <p className="text-sm text-yellow-600 font-medium">Lead Time</p>
                                                        <p className="text-xl font-bold text-yellow-900">
                                                            {selectedQuote.logistics.lead_time}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Quick Details */}
                                        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                                            <div>
                                                <h4 className="font-semibold text-gray-900 mb-3">Client Information</h4>
                                                <div className="space-y-2 text-sm text-gray-600">
                                                    <p><span className="font-medium">Company:</span> {selectedQuote.client.name}</p>
                                                    <p><span className="font-medium">Contact:</span> {selectedQuote.client.contact}</p>
                                                    <p><span className="font-medium">Email:</span> {selectedQuote.client.email}</p>
                                                </div>
                                            </div>

                                            <div>
                                                <h4 className="font-semibold text-gray-900 mb-3">Supplier Information</h4>
                                                <div className="space-y-2 text-sm text-gray-600">
                                                    <p><span className="font-medium">Company:</span> {selectedQuote.supplier.name}</p>
                                                    <p><span className="font-medium">Contact:</span> {selectedQuote.supplier.contact}</p>
                                                    <p><span className="font-medium">Email:</span> {selectedQuote.supplier.email}</p>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Recent Activity */}
                                        <div className="mt-6">
                                            <h4 className="font-semibold text-gray-900 mb-3">Recent Activity</h4>
                                            <div className="space-y-3">
                                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                                    <CheckCircle size={16} className="text-green-500 mt-0.5" />
                                                    <div className="flex-1">
                                                        <p className="text-sm font-medium text-gray-900">Quote Generated</p>
                                                        <p className="text-xs text-gray-500">{formatDate(selectedQuote.created_date)}</p>
                                                    </div>
                                                </div>
                                                
                                                {selectedQuote.versions.length > 1 && (
                                                    <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                                        <RefreshCw size={16} className="text-blue-500 mt-0.5" />
                                                        <div className="flex-1">
                                                            <p className="text-sm font-medium text-gray-900">Quote Updated</p>
                                                            <p className="text-xs text-gray-500">
                                                                Version {selectedQuote.versions[0].version} - {selectedQuote.versions[0].changes}
                                                            </p>
                                                        </div>
                                                    </div>
                                                )}

                                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                                    <AlertCircle size={16} className="text-yellow-500 mt-0.5" />
                                                    <div className="flex-1">
                                                        <p className="text-sm font-medium text-gray-900">
                                                            {selectedQuote.status === 'active' ? 'Awaiting Response' : 'Quote Expired'}
                                                        </p>
                                                        <p className="text-xs text-gray-500">
                                                            Expires on {formatDate(selectedQuote.expiry_date)}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                                <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Quote</h3>
                                <p className="text-gray-500">Choose a quote from the list to view details</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}