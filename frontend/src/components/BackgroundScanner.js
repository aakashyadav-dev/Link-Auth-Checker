import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BackgroundScanner = ({ sessionId }) => {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);

    const queueScan = async (url) => {
        try {
            setLoading(true);
            const response = await axios.post('http://localhost:5001/background_scan', {
                url,
                session_id: sessionId
            });
            
            alert(`Scan queued with ID: ${response.data.scan_id}`);
            loadScans();
        } catch (error) {
            console.error('Queue scan error:', error);
            alert('Failed to queue scan');
        } finally {
            setLoading(false);
        }
    };

    const loadScans = async () => {
        try {
            const response = await axios.get(`http://localhost:5001/scan_history/${sessionId}`);
            setScans(response.data.scan_history || []);
        } catch (error) {
            console.error('Load scans error:', error);
        }
    };

    const checkStatus = async (scanId) => {
        try {
            const response = await axios.get(`http://localhost:5001/background_scan/${scanId}`);
            alert(`Scan Status: ${response.data.status}`);
        } catch (error) {
            console.error('Check status error:', error);
        }
    };

    useEffect(() => {
        if (sessionId) {
            loadScans();
        }
    }, [sessionId]);

    return (
        <div className="bg-scanner-container">
            <h3>Background Security Scanner</h3>
            
            <div className="scanner-controls">
                <input
                    type="text"
                    placeholder="Enter URL to scan"
                    id="scanUrl"
                />
                <button 
                    onClick={() => {
                        const url = document.getElementById('scanUrl').value;
                        if (url) queueScan(url);
                    }}
                    disabled={loading}
                >
                    {loading ? 'Queuing...' : 'Queue Background Scan'}
                </button>
            </div>

            <div className="recent-scans">
                <h4>Recent Scans</h4>
                <div className="scans-list">
                    {scans.map((scan, index) => (
                        <div key={index} className="scan-item">
                            <div className="scan-url">{scan.url}</div>
                            <div className={`risk-badge ${scan.risk_level}`}>
                                {scan.risk_level}
                            </div>
                            <button onClick={() => checkStatus(scan.id)}>
                                Check Status
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <style jsx>{`
                .bg-scanner-container {
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 8px;
                }
                .scanner-controls {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                }
                .scanner-controls input {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .scanner-controls button {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .scanner-controls button:disabled {
                    background: #ccc;
                }
                .scans-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .scan-item {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 10px;
                    background: white;
                    border-radius: 4px;
                }
                .scan-url {
                    flex: 1;
                    word-break: break-all;
                }
                .risk-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                .risk-badge.SAFE { background: #d4edda; color: #155724; }
                .risk-badge.WARNING { background: #fff3cd; color: #856404; }
                .risk-badge.DANGEROUS { background: #f8d7da; color: #721c24; }
            `}</style>
        </div>
    );
};

export default BackgroundScanner;