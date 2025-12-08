import React, { useState, useEffect } from 'react';
import './styles.css';

const CodeComponent = ({
  children,
  language = 'python',
  title = '',
  editable = false,
  runnable = false
}) => {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    // Extract code from children
    if (children) {
      const childrenStr = Array.isArray(children) ? children.join('') : String(children);
      const codeMatch = childrenStr.match(/```(\w+)?\n([\s\S]*?)```/);
      if (codeMatch) {
        setCode(codeMatch[2]);
      } else {
        setCode(childrenStr);
      }
    }
  }, [children]);

  const runCode = async () => {
    if (!runnable) return;

    setIsRunning(true);
    setOutput('Running code...\n\n');

    try {
      // Simple console output capture for Python
      const logs = [];
      const originalLog = console.log;
      console.log = (...args) => {
        logs.push(args.join(' '));
      };

      // Create a function from the code
      const func = new Function(code);
      func();

      // Restore console.log
      console.log = originalLog;

      setOutput(prev => prev + logs.join('\n'));
    } catch (error) {
      setOutput(prev => prev + `Error: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    // Could add a toast notification here
  };

  return (
    <div className="code-component">
      {title && <div className="code-title">{title}</div>}
      <div className="code-block">
        <div className="code-header">
          <span className="language-tag">{language}</span>
          <div className="code-actions">
            {editable && (
              <button
                className="code-button"
                onClick={() => {
                  const textarea = document.createElement('textarea');
                  textarea.value = code;
                  document.body.appendChild(textarea);
                  textarea.select();
                  document.execCommand('copy');
                  document.body.removeChild(textarea);
                }}
              >
                Copy
              </button>
            )}
            {runnable && (
              <button
                className="code-button run-button"
                onClick={runCode}
                disabled={isRunning}
              >
                {isRunning ? 'Running...' : 'Run Code'}
              </button>
            )}
          </div>
        </div>
        <pre className="code-content">
          <code className={`language-${language}`}>{code}</code>
        </pre>
      </div>
      {output && (
        <div className="output-block">
          <div className="output-header">Output:</div>
          <pre className="output-content">{output}</pre>
        </div>
      )}
    </div>
  );
};

export default CodeComponent;