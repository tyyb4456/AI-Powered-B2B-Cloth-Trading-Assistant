import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
    Users, 
    MapPin, 
    Clock, 
    DollarSign, 
    Star, 
    Shield, 
    Mail, 
    Phone, 
    Eye,
    Filter,
    ArrowUpDown,
    Award,
    Package,
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    ExternalLink
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';

export default function Suppliers() {
    const { sessionId } = useParams();
    const { state, actions } = useApp();
    
    const [suppliers, setSuppliers] = useState([]);
    const [searchResults, setSearchResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedSupplier, setSelectedSupplier] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [sortBy, setSortBy] = useState('overall_score');
    const [filterBy, setFilterBy] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (sessionId) {
            loadSuppliers();
        }
    }, [sessionId]);

    const loadSuppliers = async () => {
        try {
            setIsLoading(true);
            const data = await apiService.getTopSuppliers(sessionId);
            setSuppliers(data.top_suppliers || []);
            setSearchResults({
                search_confidence: data.search_confidence,
                market_insights: data.market_insights,
                alternative_suggestions: data.alternative_suggestions
            });
        } catch (error) {
            console.error('Error loading suppliers:', error);
            actions.showToast('Failed to load suppliers', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    // Filter and sort suppliers
    const filteredSuppliers = suppliers
        .filter(supplier => {
            const matchesSearch = searchTerm === '' || 
                supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                supplier.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
                supplier.specialties.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
            
            const matchesFilter = filterBy === 'all' ||
                (filterBy === 'certified' && supplier.certifications.length > 0) ||
                (filterBy === 'high-score' && supplier.overall_score >= 80) ||
                (filterBy === 'fast-delivery' && supplier.lead_time_days && supplier.lead_time_days <= 20) ||
                (filterBy === 'low-price' && supplier.price_per_unit && supplier.price_per_unit <= 5.0);
            
            return matchesSearch && matchesFilter;
        })
        .sort((a, b) => {
            switch (sortBy) {
                case 'overall_score':
                    return b.overall_score - a.overall_score;
                case 'price':
                    return (a.price_per_unit || 999) - (b.price_per_unit || 999);
                case 'lead_time':
                    return (a.lead_time_days || 999) - (b.lead_time_days || 999);
                case 'reputation':
                    return b.reputation_score - a.reputation_score;
                case 'name':
                    return a.name.localeCompare(b.name);
                default:
                    return 0;
            }
        });

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-green-600 bg-green-50';
        if (score >= 60) return 'text-yellow-600 bg-yellow-50';
        return 'text-red-600 bg-red-50';
    };

    const getReputationStars = (score) => {
        const stars = Math.round(score);
        return Array.from({ length: 5 }, (_, i) => (
            <Star 
                key={i} 
                size={14} 
                className={i < stars ? 'text-yellow-400 fill-current' : 'text-gray-300'} 
            />
        ));
    };

    const formatPrice = (price) => {
        return price ? `$${price.toFixed(2)}` : 'Contact for pricing';
    };

    const SupplierCard = ({ supplier }) => (
        <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">{supplier.name}</h3>
                    <div className="flex items-center text-sm text-gray-500 mt-1">
                        <MapPin size={14} className="mr-1" />
                        {supplier.location}
                    </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(supplier.overall_score)}`}>
                    {supplier.overall_score.toFixed(1)}
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center">
                    <DollarSign size={16} className="text-green-600 mr-2" />
                    <div>
                        <div className="text-sm font-medium text-gray-900">
                            {formatPrice(supplier.price_per_unit)}
                        </div>
                        <div className="text-xs text-gray-500">per meter</div>
                    </div>
                </div>
                
                <div className="flex items-center">
                    <Clock size={16} className="text-blue-600 mr-2" />
                    <div>
                        <div className="text-sm font-medium text-gray-900">
                            {supplier.lead_time_days || 'TBD'} days
                        </div>
                        <div className="text-xs text-gray-500">lead time</div>
                    </div>
                </div>

                <div className="flex items-center">
                    <Package size={16} className="text-orange-600 mr-2" />
                    <div>
                        <div className="text-sm font-medium text-gray-900">
                            {supplier.minimum_order_qty ? `${supplier.minimum_order_qty.toLocaleString()}` : 'Flexible'}
                        </div>
                        <div className="text-xs text-gray-500">min order</div>
                    </div>
                </div>

                <div className="flex items-center">
                    <div className="flex mr-2">
                        {getReputationStars(supplier.reputation_score)}
                    </div>
                    <div>
                        <div className="text-sm font-medium text-gray-900">
                            {supplier.reputation_score.toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-500">reputation</div>
                    </div>
                </div>
            </div>

            {/* Specialties */}
            <div className="mb-4">
                <div className="text-sm font-medium text-gray-700 mb-2">Specialties</div>
                <div className="flex flex-wrap gap-2">
                    {supplier.specialties.slice(0, 3).map((specialty, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md text-xs">
                            {specialty}
                        </span>
                    ))}
                    {supplier.specialties.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs">
                            +{supplier.specialties.length - 3} more
                        </span>
                    )}
                </div>
            </div>

            {/* Certifications */}
            {supplier.certifications.length > 0 && (
                <div className="mb-4">
                    <div className="text-sm font-medium text-gray-700 mb-2">Certifications</div>
                    <div className="flex flex-wrap gap-2">
                        {supplier.certifications.slice(0, 2).map((cert, index) => (
                            <span key={index} className="flex items-center px-2 py-1 bg-green-100 text-green-700 rounded-md text-xs">
                                <Shield size={12} className="mr-1" />
                                {cert}
                            </span>
                        ))}
                        {supplier.certifications.length > 2 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs">
                                +{supplier.certifications.length - 2} more
                            </span>
                        )}
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t border-gray-100">
                <button 
                    onClick={() => {
                        setSelectedSupplier(supplier);
                        setShowModal(true);
                    }}
                    className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                    <Eye size={14} className="mr-2" />
                    View Details
                </button>
                {supplier.contact_info?.email && (
                    <button className="flex items-center justify-center px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 text-sm">
                        <Mail size={14} className="mr-2" />
                        Contact
                    </button>
                )}
            </div>
        </div>
    );

    const SupplierModal = ({ supplier, onClose }) => {
        if (!supplier) return null;

        return (
            <div className="fixed inset-0 z-50 overflow-y-auto">
                <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
                    <div 
                        className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
                        onClick={onClose}
                    />

                    <div className="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
                        {/* Header */}
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-xl font-semibold text-gray-900">{supplier.name}</h3>
                                <p className="text-gray-600 flex items-center mt-1">
                                    <MapPin size={16} className="mr-1" />
                                    {supplier.location}
                                </p>
                            </div>
                            <div className={`px-4 py-2 rounded-full font-medium ${getScoreColor(supplier.overall_score)}`}>
                                Overall Score: {supplier.overall_score.toFixed(1)}
                            </div>
                        </div>

                        {/* Detailed Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <DollarSign className="mx-auto mb-2 text-green-600" size={24} />
                                <div className="font-semibold text-gray-900">{formatPrice(supplier.price_per_unit)}</div>
                                <div className="text-sm text-gray-500">Price/Unit</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <Clock className="mx-auto mb-2 text-blue-600" size={24} />
                                <div className="font-semibold text-gray-900">{supplier.lead_time_days || 'TBD'} days</div>
                                <div className="text-sm text-gray-500">Lead Time</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <Package className="mx-auto mb-2 text-orange-600" size={24} />
                                <div className="font-semibold text-gray-900">{supplier.minimum_order_qty?.toLocaleString() || 'Flexible'}</div>
                                <div className="text-sm text-gray-500">Min Order</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <Star className="mx-auto mb-2 text-yellow-600" size={24} />
                                <div className="font-semibold text-gray-900">{supplier.reputation_score.toFixed(1)}/10</div>
                                <div className="text-sm text-gray-500">Reputation</div>
                            </div>
                        </div>

                        {/* All Specialties */}
                        <div className="mb-6">
                            <h4 className="text-lg font-medium text-gray-900 mb-3">Specialties</h4>
                            <div className="flex flex-wrap gap-2">
                                {supplier.specialties.map((specialty, index) => (
                                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm">
                                        {specialty}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* All Certifications */}
                        {supplier.certifications.length > 0 && (
                            <div className="mb-6">
                                <h4 className="text-lg font-medium text-gray-900 mb-3">Certifications</h4>
                                <div className="flex flex-wrap gap-2">
                                    {supplier.certifications.map((cert, index) => (
                                        <span key={index} className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-md text-sm">
                                            <Shield size={14} className="mr-2" />
                                            {cert}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Contact Information */}
                        {Object.keys(supplier.contact_info || {}).length > 0 && (
                            <div className="mb-6">
                                <h4 className="text-lg font-medium text-gray-900 mb-3">Contact Information</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {supplier.contact_info.email && (
                                        <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                                            <Mail size={16} className="text-gray-600 mr-3" />
                                            <div>
                                                <div className="font-medium text-gray-900">Email</div>
                                                <div className="text-sm text-gray-600">{supplier.contact_info.email}</div>
                                            </div>
                                        </div>
                                    )}
                                    {supplier.contact_info.phone && (
                                        <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                                            <Phone size={16} className="text-gray-600 mr-3" />
                                            <div>
                                                <div className="font-medium text-gray-900">Phone</div>
                                                <div className="text-sm text-gray-600">{supplier.contact_info.phone}</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Notes */}
                        {supplier.notes && (
                            <div className="mb-6">
                                <h4 className="text-lg font-medium text-gray-900 mb-3">Additional Notes</h4>
                                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{supplier.notes}</p>
                            </div>
                        )}

                        {/* Actions */}
                        <div className="flex gap-3 pt-4 border-t border-gray-200">
                            {supplier.contact_info?.email && (
                                <button className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                                    <Mail size={16} className="mr-2" />
                                    Send Email
                                </button>
                            )}
                            <button 
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    if (!sessionId) {
        return (
            <div className="text-center py-12">
                <Users size={48} className="mx-auto text-gray-400 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">No Session Selected</h2>
                <p className="text-gray-600">Please select a session to view supplier recommendations.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Suppliers</h1>
                    <p className="text-gray-600 mt-1">
                        {sessionId && `Session: ${sessionId.slice(0, 8)}...`}
                    </p>
                </div>
                {searchResults && (
                    <div className="text-right">
                        <div className="text-sm text-gray-500">Search Confidence</div>
                        <div className="text-xl font-semibold text-gray-900">
                            {(searchResults.search_confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                )}
            </div>

            {isLoading ? (
                <div className="text-center py-12">
                    <div className="spinner mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading suppliers...</p>
                </div>
            ) : suppliers.length === 0 ? (
                <div className="text-center py-12">
                    <AlertCircle size={48} className="mx-auto text-gray-400 mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">No Suppliers Found</h2>
                    <p className="text-gray-600">No suppliers were found for this session. Try starting a new request.</p>
                </div>
            ) : (
                <>
                    {/* Search and Filter Controls */}
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                            <div className="flex-1">
                                <input
                                    type="text"
                                    placeholder="Search suppliers by name, location, or specialty..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div className="flex gap-2">
                                <select
                                    value={filterBy}
                                    onChange={(e) => setFilterBy(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="all">All Suppliers</option>
                                    <option value="certified">Certified Only</option>
                                    <option value="high-score">High Score (80+)</option>
                                    <option value="fast-delivery">Fast Delivery (≤20 days)</option>
                                    <option value="low-price">Budget Friendly (≤$5)</option>
                                </select>
                                <select
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="overall_score">Overall Score</option>
                                    <option value="price">Price (Low to High)</option>
                                    <option value="lead_time">Lead Time</option>
                                    <option value="reputation">Reputation</option>
                                    <option value="name">Name (A-Z)</option>
                                </select>
                            </div>
                        </div>
                        <div className="mt-4 text-sm text-gray-600">
                            Showing {filteredSuppliers.length} of {suppliers.length} suppliers
                        </div>
                    </div>

                    {/* Market Insights */}
                    {searchResults?.market_insights && (
                        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                            <div className="flex items-start">
                                <TrendingUp className="text-blue-600 mr-3 mt-1" size={20} />
                                <div className="flex-1">
                                    <h3 className="font-medium text-blue-900 mb-2">Market Insights</h3>
                                    <p className="text-blue-800 text-sm whitespace-pre-wrap">{searchResults.market_insights}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Supplier Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        {filteredSuppliers.map((supplier) => (
                            <SupplierCard key={supplier.supplier_id} supplier={supplier} />
                        ))}
                    </div>

                    {/* Alternative Suggestions */}
                    {searchResults?.alternative_suggestions && searchResults.alternative_suggestions.length > 0 && (
                        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
                            <div className="flex items-start">
                                <AlertCircle className="text-yellow-600 mr-3 mt-1" size={20} />
                                <div className="flex-1">
                                    <h3 className="font-medium text-yellow-900 mb-2">Alternative Suggestions</h3>
                                    <ul className="text-yellow-800 text-sm space-y-1">
                                        {searchResults.alternative_suggestions.map((suggestion, index) => (
                                            <li key={index} className="flex items-start">
                                                <span className="mr-2">•</span>
                                                {suggestion}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Supplier Detail Modal */}
            {showModal && (
                <SupplierModal 
                    supplier={selectedSupplier} 
                    onClose={() => {
                        setShowModal(false);
                        setSelectedSupplier(null);
                    }} 
                />
            )}
        </div>
    );
}