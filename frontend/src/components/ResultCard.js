// components/ResultCard.js (Fixed)
import React, { useState, useEffect } from "react";

export default function ResultCard({ data, onUserDecision }) {
  const [decisionMade, setDecisionMade] = useState(false);
  const [timer, setTimer] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [storageStatus, setStorageStatus] = useState('');
  
  const riskColors = { 
    SAFE: "#2ecc71", 
    WARNING: "#f39c12", 
    DANGEROUS: "#e74c3c" 
  };
  
  const riskIcons = {
    SAFE: "✅",
    WARNING: "⚠️",
    DANGEROUS: "🚫"
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(prev => prev + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);

  const handleUserDecision = async (decision) => {
    try {
      setDecisionMade(true);
      if (onUserDecision) {
        await onUserDecision(decision, data.risk, data.input_url);
        setStorageStatus('✓ Decision saved successfully');
      }
    } catch (error) {
      setStorageStatus('⚠️ Decision saved locally');
      console.error('Failed to save decision:', error);
    }
  };

  const getRiskLevelClass = (risk) => {
    return `risk-level risk-${risk.toLowerCase()}`;
  };

  const getSecurityDetails = () => {
    if (!data.security_analysis) return null;
    
    return (
      <div className="security-details">
        <h4>Security Analysis Details</h4>
        
        {data.security_analysis.pattern_warnings && data.security_analysis.pattern_warnings.length > 0 && (
          <div className="detail-section">
            <strong>Pattern Warnings:</strong>
            <ul>
              {data.security_analysis.pattern_warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}
        
        {data.security_analysis.phishing_indicators && data.security_analysis.phishing_indicators.length > 0 && (
          <div className="detail-section">
            <strong>Phishing Indicators:</strong>
            <ul>
              {data.security_analysis.phishing_indicators.map((indicator, index) => (
                <li key={index}>{indicator}</li>
              ))}
            </ul>
          </div>
        )}
        
        {data.security_analysis.suspicious_patterns !== undefined && (
          <div className="detail-section">
            <strong>Suspicious Patterns Detected:</strong> {data.security_analysis.suspicious_patterns}
          </div>
        )}
        
        {data.security_analysis.calculated_score !== undefined && (
          <div className="detail-section">
            <strong>Raw Risk Score:</strong> {data.security_analysis.calculated_score}
          </div>
        )}
        
        {data.security_analysis.error && (
          <div className="detail-section error">
            <strong>Analysis Error:</strong> {data.security_analysis.error}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="result-card">
      <div className="result-header">
        <h2>Security Analysis Result</h2>
        <div className={getRiskLevelClass(data.risk)}>
          <span className="risk-icon">{riskIcons[data.risk] || "🔍"}</span>
          <span className="risk-text">Risk Level: {data.risk}</span>
        </div>
      </div>
      
      <div className="result-grid">
        <div className="result-item">
          <label>Domain</label>
          <div className="result-value">{data.domain}</div>
        </div>
        
        <div className="result-item">
          <label>SSL Certificate</label>
          <div className={`result-value ssl-status ${
            data.ssl === 'Valid' ? 'ssl-valid' : 
            data.ssl === 'Invalid' ? 'ssl-invalid' : 
            'ssl-unknown'
          }`}>
            {data.ssl}
          </div>
        </div>
        
        <div className="result-item">
          <label>Domain Age</label>
          <div className="result-value">{data.domain_age}</div>
        </div>
        
        <div className="result-item">
          <label>Redirects</label>
          <div className="result-value">
            {data.redirects && data.redirects.length > 1 ? (
              <span className="redirect-count">{data.redirects.length} redirects detected</span>
            ) : (
              "No redirects"
            )}
          </div>
        </div>
        
        <div className="result-item">
          <label>Phishing Score</label>
          <div className="result-value">
            <div className="score-container">
              <div 
                className="score-bar" 
                style={{width: `${data.phishing_score}%`}}
              ></div>
              <span className="score-text">{data.phishing_score}%</span>
            </div>
          </div>
        </div>
        
        {data.behavioral_context && (
          <div className="result-item full-width">
            <label>Behavioral Context</label>
            <div className="result-value behavioral-context">
              <p><strong>Recommended Action:</strong> {data.behavioral_context.recommended_action}</p>
              <p><strong>Session ID:</strong> {data.behavioral_context.session_id.substring(0, 8)}...</p>
            </div>
          </div>
        )}
      </div>
      
      <div className="details-toggle">
        <button 
          onClick={() => setShowDetails(!showDetails)}
          className="toggle-btn"
        >
          {showDetails ? 'Hide' : 'Show'} Security Details
        </button>
      </div>
      
      {showDetails && getSecurityDetails()}
      
      {!decisionMade && (
        <div className="decision-panel">
          <h4>What would you do with this URL?</h4>
          <div className="decision-buttons">
            <button 
              className="decision-btn safe"
              onClick={() => handleUserDecision('proceed')}
            >
              Proceed to Visit
            </button>
            <button 
              className="decision-btn avoid"
              onClick={() => handleUserDecision('avoid')}
            >
              Avoid This URL
            </button>
            <button 
              className="decision-btn learn"
              onClick={() => handleUserDecision('learn_more')}
            >
              Learn More
            </button>
          </div>
          <p className="decision-timer">Time considering: {timer}s</p>
        </div>
      )}
      
      {decisionMade && (
        <div className="decision-feedback">
          <p>{storageStatus || '✓ Your decision has been recorded for behavioral analysis'}</p>
        </div>
      )}
    </div>
  );
}