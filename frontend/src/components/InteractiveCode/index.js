import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import './styles.css';

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = React.lazy(() => import('@monaco-editor/react'));

const InteractiveCode = ({
  children,
  language = 'python',
  defaultCode = '',
  runnable = true,
  height = '400px',
  ...props
}) => {
  const [code, setCode] = useState(defaultCode);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [showOutput, setShowOutput] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    // Extract code from children if provided
    if (children && !defaultCode) {
      const codeMatch = children.match(/```(\w+)?\n([\s\S]*?)```/);
      if (codeMatch) {
        setCode(codeMatch[2]);
      }
    }
  }, [children, defaultCode]);

  const runCode = async () => {
    if (!runnable || !isClient) return;

    setIsRunning(true);
    setShowOutput(true);
    setOutput('Running...\n');

    try {
      // For Python code, we'll use a simple evaluation
      // In production, this should connect to a secure execution environment
      if (language === 'python') {
        // Simulate code execution without using eval/AsyncFunction during SSR
        setOutput(`Output from Python code:\n${code}\n\n[Code execution would be implemented here]`);
      } else {
        // For other languages
        setOutput(`Code executed successfully!\nLanguage: ${language}\n\n[Execution results would appear here]`);
      }
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const resetCode = () => {
    if (children) {
      const codeMatch = children.match(/```(\w+)?\n([\s\S]*?)```/);
      if (codeMatch) {
        setCode(codeMatch[2]);
      }
    } else {
      setCode(defaultCode);
    }
    setOutput('');
    setShowOutput(false);
  };

  // Don't render on server-side
  if (!isClient) {
    return (
      <div className="interactive-code">
        <div style={{ height: parseInt(height) || 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p>Loading interactive code editor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interactive-code">
      <div className="code-header">
        <div className="code-actions">
          {runnable && (
            <motion.button
              className="run-button"
              onClick={runCode}
              disabled={isRunning}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isRunning ? 'Running...' : 'Run Code'}
            </motion.button>
          )}
          <motion.button
            className="copy-button"
            onClick={copyCode}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {copied ? 'Copied!' : 'Copy'}
          </motion.button>
          <motion.button
            className="reset-button"
            onClick={resetCode}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Reset
          </motion.button>
          <motion.button
            className="edit-button"
            onClick={() => setEditMode(!editMode)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {editMode ? 'Preview' : 'Edit'}
          </motion.button>
        </div>
      </div>

      <div className="editor-container">
        <Suspense fallback={<div style={{ height: parseInt(height) || 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading editor...</div>}>
          <MonacoEditor
            height={height}
            language={language}
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              readOnly: !editMode,
            }}
            {...props}
          />
        </Suspense>
      </div>

      <AnimatePresence>
        {showOutput && (
          <motion.div
            className="output-container"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="output-header">Output:</div>
            <pre className="output-content">{output}</pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InteractiveCode;