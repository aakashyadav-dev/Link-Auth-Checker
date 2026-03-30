// UrlInput.js
import React, { useState } from "react";

export default function UrlInput({ onCheck }) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onCheck(url);
  };

  return (
    <div className="url-input-container">
      <form onSubmit={handleSubmit} className="url-input-form">
        <div className="input-group">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL to analyze (e.g., https://example.com)"
            className="url-input"
            type="url"
          />
          <button 
            type="submit" 
            className="scan-button"
            disabled={!url.trim()}
          >
            <span className="button-text">Scan URL</span>
            <span className="button-icon">🔍</span>
          </button>
        </div>
        <p className="input-hint">
          Enter a full URL including http:// or https:// for accurate analysis
        </p>
      </form>
    </div>
  );
}