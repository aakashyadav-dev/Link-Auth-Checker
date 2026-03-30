
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CloudPhishingDB = () => {
    const [stats, setStats] = useState(null);
    const [checkResult, setCheckResult] = useState(null);
    const [recentThreats, setRecentThreats] = useState([]);
    const [loading, setLoading] = useState(false);
    const [statsLoading, setStatsLoading] = useState(false);
    const [url, setUrl] = useState('');
    const [description, setDescription] = useState('');
    const [activeTab, setActiveTab] = useState('check');

    const loadStats = async () => {
        setStatsLoading(true);
        try {
            const response = await axios.get('http://localhost:5001/cloud_db/stats');
            setStats(response.data);
            console.log('Database stats:', response.data);
        } catch (error) {
            console.error('Load stats error:', error);
        } finally {
            setStatsLoading(false);
        }
    };

    const checkUrl = async () => {
        if (!url) return;
        
        try {
            setLoading(true);
            const response = await axios.post('http://localhost:5001/cloud_db/check', {
                url
            });
            setCheckResult(response.data);
            
            // Refresh stats after check
            loadStats();
        } catch (error) {
            console.error('Check URL error:', error);
            alert('Error checking URL');
        } finally {
            setLoading(false);
        }
    };

    const addToDatabase = async () => {
        if (!url) return;
        
        try {
            setLoading(true);
            const response = await axios.post('http://localhost:5001/cloud_db/add', {
                url,
                threat_type: 'phishing',
                confidence: 0.9,
                description: description || 'User-submitted suspicious URL'
            });
            
            if (response.data.success) {
                alert('✅ URL added to database successfully');
                setUrl('');
                setDescription('');
                loadStats(); // Refresh stats after adding
                
                // Also refresh check result if it was for this URL
                if (checkResult && checkResult.url === url) {
                    setCheckResult(null);
                }
            } else {
                alert('❌ Failed to add URL: ' + response.data.error);
            }
        } catch (error) {
            console.error('Add to DB error:', error);
            alert('Error adding to database');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStats();
        // Refresh stats every 30 seconds
        const interval = setInterval(loadStats, 30000);
        return () => clearInterval(interval);
    }, []);

    // Format number with commas
    const formatNumber = (num) => {
        return num?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") || "0";
    };

    return (
        <div className="cloud-db-container">
            <div className="cloud-db-header">
                <h3>☁️ Cloud Phishing Database</h3>
                <p className="description">
                    The Cloud Phishing Database checks URLs against known phishing threats.
                    It automatically updates from multiple threat intelligence feeds and
                    allows community contributions.
                </p>
            </div>

            {/* Database Statistics Cards */}
            <div className="stats-grid">
                {statsLoading ? (
                    <div className="loading-stats">Loading statistics...</div>
                ) : (
                    <>
                        <div className="stat-card total">
                            <div className="stat-icon">📊</div>
                            <div className="stat-content">
                                <div className="stat-value">{formatNumber(stats?.total_urls)}</div>
                                <div className="stat-label">Total URLs in Database</div>
                                {stats?.total_urls > 0 && (
                                    <div className="stat-trend">↑ +{stats.recent_additions || 0} new today</div>
                                )}
                            </div>
                        </div>

                        <div className="stat-card active">
                            <div className="stat-icon">⚠️</div>
                            <div className="stat-content">
                                <div className="stat-value">{formatNumber(stats?.active_urls)}</div>
                                <div className="stat-label">Active Threats</div>
                                <div className="stat-detail">Currently malicious</div>
                            </div>
                        </div>

                        <div className="stat-card cache">
                            <div className="stat-icon">💾</div>
                            <div className="stat-content">
                                <div className="stat-value">{formatNumber(stats?.cache_size)}</div>
                                <div className="stat-label">Cached Lookups</div>
                                <div className="stat-detail">Fast recent checks</div>
                            </div>
                        </div>

                        <div className="stat-card feeds">
                            <div className="stat-icon">📡</div>
                            <div className="stat-content">
                                <div className="stat-value">{stats?.feeds?.length || 0}</div>
                                <div className="stat-label">Active Feeds</div>
                                <div className="stat-detail">Threat intelligence sources</div>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Threat Types Breakdown */}
            {stats?.threat_types && Object.keys(stats.threat_types).length > 0 && (
                <div className="threat-breakdown">
                    <h4>Threat Breakdown</h4>
                    <div className="threat-bars">
                        {Object.entries(stats.threat_types).map(([type, count]) => (
                            <div key={type} className="threat-bar-item">
                                <div className="threat-label">{type}</div>
                                <div className="threat-bar-container">
                                    <div 
                                        className="threat-bar" 
                                        style={{ 
                                            width: `${(count / stats.active_urls * 100)}%`,
                                            backgroundColor: type === 'phishing' ? '#dc3545' : '#ffc107'
                                        }}
                                    ></div>
                                    <span className="threat-count">{count}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Top Sources */}
            {stats?.top_sources && stats.top_sources.length > 0 && (
                <div className="top-sources">
                    <h4>Top Intelligence Sources</h4>
                    <div className="sources-list">
                        {stats.top_sources.map((source, index) => (
                            <div key={index} className="source-item">
                                <span className="source-name">{source.source}</span>
                                <span className="source-count">{formatNumber(source.count)} URLs</span>
                                <div className="source-bar">
                                    <div 
                                        className="source-bar-fill"
                                        style={{ 
                                            width: `${(source.count / stats.total_urls * 100)}%`
                                        }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="db-tabs">
                <button 
                    className={`tab-btn ${activeTab === 'check' ? 'active' : ''}`}
                    onClick={() => setActiveTab('check')}
                >
                    🔍 Check URL
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'add' ? 'active' : ''}`}
                    onClick={() => setActiveTab('add')}
                >
                    ➕ Add to Database
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
                    onClick={() => setActiveTab('stats')}
                >
                    📊 Detailed Stats
                </button>
            </div>

            {activeTab === 'check' && (
                <div className="check-tab">
                    <h4>Check URL Against Database</h4>
                    <p>Enter a URL to see if it's known to be malicious</p>
                    
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Enter URL to check (e.g., http://paypal-verify.tk)"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                        />
                        <button onClick={checkUrl} disabled={loading || !url}>
                            {loading ? 'Checking...' : 'Check URL'}
                        </button>
                    </div>

                    {checkResult && (
                        <div className={`check-result ${checkResult.found ? 'danger' : 'safe'}`}>
                            <div className="result-icon">
                                {checkResult.found ? '⚠️' : '✅'}
                            </div>
                            <div className="result-content">
                                <h5>
                                    {checkResult.found 
                                        ? 'URL Found in Phishing Database!' 
                                        : 'URL Not Found in Database'}
                                </h5>
                                
                                {checkResult.found && (
                                    <div className="result-details">
                                        <p><strong>Threat Type:</strong> {checkResult.threat_type || 'phishing'}</p>
                                        <p><strong>Confidence:</strong> {(checkResult.confidence * 100).toFixed(1)}%</p>
                                        <p><strong>Source:</strong> {checkResult.source || 'database'}</p>
                                        <p><strong>Match Type:</strong> {checkResult.match_type || 'exact'}</p>
                                        {checkResult.description && (
                                            <p><strong>Description:</strong> {checkResult.description}</p>
                                        )}
                                        {checkResult.first_seen && (
                                            <p><strong>First Seen:</strong> {new Date(checkResult.first_seen).toLocaleString()}</p>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    <div className="example-urls">
                        <h5>Try these example URLs:</h5>
                        <div className="url-examples">
                            <button onClick={() => setUrl('http://paypal-verify.tk')}>
                                paypal-verify.tk
                            </button>
                            <button onClick={() => setUrl('http://secure-banking-verify.xyz')}>
                                secure-banking-verify.xyz
                            </button>
                            <button onClick={() => setUrl('https://www.google.com')}>
                                google.com (safe)
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'add' && (
                <div className="add-tab">
                    <h4>Add URL to Database</h4>
                    <p>Help protect others by submitting suspicious URLs</p>
                    
                    <div className="add-form">
                        <div className="form-group">
                            <label>Suspicious URL:</label>
                            <input
                                type="text"
                                placeholder="Enter suspicious URL"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label>Description (optional):</label>
                            <textarea
                                placeholder="Describe why this URL is suspicious"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows="3"
                            />
                        </div>

                        <button 
                            onClick={addToDatabase} 
                            disabled={loading || !url}
                            className="add-btn"
                        >
                            {loading ? 'Adding...' : 'Add to Database'}
                        </button>
                    </div>

                    <div className="note">
                        <p>⚠️ Note: Only add URLs that you believe are actually malicious.</p>
                        <p className="small">Your contribution helps protect other users!</p>
                    </div>
                </div>
            )}

            {activeTab === 'stats' && (
                <div className="stats-tab">
                    <h4>Database Statistics</h4>
                    
                    <div className="stats-details">
                        <div className="stats-row">
                            <span className="stats-label">Total URLs:</span>
                            <span className="stats-value">{formatNumber(stats?.total_urls)}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stats-label">Active Threats:</span>
                            <span className="stats-value">{formatNumber(stats?.active_urls)}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stats-label">Recent Additions (24h):</span>
                            <span className="stats-value">{formatNumber(stats?.recent_additions)}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stats-label">Cache Size:</span>
                            <span className="stats-value">{formatNumber(stats?.cache_size)}</span>
                        </div>
                    </div>

                    {stats?.feeds && stats.feeds.length > 0 && (
                        <div className="feeds-status">
                            <h5>📡 Feed Status</h5>
                            <table className="feeds-table">
                                <thead>
                                    <tr>
                                        <th>Feed Name</th>
                                        <th>Last Update</th>
                                        <th>URL Count</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stats.feeds.map((feed, index) => (
                                        <tr key={index}>
                                            <td>{feed.name}</td>
                                            <td>{feed.last_update ? new Date(feed.last_update).toLocaleString() : 'Never'}</td>
                                            <td>{formatNumber(feed.urls)}</td>
                                            <td>
                                                <span className={`status-badge ${feed.status}`}>
                                                    {feed.status || 'unknown'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {stats?.top_sources && stats.top_sources.length > 0 && (
                        <div className="source-stats">
                            <h5>📊 Top Contributing Sources</h5>
                            <ul className="source-list">
                                {stats.top_sources.map((source, index) => (
                                    <li key={index}>
                                        <span className="source-rank">#{index + 1}</span>
                                        <span className="source-name">{source.source}</span>
                                        <span className="source-count">{formatNumber(source.count)} URLs</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            <style jsx>{`
                .cloud-db-container {
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }

                .cloud-db-header {
                    margin-bottom: 30px;
                }

                .cloud-db-header h3 {
                    color: #333;
                    margin-bottom: 10px;
                }

                .cloud-db-header .description {
                    color: #666;
                    line-height: 1.6;
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .stat-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }

                .stat-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                }

                .stat-card.total { border-left: 4px solid #007bff; }
                .stat-card.active { border-left: 4px solid #dc3545; }
                .stat-card.cache { border-left: 4px solid #28a745; }
                .stat-card.feeds { border-left: 4px solid #ffc107; }

                .stat-icon {
                    font-size: 2.5em;
                }

                .stat-content {
                    flex: 1;
                }

                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #333;
                    line-height: 1.2;
                }

                .stat-label {
                    color: #666;
                    font-size: 0.9em;
                    margin-bottom: 5px;
                }

                .stat-trend {
                    font-size: 0.8em;
                    color: #28a745;
                }

                .stat-detail {
                    font-size: 0.8em;
                    color: #999;
                }

                .loading-stats {
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }

                .threat-breakdown {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }

                .threat-breakdown h4 {
                    margin-bottom: 15px;
                    color: #333;
                }

                .threat-bar-item {
                    margin-bottom: 15px;
                }

                .threat-label {
                    font-size: 0.9em;
                    color: #666;
                    margin-bottom: 5px;
                    text-transform: capitalize;
                }

                .threat-bar-container {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .threat-bar {
                    height: 20px;
                    border-radius: 10px;
                    transition: width 0.3s;
                }

                .threat-count {
                    min-width: 40px;
                    font-weight: bold;
                    color: #333;
                }

                .top-sources {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }

                .top-sources h4 {
                    margin-bottom: 15px;
                    color: #333;
                }

                .source-item {
                    margin-bottom: 15px;
                }

                .source-name {
                    font-weight: 500;
                    color: #333;
                }

                .source-count {
                    float: right;
                    color: #666;
                }

                .source-bar {
                    height: 8px;
                    background: #f0f0f0;
                    border-radius: 4px;
                    margin-top: 5px;
                }

                .source-bar-fill {
                    height: 100%;
                    background: #007bff;
                    border-radius: 4px;
                    transition: width 0.3s;
                }

                .db-tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 10px;
                }

                .tab-btn {
                    padding: 10px 20px;
                    border: none;
                    background: none;
                    cursor: pointer;
                    font-size: 1em;
                    color: #666;
                    transition: all 0.3s;
                }

                .tab-btn:hover {
                    color: #007bff;
                }

                .tab-btn.active {
                    color: #007bff;
                    border-bottom: 2px solid #007bff;
                }

                .check-tab, .add-tab, .stats-tab {
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                }

                .input-group {
                    display: flex;
                    gap: 10px;
                    margin: 20px 0;
                }

                .input-group input {
                    flex: 1;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 1em;
                }

                .input-group button {
                    padding: 12px 24px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1em;
                }

                .input-group button:disabled {
                    background: #ccc;
                }

                .check-result {
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 8px;
                    display: flex;
                    gap: 20px;
                    align-items: start;
                }

                .check-result.danger {
                    background: #fff3f3;
                    border-left: 4px solid #dc3545;
                }

                .check-result.safe {
                    background: #f0fff0;
                    border-left: 4px solid #28a745;
                }

                .result-icon {
                    font-size: 2em;
                }

                .result-content {
                    flex: 1;
                }

                .result-content h5 {
                    margin-bottom: 10px;
                    font-size: 1.1em;
                }

                .result-details {
                    margin-top: 10px;
                }

                .result-details p {
                    margin: 5px 0;
                    color: #666;
                }

                .example-urls {
                    margin-top: 30px;
                }

                .url-examples {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 10px;
                }

                .url-examples button {
                    padding: 8px 16px;
                    background: #f0f0f0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9em;
                }

                .url-examples button:hover {
                    background: #e0e0e0;
                }

                .add-form {
                    max-width: 500px;
                    margin: 20px 0;
                }

                .form-group {
                    margin-bottom: 20px;
                }

                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    color: #333;
                    font-weight: bold;
                }

                .form-group input,
                .form-group textarea {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 1em;
                }

                .add-btn {
                    padding: 12px 24px;
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1em;
                }

                .add-btn:disabled {
                    background: #ccc;
                }

                .note {
                    margin-top: 20px;
                    padding: 15px;
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    border-radius: 4px;
                }

                .note .small {
                    font-size: 0.9em;
                    color: #856404;
                    margin-top: 5px;
                }

                .stats-details {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }

                .stats-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    border-bottom: 1px solid #e0e0e0;
                }

                .stats-row:last-child {
                    border-bottom: none;
                }

                .stats-label {
                    font-weight: 500;
                    color: #666;
                }

                .stats-value {
                    font-weight: bold;
                    color: #333;
                }

                .feeds-status {
                    margin-top: 20px;
                }

                .feeds-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }

                .feeds-table th,
                .feeds-table td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }

                .feeds-table th {
                    background: #f8f9fa;
                    font-weight: bold;
                }

                .status-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.9em;
                }

                .status-badge.success {
                    background: #d4edda;
                    color: #155724;
                }

                .status-badge.failed {
                    background: #f8d7da;
                    color: #721c24;
                }

                .source-stats {
                    margin-top: 20px;
                }

                .source-list {
                    list-style: none;
                    padding: 0;
                }

                .source-list li {
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    border-bottom: 1px solid #f0f0f0;
                }

                .source-rank {
                    width: 50px;
                    color: #666;
                }

                .source-name {
                    flex: 1;
                    font-weight: 500;
                }

                .source-count {
                    color: #007bff;
                    font-weight: bold;
                }
            `}</style>
        </div>
    );
};

export default CloudPhishingDB;
