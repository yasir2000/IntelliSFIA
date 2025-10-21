import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

// Simple test to verify React is working
function TestApp() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    setTimeout(() => {
      setMessage('✅ React is working! SFIA 9 Framework loaded successfully.');
    }, 1000);
  }, []);

  return (
    <div style={{
      padding: '40px',
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <h1 style={{ color: '#667eea', marginBottom: '20px' }}>
          🎯 SFIA 9 Framework - Test Page
        </h1>
        
        <div style={{
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '4px',
          padding: '15px',
          marginBottom: '20px',
          color: '#155724'
        }}>
          <strong>{message}</strong>
        </div>

        <div style={{
          backgroundColor: '#cce5ff',
          border: '1px solid #99ccff', 
          borderRadius: '4px',
          padding: '15px',
          marginBottom: '20px',
          color: '#004085'
        }}>
          <strong>Status:</strong> If you can see this message, the React application is running correctly.
        </div>

        <button
          onClick={() => setMessage('🚀 Button clicked! Interactive features are working.')}
          style={{
            padding: '12px 24px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '16px',
            marginRight: '10px'
          }}
        >
          Test Button
        </button>

        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '12px 24px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Reload Page
        </button>
      </div>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        marginTop: '20px'
      }}>
        <h2 style={{ color: '#333', marginBottom: '15px' }}>🔧 Debug Information</h2>
        <ul style={{ textAlign: 'left', lineHeight: '1.6' }}>
          <li><strong>React Version:</strong> 18+</li>
          <li><strong>Server:</strong> localhost:3000</li>
          <li><strong>Build:</strong> Development mode</li>
          <li><strong>Timestamp:</strong> {new Date().toLocaleString()}</li>
        </ul>
      </div>
    </div>
  );
}

// Root render
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<TestApp />);