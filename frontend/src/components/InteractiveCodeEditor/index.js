import React, { useState, useRef, useEffect, Suspense } from 'react';
import { Button, Card, Space, Typography, message } from 'antd';
import PlayCircleOutlined from '@ant-design/icons/PlayCircleOutlined';
import CopyOutlined from '@ant-design/icons/CopyOutlined';
import SaveOutlined from '@ant-design/icons/SaveOutlined';
import './styles.css';

// Dynamically import Monaco Editor to avoid SSR issues
const Editor = React.lazy(() => import('@monaco-editor/react'));

const { Text } = Typography;

const InteractiveCodeEditor = ({
  language = 'python',
  defaultValue = '',
  theme = 'vs-dark',
  height = '400px',
  options = {},
  showRunButton = true,
  showCopyButton = true,
  showSaveButton = true,
  onRun,
  onSave,
  readOnly = false,
  title = null,
  description = null,
  expectedOutput = null
}) => {
  const [code, setCode] = useState(defaultValue);
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const editorRef = useRef(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleRunCode = async () => {
    if (!isClient) return;

    setIsLoading(true);
    try {
      if (onRun) {
        const result = await onRun(code);
        setOutput(result);
      } else {
        // Default execution logic
        setOutput('Running code...\n\n(Code execution would be implemented here)');
      }
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    message.success('Code copied to clipboard!');
  };

  const handleSaveCode = () => {
    if (onSave) {
      onSave(code);
      message.success('Code saved!');
    } else {
      // Default save to localStorage only on client-side
      if (isClient && typeof window !== 'undefined') {
        try {
          const savedCode = JSON.parse(localStorage.getItem('savedCode') || '{}');
          const key = `code_${Date.now()}`;
          savedCode[key] = {
            code,
            language,
            timestamp: new Date().toISOString()
          };
          localStorage.setItem('savedCode', JSON.stringify(savedCode));
          message.success('Code saved locally!');
        } catch (error) {
          console.error('Error saving code to localStorage:', error);
          message.error('Failed to save code locally');
        }
      }
    }
  };

  const defaultOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    readOnly,
    ...options
  };

  // Don't render on server-side
  if (!isClient) {
    return (
      <Card title={title} className="interactive-code-editor">
        <div style={{ height: parseInt(height) || 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Text type="secondary">Loading editor...</Text>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={title}
      className="interactive-code-editor"
      extra={
        <Space>
          {showRunButton && (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleRunCode}
              loading={isLoading}
            >
              Run Code
            </Button>
          )}
          {showCopyButton && (
            <Button
              icon={<CopyOutlined />}
              onClick={handleCopyCode}
            >
              Copy
            </Button>
          )}
          {showSaveButton && (
            <Button
              icon={<SaveOutlined />}
              onClick={handleSaveCode}
            >
              Save
            </Button>
          )}
        </Space>
      }
    >
      {description && (
        <div className="editor-description">
          <Text type="secondary">{description}</Text>
        </div>
      )}

      <Suspense fallback={<div style={{ height: parseInt(height) || 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading editor...</div>}>
        <Editor
          height={height}
          language={language}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme={theme}
          options={defaultOptions}
          onMount={(editor) => {
            editorRef.current = editor;
          }}
        />
      </Suspense>

      {output && (
        <div className="output-container">
          <h4>Output:</h4>
          <pre className="output-content">{output}</pre>
          {expectedOutput && (
            <div className="expected-output">
              <h5>Expected Output:</h5>
              <pre>{expectedOutput}</pre>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default InteractiveCodeEditor;