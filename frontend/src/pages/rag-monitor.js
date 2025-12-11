import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import axios from 'axios';

const API_BASE_URL = '/api/v1';
const API_FULL_URL = 'http://localhost:8000/api/v1';

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
        background: `linear-gradient(145deg, ${getStatusColor(status)} 0%, ${getStatusColor(status)}dd 100%)`,
        color: 'white',
        padding: '6px 14px',
        borderRadius: '20px',
        fontSize: '11px',
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        boxShadow: `0 2px 8px ${getStatusColor(status)}55`,
        border: '1px solid rgba(255, 255, 255, 0.3)',
        transition: 'all 0.3s ease'
      }}
    >
      {status}
    </span>
  );

  if (loading && !healthData) {
    return (
      <Layout title="RAG Monitor">
        <div className="rag-monitor-container">
          <div style={{ textAlign: 'center' }}>Loading RAG monitoring data...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="RAG System Monitor">
      <div style={{
        minHeight: '100vh',
        background: `
          linear-gradient(135deg, #1e3c72 0%, #2a5298 20%, #7e57c2 40%, #b39ddb 60%, #ce93d8 80%, #f48fb1 100%),
          radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%)
        `,
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.5s ease'
      }}>
        {/* Animated background circles */}
        <div style={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '300px',
          height: '300px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          animation: 'float 6s ease-in-out infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '10%',
          right: '10%',
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
          animation: 'float 8s ease-in-out infinite reverse'
        }} />

        <div style={{
          marginBottom: '40px',
          textAlign: 'center',
          position: 'relative',
          zIndex: 10,
          animation: 'fadeInDown 1s ease-out'
        }}>
          <h1 style={{
            color: 'white',
            textShadow: '3px 3px 6px rgba(0,0,0,0.4)',
            fontSize: '3rem',
            fontWeight: 'bold',
            marginBottom: '10px',
            background: 'linear-gradient(45deg, #ffffff, #f0f0ff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🤖 RAG System Monitor
          </h1>
          <p style={{
            color: 'rgba(255, 255, 255, 0.95)',
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
            fontSize: '1.2rem',
            fontWeight: '300'
          }}>
            Monitor the health and performance of the Retrieval-Augmented Generation system
          </p>
        </div>

        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.97)',
          borderRadius: '20px',
          padding: '40px',
          maxWidth: '1200px',
          width: '100%',
          boxShadow: '0 25px 80px rgba(0, 0, 0, 0.25)',
          backdropFilter: 'blur(15px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          position: 'relative',
          zIndex: 10,
          animation: 'fadeInUp 1s ease-out'
        }}>

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
          background: 'linear-gradient(135deg, #4fc3f7 0%, #29b6f6 50%, #039be5 100%)',
          borderRadius: '16px',
          padding: '30px',
          marginBottom: '30px',
          boxShadow: '0 10px 30px rgba(3, 155, 229, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.4)',
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s ease'
        }}>
          <div style={{
            position: 'absolute',
            top: '-50%',
            right: '-50%',
            width: '200%',
            height: '200%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
            animation: 'rotate 20s linear infinite'
          }} />
          <h2 style={{
            color: 'white',
            marginBottom: '15px',
            fontSize: '1.5rem',
            fontWeight: '600',
            textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
          }}>Overall System Status</h2>
          {healthData && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '15px',
              color: 'white',
              fontSize: '1.05rem'
            }}>
              <span style={{ fontWeight: '500' }}>Status:</span>
              {getStatusBadge(healthData.overall)}
              <span style={{
                marginLeft: '30px',
                opacity: '0.95',
                fontSize: '0.95rem'
              }}>
                Last updated: {new Date(healthData.timestamp * 1000).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        {/* Component Health */}
        <div style={{
          background: 'linear-gradient(135deg, #66bb6a 0%, #4caf50 50%, #388e3c 100%)',
          borderRadius: '16px',
          padding: '30px',
          marginBottom: '30px',
          boxShadow: '0 10px 30px rgba(56, 142, 60, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.4)',
          position: 'relative'
        }}>
          <div style={{
            position: 'absolute',
            bottom: '-30%',
            left: '-10%',
            width: '120%',
            height: '120%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)'
          }} />
          <h2 style={{
            color: 'white',
            marginBottom: '25px',
            fontSize: '1.5rem',
            fontWeight: '600',
            textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
          }}>Component Health</h2>
          {healthData?.components && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '20px',
              position: 'relative',
              zIndex: 1
            }}>
              {Object.entries(healthData.components).map(([component, data]) => (
                <div key={component} style={{
                  background: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '12px',
                  padding: '20px',
                  border: `2px solid ${getStatusColor(data.status)}`,
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '4px',
                    background: `linear-gradient(90deg, ${getStatusColor(data.status)}, ${getStatusColor(data.status)}dd)`
                  }} />
                  <h3 style={{
                    margin: '0 0 12px 0',
                    textTransform: 'capitalize',
                    color: '#2c3e50',
                    fontSize: '1.1rem',
                    fontWeight: '600'
                  }}>
                    {component}
                  </h3>
                  <div style={{ marginBottom: '12px' }}>
                    {getStatusBadge(data.status)}
                  </div>
                  {data.error && (
                    <div style={{
                      color: '#e74c3c',
                      fontSize: '13px',
                      marginTop: '10px',
                      padding: '8px',
                      backgroundColor: '#ffebee',
                      borderRadius: '6px'
                    }}>
                      Error: {data.error}
                    </div>
                  )}
                  {data.collections && (
                    <div style={{ marginTop: '10px', color: '#555' }}>
                      <strong>Collections:</strong> {data.collections.join(', ')}
                    </div>
                  )}
                  {data.total_documents !== undefined && (
                    <div style={{ marginTop: '8px', color: '#555' }}>
                      <strong>Documents:</strong> {data.total_documents.toLocaleString()}
                    </div>
                  )}
                  {data.embedding_dimension && (
                    <div style={{ marginTop: '8px', color: '#555' }}>
                      <strong>Embedding Dimension:</strong> {data.embedding_dimension}
                    </div>
                  )}
                  {data.model && (
                    <div style={{ marginTop: '8px', color: '#555' }}>
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
            background: 'linear-gradient(145deg, #fefce8 0%, #fef3c7 100%)',
            border: '1px solid #ffd666',
            borderRadius: '12px',
            padding: '25px',
            marginBottom: '25px',
            boxShadow: '0 4px 15px rgba(251, 146, 60, 0.1)'
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
          background: 'linear-gradient(145deg, #faf5ff 0%, #f3e8ff 100%)',
          border: '1px solid #d3adf7',
          borderRadius: '12px',
          padding: '25px',
          marginBottom: '25px',
          boxShadow: '0 4px 15px rgba(168, 85, 247, 0.1)'
        }}>
          <h2>System Tests</h2>
          <button
            onClick={runIngestionTest}
            disabled={loading}
            style={{
              background: loading
                ? 'linear-gradient(135deg, #b0bec5 0%, #90a4ae 100%)'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '12px 28px',
              borderRadius: '25px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginRight: '15px',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
              transition: 'all 0.3s ease',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
              }
            }}
            onMouseOut={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
              }
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
          background: 'linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%)',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '25px',
          boxShadow: '0 4px 15px rgba(148, 163, 184, 0.1)'
        }}>
          <h2>API Endpoints</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li><a href={`${API_FULL_URL}/docs`} target="_blank" rel="noopener noreferrer">📚 API Documentation</a></li>
            <li><a href={`${API_FULL_URL}/health`} target="_blank" rel="noopener noreferrer">💓 Basic Health</a></li>
            <li><a href={`${API_FULL_URL}/health/detailed`} target="_blank" rel="noopener noreferrer">📊 Detailed Health</a></li>
            <li><a href={`${API_FULL_URL}/health/rag`} target="_blank" rel="noopener noreferrer">🤖 RAG Health</a></li>
          </ul>
        </div>
        </div>
      </div>
    </Layout>
  );
};

export default RAGMonitor;