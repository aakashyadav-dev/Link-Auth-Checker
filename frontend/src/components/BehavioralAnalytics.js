// components/BehavioralAnalytics.js (Fixed)
import React from "react";

export default function BehavioralAnalytics({ data, onClose }) {
  const getScoreColor = (score) => {
    if (score >= 80) return "#2ecc71";
    if (score >= 60) return "#f39c12";
    return "#e74c3c";
  };

  const getScoreLevel = (score) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Moderate";
    if (score >= 20) return "Needs Improvement";
    return "Poor";
  };

  return (
    <div className="analytics-overlay">
      <div className="analytics-modal">
        <div className="analytics-header">
          <h2>Your Security Behavior Profile</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        
        {/* Scan Statistics */}
        <div className="scan-statistics">
          <h3>📊 Scan Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card total">
              <div className="stat-number">{data.total_scans || 0}</div>
              <div className="stat-label">Total URLs Scanned</div>
            </div>
            <div className="stat-card safe">
              <div className="stat-number">{data.safe_scans || 0}</div>
              <div className="stat-label">Safe URLs</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-number">{data.warning_scans || 0}</div>
              <div className="stat-label">Warnings</div>
            </div>
            <div className="stat-card dangerous">
              <div className="stat-number">{data.dangerous_scans || 0}</div>
              <div className="stat-label">Dangerous</div>
            </div>
          </div>
          
          {data.total_decisions > 0 && (
            <div className="decisions-summary">
              <h4>Decisions Made: {data.total_decisions}</h4>
              <div className="decision-breakdown">
                <span className="decision-item safe">Safe: {data.safe_decisions}</span>
                <span className="decision-item warning">Warning: {data.warning_decisions}</span>
                <span className="decision-item dangerous">Dangerous: {data.dangerous_decisions}</span>
              </div>
            </div>
          )}
        </div>
        
        {/* Behavioral Metrics */}
        <div className="analytics-grid">
          <div className="metric-card">
            <h3>Phishing Susceptibility</h3>
            <div className="score-circle" style={{ borderColor: getScoreColor(100 - data.phishing_susceptibility_score) }}>
              <span className="score-value">{100 - data.phishing_susceptibility_score}</span>
              <span className="score-label">/100</span>
            </div>
            <p className="score-level">{getScoreLevel(100 - data.phishing_susceptibility_score)}</p>
            <p className="metric-description">Lower susceptibility indicates better phishing detection</p>
          </div>
          
          <div className="metric-card">
            <h3>Security Compliance</h3>
            <div className="score-circle" style={{ borderColor: getScoreColor(data.security_compliance_score) }}>
              <span className="score-value">{data.security_compliance_score}</span>
              <span className="score-label">/100</span>
            </div>
            <p className="score-level">{getScoreLevel(data.security_compliance_score)}</p>
            <p className="metric-description">Follows security recommendations effectively</p>
          </div>
          
          <div className="metric-card">
            <h3>Risk Perception</h3>
            <div className="score-circle" style={{ borderColor: getScoreColor(data.risk_perception_score) }}>
              <span className="score-value">{data.risk_perception_score}</span>
              <span className="score-label">/100</span>
            </div>
            <p className="score-level">{getScoreLevel(data.risk_perception_score)}</p>
            <p className="metric-description">Ability to quickly identify potential threats</p>
          </div>
        </div>
        
        {/* Behavioral Insights */}
        <div className="behavioral-insights">
          <h3>🎯 Behavioral Insights</h3>
          <div className="insights-list">
            {data.behavioral_insights && data.behavioral_insights.length > 0 ? (
              data.behavioral_insights.map((insight, index) => (
                <div key={index} className="insight-item">
                  {insight}
                </div>
              ))
            ) : (
              <div className="insight-item">
                Start scanning URLs and making decisions to get personalized insights
              </div>
            )}
          </div>
        </div>
        
        {/* Recommendations */}
        <div className="recommendations">
          <h3>💡 Security Recommendations</h3>
          <ul>
            <li>Always verify SSL certificates before entering sensitive information</li>
            <li>Be cautious of URLs with multiple redirects</li>
            <li>Check domain age and reputation for unknown websites</li>
            <li>Use this scanner for suspicious links before clicking</li>
            {data.total_scans < 5 && (
              <li><strong>Scan more URLs to get better behavioral insights!</strong></li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}