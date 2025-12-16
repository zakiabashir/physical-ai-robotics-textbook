import React, { useState } from 'react';
import './feedback.css';

const FeedbackComponent = ({ messageId, onFeedbackSubmit }) => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState('');
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRating = (value) => {
    setRating(value);
    setShowFeedback(true);
  };

  const handleSubmit = async () => {
    if (!rating) return;

    const feedbackData = {
      messageId,
      rating,
      category,
      comment,
      timestamp: new Date().toISOString()
    };

    try {
      // Send feedback to backend
      await fetch(`https://physical-ai-robotics-textbook-production.up.railway.app/api/v1/chat/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      setSubmitted(true);
      onFeedbackSubmit?.(feedbackData);

      // Hide feedback form after 2 seconds
      setTimeout(() => {
        setShowFeedback(false);
        setSubmitted(false);
        setRating(0);
        setCategory('');
        setComment('');
      }, 2000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  if (submitted) {
    return (
      <div className="feedback-submitted">
        <span>✓ Thank you for your feedback!</span>
      </div>
    );
  }

  return (
    <div className="feedback-container">
      <div className="feedback-prompt">
        Was this response helpful?
      </div>
      <div className="feedback-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={`star-btn ${star <= rating ? 'active' : ''}`}
            onClick={() => handleRating(star)}
            aria-label={`Rate ${star} stars`}
          >
            ★
          </button>
        ))}
      </div>

      {showFeedback && (
        <div className="feedback-form">
          <div className="feedback-category">
            <label>Category:</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">Select...</option>
              <option value="helpful">Helpful</option>
              <option value="incorrect">Incorrect</option>
              <option value="irrelevant">Irrelevant</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="feedback-comment">
            <label>Additional comments (optional):</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us more..."
              rows={3}
              maxLength={500}
            />
          </div>

          <div className="feedback-actions">
            <button onClick={() => setShowFeedback(false)}>Cancel</button>
            <button onClick={handleSubmit} className="submit-btn">Submit</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackComponent;