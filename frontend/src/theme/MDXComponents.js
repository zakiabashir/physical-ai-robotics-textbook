import React from 'react';
import InteractiveCode from '@site/src/components/InteractiveCode';
import Quiz from '@site/src/components/Quiz';
import QuizComponent from '@site/src/components/QuizComponent';
import DiagramComponent from '@site/src/components/DiagramComponent';
import CodeComponent from '@site/src/components/CodeComponent';
import CodeBlock from '@theme/CodeBlock';
import Admonition from '@theme/Admonition';

const MDXComponents = {
  // Interactive Code Block
  InteractiveCode: (props) => <InteractiveCode {...props} />,

  // Quiz Component
  Quiz: (props) => <Quiz {...props} />,

  // Enhanced Code Block with run button for Python
  code: (props) => {
    if (props.className === 'language-python') {
      return <InteractiveCode language="python" {...props} />;
    }
    return <CodeBlock {...props} />;
  },

  // Activity component
  Activity: ({ children, title, type = 'hands-on' }) => (
    <div className="activity-container">
      <div className="activity-header">
        <div className="activity-icon">
          {type === 'hands-on' ? '🛠️' : type === 'lab' ? '🔬' : '📚'}
        </div>
        <h3 className="activity-title">{title || 'Activity'}</h3>
      </div>
      <div className="activity-content">
        {children}
      </div>
    </div>
  ),

  // Learning Objectives component
  LearningObjectives: ({ children }) => (
    <Admonition type="info" title="Learning Objectives">
      <ul>
        {React.Children.map(children, (child, index) => (
          <li key={index}>{child}</li>
        ))}
      </ul>
    </Admonition>
  ),

  // Key Concept highlight
  KeyConcept: ({ children, term }) => (
    <Admonition type="tip" title={`Key Concept: ${term}`}>
      {children}
    </Admonition>
  ),

  // Practice Exercise component
  Practice: ({ children, difficulty = 'medium' }) => (
    <Admonition
      type="note"
      title={
        <span>
          Practice Exercise
          <span style={{
            marginLeft: 8,
            fontSize: '0.8em',
            background: difficulty === 'easy' ? '#4caf50' : difficulty === 'hard' ? '#ff9800' : '#2196f3',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '12px'
          }}>
            {difficulty}
          </span>
        </span>
      }
    >
      {children}
    </Admonition>
  ),

  // Warning component
  Warning: ({ children }) => (
    <Admonition type="caution" title="Important">
      {children}
    </Admonition>
  ),

  // Formula/Math component (simplified)
  Formula: ({ children, label }) => (
    <div className="formula-container">
      {label && <label>{label}:</label>}
      <div className="formula">
        {children}
      </div>
    </div>
  ),

  // Embedded Mermaid diagram
  Diagram: ({ children, caption }) => (
    <div className="mermaid-diagram">
      <div className="mermaid">
        {children}
      </div>
      {caption && <p className="diagram-caption">{caption}</p>}
    </div>
  ),

  // Step-by-step instructions
  Steps: ({ children }) => {
    const steps = React.Children.toArray(children);
    return (
      <div className="activity-steps">
        {steps.map((step, index) => (
          <div key={index} className="activity-step">
            <div className="step-number">{index + 1}</div>
            <div className="step-content">{step}</div>
          </div>
        ))}
      </div>
    );
  },

  // New Quiz Component
  QuizComponent: (props) => <QuizComponent {...props} />,

  // Enhanced Diagram Component
  DiagramComponent: (props) => <DiagramComponent {...props} />,

  // Enhanced Code Component (for backward compatibility)
  CodeRunner: (props) => <CodeComponent {...props} />
};

export default MDXComponents;