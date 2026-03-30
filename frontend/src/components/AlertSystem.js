import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AlertSystem = () => {
    const [alerts, setAlerts] = useState({ active: [], recent: [] });
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState(null);
    const [showModal, setShowModal] = useState(false);

    const loadAlerts = async (showRefreshIndicator = false) => {
        if (showRefreshIndicator) {
            setRefreshing(true);
        } else {
            setLoading(true);
        }
        
        try {
            const response = await axios.get('http://localhost:5001/alerts');
            setAlerts(response.data);
            console.log('Alerts loaded:', response.data);
        } catch (error) {
            console.error('Load alerts error:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const resolveAlert = async (alertId) => {
        try {
            await axios.post(`http://localhost:5001/alerts/${alertId}/resolve`, {
                resolved_by: 'user'
            });
            // Reload alerts after resolving
            loadAlerts();
            // Show success message in modal instead of alert
            setShowSuccessMessage('Alert resolved successfully');
        } catch (error) {
            console.error('Resolve alert error:', error);
            setShowErrorMessage('Failed to resolve alert');
        }
    };

    const showAlertDetails = (alert) => {
        setSelectedAlert(alert);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedAlert(null);
    };

    const [showSuccess, setShowSuccess] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [showError, setShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const setShowSuccessMessage = (message) => {
        setSuccessMessage(message);
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
    };

    const setShowErrorMessage = (message) => {
        setErrorMessage(message);
        setShowError(true);
        setTimeout(() => setShowError(false), 3000);
    };

    const getSeverityColor = (severity) => {
        switch(severity?.toUpperCase()) {
            case 'CRITICAL': return '#8B0000';
            case 'HIGH': return '#dc3545';
            case 'MEDIUM': return '#ffc107';
            case 'LOW': return '#28a745';
            default: return '#6c757d';
        }
    };

    const getSeverityIcon = (severity) => {
        switch(severity?.toUpperCase()) {
            case 'CRITICAL': return '🔥';
            case 'HIGH': return '⚠️';
            case 'MEDIUM': return '⚡';
            case 'LOW': return 'ℹ️';
            default: return '📢';
        }
    };

    const formatTime = (timestamp) => {
        if (!timestamp) return 'Unknown';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    };

    useEffect(() => {
        loadAlerts();
        
        // Refresh every 30 seconds
        const interval = setInterval(() => loadAlerts(true), 30000);
        
        // Cleanup interval on component unmount
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="alert-system-container">
            {/* Success Toast */}
            {showSuccess && (
                <div className="toast success">
                    ✅ {successMessage}
                </div>
            )}

            {/* Error Toast */}
            {showError && (
                <div className="toast error">
                    ❌ {errorMessage}
                </div>
            )}

            {/* Alert Details Modal */}
            {showModal && selectedAlert && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Alert Details</h3>
                            <button className="close-btn" onClick={closeModal}>×</button>
                        </div>
                        <div className="modal-body">
                            <div className="detail-row">
                                <span className="detail-label">Alert ID:</span>
                                <span className="detail-value">{selectedAlert.id}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Title:</span>
                                <span className="detail-value">{selectedAlert.title}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Message:</span>
                                <span className="detail-value">{selectedAlert.message}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Severity:</span>
                                <span className="detail-value">
                                    <span className={`severity-badge-small`} 
                                          style={{backgroundColor: getSeverityColor(selectedAlert.severity)}}>
                                        {selectedAlert.severity}
                                    </span>
                                </span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Source:</span>
                                <span className="detail-value">{selectedAlert.source}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Created:</span>
                                <span className="detail-value">{new Date(selectedAlert.created_at).toLocaleString()}</span>
                            </div>
                            {selectedAlert.metadata && Object.keys(selectedAlert.metadata).length > 0 && (
                                <div className="detail-row metadata">
                                    <span className="detail-label">Metadata:</span>
                                    <pre className="metadata-pre">
                                        {JSON.stringify(selectedAlert.metadata, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="close-modal-btn" onClick={closeModal}>Close</button>
                            {selectedAlert.status === 'active' && (
                                <button 
                                    className="resolve-modal-btn" 
                                    onClick={() => {
                                        resolveAlert(selectedAlert.id);
                                        closeModal();
                                    }}
                                >
                                    Resolve Alert
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="alert-header">
                <h3>🚨 Real-time Alert System</h3>
                <div className="alert-controls">
                    <button 
                        onClick={() => loadAlerts(true)} 
                        disabled={refreshing}
                        className="refresh-btn"
                    >
                        {refreshing ? '⟳ Refreshing...' : '⟳ Refresh Alerts'}
                    </button>
                </div>
            </div>

            {loading && (
                <div className="loading-indicator">
                    <div className="spinner"></div>
                    <p>Loading alerts...</p>
                </div>
            )}

            {/* Active Alerts Section */}
            {!loading && alerts.active && alerts.active.length > 0 && (
                <div className="active-alerts">
                    <div className="section-header">
                        <h4>Active Alerts</h4>
                        <span className="alert-count">{alerts.active.length}</span>
                    </div>
                    
                    <div className="alerts-list">
                        {alerts.active.map((alert) => (
                            <div key={alert.id} className={`alert-item severity-${alert.severity?.toLowerCase()}`}>
                                <div className="alert-header">
                                    <div className="alert-title-group">
                                        <span className="severity-icon">
                                            {getSeverityIcon(alert.severity)}
                                        </span>
                                        <span className="alert-title">{alert.title}</span>
                                    </div>
                                    <span 
                                        className="severity-badge"
                                        style={{backgroundColor: getSeverityColor(alert.severity)}}
                                    >
                                        {alert.severity}
                                    </span>
                                </div>
                                
                                <div className="alert-message">{alert.message}</div>
                                
                                <div className="alert-footer">
                                    <div className="alert-meta">
                                        <span className="alert-source">
                                            🔍 {alert.source || 'system'}
                                        </span>
                                        <span className="alert-time">
                                            🕒 {formatTime(alert.created_at)}
                                        </span>
                                    </div>
                                    
                                    <div className="alert-actions">
                                        {alert.metadata && Object.keys(alert.metadata).length > 0 && (
                                            <button 
                                                className="details-btn"
                                                onClick={() => showAlertDetails(alert)}
                                            >
                                                📋 Details
                                            </button>
                                        )}
                                        <button 
                                            className="resolve-btn"
                                            onClick={() => resolveAlert(alert.id)}
                                        >
                                            ✓ Resolve
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* No Active Alerts Message */}
            {!loading && alerts.active && alerts.active.length === 0 && (
                <div className="no-alerts">
                    <div className="no-alerts-icon">✅</div>
                    <h4>All Clear!</h4>
                    <p>No active alerts at the moment.</p>
                </div>
            )}

            {/* Recent Alerts Section */}
            {!loading && alerts.recent && alerts.recent.length > 0 && (
                <div className="recent-alerts">
                    <div className="section-header">
                        <h4>Recent Alerts</h4>
                        <span className="alert-count">{alerts.recent.length}</span>
                    </div>
                    
                    <div className="alerts-list recent">
                        {alerts.recent.map((alert) => (
                            <div key={alert.id} className={`alert-item recent severity-${alert.severity?.toLowerCase()}`}>
                                <div className="alert-header">
                                    <div className="alert-title-group">
                                        <span className="severity-icon">
                                            {getSeverityIcon(alert.severity)}
                                        </span>
                                        <span className="alert-title">{alert.title}</span>
                                    </div>
                                    <span 
                                        className="severity-badge small"
                                        style={{backgroundColor: getSeverityColor(alert.severity)}}
                                    >
                                        {alert.severity}
                                    </span>
                                </div>
                                
                                <div className="alert-message">{alert.message}</div>
                                
                                <div className="alert-footer">
                                    <div className="alert-meta">
                                        <span className="alert-source">
                                            🔍 {alert.source || 'system'}
                                        </span>
                                        <span className="alert-time">
                                            🕒 {formatTime(alert.created_at)}
                                        </span>
                                    </div>
                                    <span className="resolved-badge">
                                        ✓ Resolved {alert.resolved_at ? formatTime(alert.resolved_at) : ''}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Alert Statistics */}
            {!loading && (alerts.active?.length > 0 || alerts.recent?.length > 0) && (
                <div className="alert-stats">
                    <div className="stat-item">
                        <span className="stat-label">Active:</span>
                        <span className="stat-value active">{alerts.active?.length || 0}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Resolved (24h):</span>
                        <span className="stat-value">
                            {alerts.recent?.filter(a => 
                                a.resolved_at && new Date(a.resolved_at) > new Date(Date.now() - 86400000)
                            ).length || 0}
                        </span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Total:</span>
                        <span className="stat-value">{(alerts.active?.length || 0) + (alerts.recent?.length || 0)}</span>
                    </div>
                </div>
            )}

            <style jsx>{`
                .alert-system-container {
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    position: relative;
                }

                /* Toast Notifications */
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 25px;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    z-index: 2000;
                    animation: slideIn 0.3s ease;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }

                .toast.success {
                    background: #28a745;
                }

                .toast.error {
                    background: #dc3545;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                /* Modal Styles */
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                    animation: fadeIn 0.2s ease;
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                .modal-content {
                    background: white;
                    border-radius: 12px;
                    width: 90%;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    animation: scaleIn 0.3s ease;
                }

                @keyframes scaleIn {
                    from {
                        transform: scale(0.9);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1);
                        opacity: 1;
                    }
                }

                .modal-header {
                    padding: 20px;
                    border-bottom: 1px solid #e0e0e0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #f8f9fa;
                    border-radius: 12px 12px 0 0;
                }

                .modal-header h3 {
                    margin: 0;
                    color: #333;
                }

                .close-btn {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 0 8px;
                }

                .close-btn:hover {
                    color: #333;
                }

                .modal-body {
                    padding: 20px;
                }

                .detail-row {
                    margin-bottom: 15px;
                    display: flex;
                    flex-direction: column;
                }

                .detail-label {
                    font-weight: bold;
                    color: #666;
                    margin-bottom: 5px;
                    font-size: 0.9em;
                }

                .detail-value {
                    color: #333;
                    word-break: break-word;
                }

                .severity-badge-small {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    font-size: 0.8em;
                    font-weight: bold;
                }

                .metadata {
                    margin-top: 10px;
                }

                .metadata-pre {
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 0.9em;
                    overflow-x: auto;
                    margin: 5px 0 0 0;
                }

                .modal-footer {
                    padding: 20px;
                    border-top: 1px solid #e0e0e0;
                    display: flex;
                    justify-content: flex-end;
                    gap: 10px;
                }

                .close-modal-btn {
                    padding: 10px 20px;
                    background: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }

                .close-modal-btn:hover {
                    background: #5a6268;
                }

                .resolve-modal-btn {
                    padding: 10px 20px;
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }

                .resolve-modal-btn:hover {
                    background: #218838;
                }

                .alert-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }

                .alert-header h3 {
                    color: #333;
                    margin: 0;
                }

                .refresh-btn {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9em;
                    transition: all 0.3s;
                }

                .refresh-btn:hover {
                    background: #0056b3;
                }

                .refresh-btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }

                .loading-indicator {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }

                .spinner {
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #007bff;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 15px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .section-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }

                .section-header h4 {
                    color: #333;
                    margin: 0;
                }

                .alert-count {
                    background: #e0e0e0;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.9em;
                    color: #666;
                }

                .active-alerts, .recent-alerts {
                    margin-bottom: 30px;
                }

                .alerts-list {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }

                .alert-item {
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid transparent;
                }

                .alert-item.severity-critical {
                    border-left-color: #8B0000;
                    background: #fff5f5;
                }

                .alert-item.severity-high {
                    border-left-color: #dc3545;
                    background: #fff3f3;
                }

                .alert-item.severity-medium {
                    border-left-color: #ffc107;
                    background: #fff9e6;
                }

                .alert-item.severity-low {
                    border-left-color: #28a745;
                    background: #f0fff0;
                }

                .alert-item.recent {
                    opacity: 0.8;
                }

                .alert-item.recent:hover {
                    opacity: 1;
                }

                .alert-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }

                .alert-title-group {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .severity-icon {
                    font-size: 1.2em;
                }

                .alert-title {
                    font-weight: bold;
                    color: #333;
                }

                .severity-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    font-size: 0.8em;
                    font-weight: bold;
                }

                .severity-badge.small {
                    font-size: 0.7em;
                    padding: 2px 6px;
                }

                .alert-message {
                    color: #666;
                    margin-bottom: 15px;
                    line-height: 1.5;
                }

                .alert-footer {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 10px;
                }

                .alert-meta {
                    display: flex;
                    gap: 15px;
                    font-size: 0.9em;
                    color: #999;
                }

                .alert-source, .alert-time {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }

                .alert-actions {
                    display: flex;
                    gap: 8px;
                }

                .details-btn, .resolve-btn {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9em;
                    transition: all 0.3s;
                }

                .details-btn {
                    background: #6c757d;
                    color: white;
                }

                .details-btn:hover {
                    background: #5a6268;
                }

                .resolve-btn {
                    background: #28a745;
                    color: white;
                }

                .resolve-btn:hover {
                    background: #218838;
                }

                .resolved-badge {
                    font-size: 0.9em;
                    color: #28a745;
                }

                .no-alerts {
                    text-align: center;
                    padding: 60px 20px;
                    background: white;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }

                .no-alerts-icon {
                    font-size: 4em;
                    margin-bottom: 15px;
                }

                .no-alerts h4 {
                    color: #333;
                    margin-bottom: 10px;
                }

                .no-alerts p {
                    color: #666;
                }

                .alert-stats {
                    display: flex;
                    justify-content: space-around;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    margin-top: 20px;
                }

                .stat-item {
                    text-align: center;
                }

                .stat-label {
                    display: block;
                    color: #666;
                    font-size: 0.9em;
                    margin-bottom: 5px;
                }

                .stat-value {
                    font-size: 1.5em;
                    font-weight: bold;
                    color: #333;
                }

                .stat-value.active {
                    color: #dc3545;
                }
            `}</style>
        </div>
    );
};

export default AlertSystem;