import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BackgroundScanner from './components/BackgroundScanner';
import BiometricsModule from './components/BiometricsModule';
import AlertSystem from './components/AlertSystem';
import CloudPhishingDB from './components/CloudPhishingDB';
import './style.css';

function App() {
    const [url, setUrl] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState('');
    const [analytics, setAnalytics] = useState(null);
    const [activeTab, setActiveTab] = useState('scanner');
    const [decisionTime, setDecisionTime] = useState(null);
    const [mouseMovements, setMouseMovements] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [analyticsLoading, setAnalyticsLoading] = useState(false);

    useEffect(() => {
        // Generate or retrieve session ID
        let sid = localStorage.getItem('sessionId');
        if (!sid) {
            sid = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('sessionId', sid);
        }
        setSessionId(sid);

        // Track mouse movements
        const handleMouseMove = (e) => {
            setMouseMovements(prev => {
                const newMovement = {
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                };
                return [...prev.slice(-20), newMovement];
            });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    // Load analytics when sessionId changes
    useEffect(() => {
        if (sessionId) {
            loadAnalytics();
        }
    }, [sessionId]);

    const checkUrl = async () => {
        if (!url) return;
        
        setLoading(true);
        setDecisionTime(Date.now());
        setResult(null); // Clear previous results
        
        try {
            const response = await axios.post('http://localhost:5001/check', {
                url: url
            }, {
                headers: {
                    'X-Session-ID': sessionId
                }
            });
            
            setResult(response.data);
            await loadAnalytics(); // Wait for analytics to load
        } catch (error) {
            console.error('Error checking URL:', error);
            alert('Error checking URL. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const trackDecision = async (decision) => {
        // Prevent double submission
        if (isSubmitting) {
            console.log('Already submitting, please wait...');
            return;
        }
        
        if (!result || !decisionTime) {
            alert('No active URL check found. Please check a URL first.');
            return;
        }

        setIsSubmitting(true);
        const responseTime = Date.now() - decisionTime;

        try {
            console.log(`Submitting decision: ${decision} for ${result.input_url}`);
            
            const response = await axios.post('http://localhost:5001/user_decision', {
                session_id: sessionId,
                url: result.input_url,
                risk_level: result.risk,
                decision: decision,
                response_time: responseTime,
                mouse_movements: mouseMovements.slice(-10) // Send last 10 movements
            });
            
            if (response.data.status === 'success') {
                alert(`✅ Decision recorded: You chose to ${decision}`);
                await loadAnalytics(); // Refresh analytics
            } else {
                alert(`⚠️ Decision recorded but with issues: ${response.data.message}`);
            }
        } catch (error) {
            console.error('Error tracking decision:', error);
            alert('Error recording decision. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const loadAnalytics = async () => {
        if (!sessionId) return;
        
        setAnalyticsLoading(true);
        try {
            console.log(`Loading analytics for session: ${sessionId}`);
            const response = await axios.get(`http://localhost:5001/behavioral_analytics/${sessionId}`);
            setAnalytics(response.data);
            console.log('Analytics loaded:', response.data);
        } catch (error) {
            console.error('Error loading analytics:', error);
            // Don't show alert for analytics errors, just log them
        } finally {
            setAnalyticsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !loading) {
            checkUrl();
        }
    };

    return (
        <div className="App">
            <header className="app-header">
                <h1>🔐 Link Auth Checker</h1>
                <p>Advanced Security Scanner with Behavioral Analytics</p>
                {sessionId && (
                    <div className="session-info">
                        Session: {sessionId.substring(0, 8)}...
                    </div>
                )}
            </header>

            <nav className="tab-nav">
                <button 
                    className={activeTab === 'scanner' ? 'active' : ''}
                    onClick={() => setActiveTab('scanner')}
                >
                    🔍 URL Scanner
                </button>
                <button 
                    className={activeTab === 'background' ? 'active' : ''}
                    onClick={() => setActiveTab('background')}
                >
                    ⚡ Background Scanner
                </button>
                <button 
                    className={activeTab === 'biometrics' ? 'active' : ''}
                    onClick={() => setActiveTab('biometrics')}
                >
                    👤 Biometrics
                </button>
                <button 
                    className={activeTab === 'alerts' ? 'active' : ''}
                    onClick={() => setActiveTab('alerts')}
                >
                    🚨 Alerts
                </button>
                <button 
                    className={activeTab === 'cloud' ? 'active' : ''}
                    onClick={() => setActiveTab('cloud')}
                >
                    ☁️ Cloud DB
                </button>
                <button 
                    className={activeTab === 'analytics' ? 'active' : ''}
                    onClick={() => setActiveTab('analytics')}
                >
                    📊 Analytics
                </button>
            </nav>

            <main className="app-main">
                {activeTab === 'scanner' && (
                    <div className="scanner-tab">
                        <div className="input-section">
                            <input
                                type="text"
                                placeholder="Enter URL to check (e.g., https://example.com)"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyPress={handleKeyPress}
                                disabled={loading}
                            />
                            <button onClick={checkUrl} disabled={loading || !url}>
                                {loading ? 'Checking...' : 'Check URL'}
                            </button>
                        </div>

                        {loading && (
                            <div className="loading-indicator">
                                <div className="spinner"></div>
                                <p>Analyzing URL... This may take a moment.</p>
                            </div>
                        )}

                        {result && !loading && (
                            <div className="result-section">
                                <h2>Analysis Results</h2>
                                
                                <div className={`risk-badge ${result.risk}`}>
                                    Risk Level: {result.risk}
                                </div>
                                
                                <div className="result-details">
                                    <div className="detail-item">
                                        <strong>Domain:</strong> {result.domain || 'Unknown'}
                                    </div>
                                    <div className="detail-item">
                                        <strong>SSL Certificate:</strong> 
                                        <span className={result.ssl === 'Valid' ? 'text-safe' : 'text-danger'}>
                                            {result.ssl || 'Unknown'}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Domain Age:</strong> {result.domain_age || 'Unknown'}
                                    </div>
                                    <div className="detail-item">
                                        <strong>Phishing Score:</strong> 
                                        <span className={`score-${result.risk}`}>
                                            {result.phishing_score}%
                                        </span>
                                    </div>
                                </div>

                                {result.security_analysis && (
                                    <div className="security-analysis">
                                        <h3>Security Analysis</h3>
                                        
                                        {result.security_analysis.pattern_warnings && 
                                         result.security_analysis.pattern_warnings.length > 0 && (
                                            <div className="warnings">
                                                <h4>⚠️ Warnings:</h4>
                                                <ul>
                                                    {result.security_analysis.pattern_warnings.map((warning, i) => (
                                                        <li key={i}>{warning}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        {result.security_analysis.phishing_indicators && 
                                         result.security_analysis.phishing_indicators.length > 0 && (
                                            <div className="indicators">
                                                <h4>🚨 Phishing Indicators:</h4>
                                                <ul>
                                                    {result.security_analysis.phishing_indicators.map((indicator, i) => (
                                                        <li key={i}>{indicator}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        {result.security_analysis.cloud_db_match && (
                                            <div className="cloud-match">
                                                <h4>☁️ Cloud Database Match</h4>
                                                <p>This URL was found in our phishing database</p>
                                            </div>
                                        )}

                                        {result.security_analysis.threat_intel && 
                                         result.security_analysis.threat_intel.score > 0 && (
                                            <div className="threat-intel">
                                                <h4>🧠 Threat Intelligence</h4>
                                                <p>Risk Score: {result.security_analysis.threat_intel.score}</p>
                                            </div>
                                        )}
                                    </div>
                                )}

                                <div className="decision-section">
                                    <h3>Your Decision</h3>
                                    <p className="recommendation">
                                        {result.behavioral_context?.recommended_action || 'Use caution when visiting unknown URLs'}
                                    </p>
                                    <div className="decision-buttons">
                                        <button 
                                            className="proceed-btn"
                                            onClick={() => trackDecision('proceed')}
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting ? 'Recording...' : '✅ Proceed to Website'}
                                        </button>
                                        <button 
                                            className="avoid-btn"
                                            onClick={() => trackDecision('avoid')}
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting ? 'Recording...' : '🚫 Avoid Website'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'background' && (
                    <BackgroundScanner sessionId={sessionId} />
                )}

                {activeTab === 'biometrics' && (
                    <BiometricsModule sessionId={sessionId} />
                )}

                {activeTab === 'alerts' && (
                    <AlertSystem />
                )}

                {activeTab === 'cloud' && (
                    <CloudPhishingDB />
                )}

                {activeTab === 'analytics' && (
                    <div className="analytics-tab">
                        <div className="analytics-header">
                            <h2>Your Security Analytics</h2>
                            <button 
                                onClick={loadAnalytics} 
                                disabled={analyticsLoading}
                                className="refresh-btn"
                            >
                                {analyticsLoading ? 'Refreshing...' : '🔄 Refresh'}
                            </button>
                        </div>
                        
                        {analyticsLoading && (
                            <div className="loading-indicator">
                                <div className="spinner"></div>
                                <p>Loading analytics...</p>
                            </div>
                        )}

                        {!analyticsLoading && analytics && (
                            <>
                                <div className="analytics-grid">
                                    <div className="analytics-card">
                                        <h3>Phishing Susceptibility</h3>
                                        <div className="score">{analytics.phishing_susceptibility_score}%</div>
                                        <p className="score-desc">How often you proceed to risky URLs</p>
                                    </div>
                                    
                                    <div className="analytics-card">
                                        <h3>Security Compliance</h3>
                                        <div className="score">{analytics.security_compliance_score}%</div>
                                        <p className="score-desc">How well you avoid threats</p>
                                    </div>
                                    
                                    <div className="analytics-card">
                                        <h3>Risk Perception</h3>
                                        <div className="score">{analytics.risk_perception_score}%</div>
                                        <p className="score-desc">Your ability to identify risks</p>
                                    </div>
                                </div>

                                <div className="scan-summary">
                                    <h3>Scan Summary</h3>
                                    <div className="summary-stats">
                                        <div className="stat total">
                                            <label>Total Scans:</label>
                                            <span>{analytics.total_scans || 0}</span>
                                        </div>
                                        <div className="stat safe">
                                            <label>✅ Safe URLs:</label>
                                            <span>{analytics.safe_scans || 0}</span>
                                        </div>
                                        <div className="stat warning">
                                            <label>⚠️ Warning URLs:</label>
                                            <span>{analytics.warning_scans || 0}</span>
                                        </div>
                                        <div className="stat dangerous">
                                            <label>🚨 Dangerous URLs:</label>
                                            <span>{analytics.dangerous_scans || 0}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="decisions-summary">
                                    <h3>Decision Summary</h3>
                                    <div className="summary-stats">
                                        <div className="stat">
                                            <label>Total Decisions:</label>
                                            <span>{analytics.total_decisions || 0}</span>
                                        </div>
                                        <div className="stat safe">
                                            <label>Safe Decisions:</label>
                                            <span>{analytics.safe_decisions || 0}</span>
                                        </div>
                                        <div className="stat warning">
                                            <label>Warning Decisions:</label>
                                            <span>{analytics.warning_decisions || 0}</span>
                                        </div>
                                        <div className="stat dangerous">
                                            <label>Dangerous Decisions:</label>
                                            <span>{analytics.dangerous_decisions || 0}</span>
                                        </div>
                                    </div>
                                </div>

                                {analytics.behavioral_insights && analytics.behavioral_insights.length > 0 && (
                                    <div className="insights">
                                        <h3>Behavioral Insights</h3>
                                        <ul>
                                            {analytics.behavioral_insights.map((insight, i) => (
                                                <li key={i}>{insight}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </>
                        )}

                        {!analyticsLoading && !analytics && (
                            <div className="no-data">
                                <p>No analytics data available yet. Start scanning URLs to see your analytics.</p>
                            </div>
                        )}
                    </div>
                )}
            </main>

            <footer className="app-footer">
                <p>© 2026 Link Auth Checker - Advanced Security Suite v2.0</p>
                <p className="footer-note">Your behavior is being analyzed to improve security</p>
            </footer>
        </div>
    );
}

export default App;