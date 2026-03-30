// Loader.js
import React from "react";

export default function Loader() {
  return (
    <div className="loader-container">
      <div className="loader-spinner"></div>
      <p className="loader-text">Analyzing URL security...</p>
      <p className="loader-subtext">This may take a few seconds</p>
    </div>
  );
}