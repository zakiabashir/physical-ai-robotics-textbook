import React from 'react';
import './styles.css';

const DiagramComponent = ({ title, children, type = 'default' }) => {
  return (
    <div className={`diagramContainer ${type}`}>
      {title && <h4 className="diagramTitle">{title}</h4>}
      <div className="diagramContent">
        {children}
      </div>
    </div>
  );
};

export default DiagramComponent;