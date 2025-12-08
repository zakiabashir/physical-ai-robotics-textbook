import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const RAGMonitor = () => {
  const [healthData, setHealthData] = useState(null);
  const [ingestionStats, setIngestionStats] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all health data
      const [healthResponse, ragResponse, ingestionResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/health/detailed`),
        axios.get(`${API_BASE_URL}/health/rag`),
        axios.get(`${API_BASE_URL}/ingestion/status`)
      ]);

      setHealthData(healthResponse.data);
      setIngestionStats({
        rag: ragResponse.data,
        ingestion: ingestionResponse.data
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const runIngestionTest = async () => {
    try {
      setTestResults(null);
      const response = await axios.post(`${API_BASE_URL}/health/ingestion/test`);
      setTestResults(response.data);
    } catch (err) {
      setTestResults({
        overall: 'failed',
        error: err.response?.data?.detail || err.message
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#52c41a';
      case 'degraded': return '#faad14';
      case 'unhealthy': return '#f5222d';
      case 'needs_ingestion': return '#1890ff';
      case 'slow': return '#fa8c16';
      default: return '#d9d9d9';
    }
  };

  const getStatusBadge = (status) => (
    <span
      style={{
        backgroundColor: getStatusColor(status),
        color: 'white',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 'bold',
        textTransform: 'uppercase'
      }}
    >
      {status}
    </span>
  );

  if (loading && !healthData) {
    return (
      <Layout title="RAG Monitor">
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <div>Loading RAG monitoring data...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="RAG System Monitor">
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '30px' }}>
          <h1>🤖 RAG System Monitor</h1>
          <p>Monitor the health and performance of the Retrieval-Augmented Generation system</p>
        </div>

        {error && (
          <div style={{
            backgroundColor: '#fff2f0',
            border: '1px solid #ffccc7',
            borderRadius: '4px',
            padding: '12px',
            marginBottom: '20px'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Overall System Status */}
        <div style={{
          backgroundColor: '#f0f9ff',
          border: '1px solid #bae7ff',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h2>Overall System Status</h2>
          {healthData && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>Status:</span>
              {getStatusBadge(healthData.overall)}
              <span style={{ marginLeft: '20px', color: '#666' }}>
                Last updated: {new Date(healthData.timestamp * 1000).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        {/* Component Health */}
        <div style={{
          backgroundColor: '#f6ffed',
          border: '1px solid #b7eb8f',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h2>Component Health</h2>
          {healthData?.components && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {Object.entries(healthData.components).map(([component, data]) => (
                <div key={component} style={{
                  backgroundColor: 'white',
                  border: `1px solid ${getStatusColor(data.status)}`,
                  borderRadius: '4px',
                  padding: '15px'
                }}>
                  <h3 style={{ margin: '0 0 10px 0', textTransform: 'capitalize' }}>
                    {component}
                  </h3>
                  <div>{getStatusBadge(data.status)}</div>
                  {data.error && (
                    <div style={{ color: '#f5222d', fontSize: '12px', marginTop: '5px' }}>
                      Error: {data.error}
                    </div>
                  )}
                  {data.collections && (
                    <div style={{ marginTop: '10px' }}>
                      <strong>Collections:</strong> {data.collections.join(', ')}
                    </div>
                  )}
                  {data.total_documents !== undefined && (
                    <div style={{ marginTop: '5px' }}>
                      <strong>Documents:</strong> {data.total_documents.toLocaleString()}
                    </div>
                  )}
                  {data.embedding_dimension && (
                    <div style={{ marginTop: '5px' }}>
                      <strong>Embedding Dimension:</strong> {data.embedding_dimension}
                    </div>
                  )}
                  {data.model && (
                    <div style={{ marginTop: '5px' }}>
                      <strong>Model:</strong> {data.model}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* RAG Specific Stats */}
        {ingestionStats && (
          <div style={{
            backgroundColor: '#fff9e6',
            border: '1px solid #ffd666',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px'
          }}>
            <h2>RAG Performance Metrics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              {/* Ingestion */}
              <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '4px' }}>
                <h4>📥 Ingestion</h4>
                <p><strong>Status:</strong> {getStatusBadge(ingestionStats.rag.ingestion.status)}</p>
                {ingestionStats.rag.ingestion.document_count !== undefined && (
                  <p><strong>Documents:</strong> {ingestionStats.rag.ingestion.document_count.toLocaleString()}</p>
                )}
                {ingestionStats.rag.ingestion.message && (
                  <p style={{ color: '#666', fontSize: '14px' }}>{ingestionStats.rag.ingestion.message}</p>
                )}
              </div>

              {/* Retrieval */}
              <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '4px' }}>
                <h4>🔍 Retrieval</h4>
                <p><strong>Status:</strong> {getStatusBadge(ingestionStats.rag.retrieval.status)}</p>
                {ingestionStats.rag.retrieval.query_time_ms && (
                  <p><strong>Query Time:</strong> {ingestionStats.rag.retrieval.query_time_ms}ms</p>
                )}
                {ingestionStats.rag.retrieval.avg_score && (
                  <p><strong>Avg Score:</strong> {(ingestionStats.rag.retrieval.avg_score * 100).toFixed(1)}%</p>
                )}
                {ingestionStats.rag.retrieval.warning && (
                  <p style={{ color: '#fa8c16', fontSize: '14px' }}>⚠️ {ingestionStats.rag.retrieval.warning}</p>
                )}
              </div>

              {/* Generation */}
              <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '4px' }}>
                <h4>💬 Generation</h4>
                <p><strong>Status:</strong> {getStatusBadge(ingestionStats.rag.generation.status)}</p>
                {ingestionStats.rag.generation.response_time_ms && (
                  <p><strong>Response Time:</strong> {ingestionStats.rag.generation.response_time_ms}ms</p>
                )}
                {ingestionStats.rag.generation.model && (
                  <p><strong>Model:</strong> {ingestionStats.rag.generation.model}</p>
                )}
                {ingestionStats.rag.generation.warning && (
                  <p style={{ color: '#fa8c16', fontSize: '14px' }}>⚠️ {ingestionStats.rag.generation.warning}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Test Controls */}
        <div style={{
          backgroundColor: '#f9f0ff',
          border: '1px solid #d3adf7',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h2>System Tests</h2>
          <button
            onClick={runIngestionTest}
            disabled={loading}
            style={{
              backgroundColor: '#1890ff',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginRight: '10px'
            }}
          >
            Run Ingestion Pipeline Test
          </button>
          <button
            onClick={fetchHealthData}
            disabled={loading}
            style={{
              backgroundColor: '#52c41a',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            Refresh Data
          </button>

          {testResults && (
            <div style={{ marginTop: '20px', backgroundColor: 'white', padding: '15px', borderRadius: '4px' }}>
              <h3>Test Results</h3>
              <p><strong>Overall:</strong> {getStatusBadge(testResults.overall)}</p>
              {testResults.tests && (
                <div style={{ marginTop: '10px' }}>
                  {Object.entries(testResults.tests).map(([test, result]) => (
                    <div key={test} style={{ marginBottom: '10px' }}>
                      <strong>{test.replace('_', ' ')}:</strong> {getStatusBadge(result.status)}
                      {result.error && <span style={{ color: '#f5222d', marginLeft: '10px' }}>{result.error}</span>}
                      {result.urls_found && <span style={{ marginLeft: '10px' }}>URLs: {result.urls_found}</span>}
                      {result.chars_extracted && <span style={{ marginLeft: '10px' }}>Chars: {result.chars_extracted.toLocaleString()}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* API Links */}
        <div style={{
          backgroundColor: '#f0f0f0',
          border: '1px solid #d9d9d9',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <h2>API Endpoints</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li><a href={`${API_BASE_URL}/docs`} target="_blank" rel="noopener noreferrer">📚 API Documentation</a></li>
            <li><a href={`${API_BASE_URL}/health`} target="_blank" rel="noopener noreferrer">💓 Basic Health</a></li>
            <li><a href={`${API_BASE_URL}/health/detailed`} target="_blank" rel="noopener noreferrer">📊 Detailed Health</a></li>
            <li><a href={`${API_BASE_URL}/health/rag`} target="_blank" rel="noopener noreferrer">🤖 RAG Health</a></li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};

export default RAGMonitor;