import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles.css';

const Quiz = ({ questions, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    // Initialize answers array
    if (questions && questions.length > 0) {
      setAnswers(new Array(questions.length).fill(null));
    }
  }, [questions]);

  const handleOptionSelect = (optionIndex) => {
    if (showFeedback) return;

    setSelectedOption(optionIndex);
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = optionIndex;
    setAnswers(newAnswers);
    setShowFeedback(true);

    // Update score
    const question = questions[currentQuestion];
    if (question.type === 'multiple-choice' && optionIndex === question.correctAnswer) {
      setScore(score + 1);
    }
  };

  const handleNext = () => {
    setShowFeedback(false);
    setSelectedOption(null);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
      if (onComplete) {
        onComplete({
          score: score + (selectedOption === questions[currentQuestion].correctAnswer ? 1 : 0),
          totalQuestions: questions.length,
          answers: [...answers, selectedOption]
        });
      }
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setShowFeedback(false);
      setSelectedOption(null);
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleRestart = () => {
    setCurrentQuestion(0);
    setAnswers(new Array(questions.length).fill(null));
    setShowResults(false);
    setSelectedOption(null);
    setShowFeedback(false);
    setScore(0);
  };

  const getScoreMessage = () => {
    const percentage = (score / questions.length) * 100;
    if (percentage === 100) return "Perfect! You've mastered this topic! 🎉";
    if (percentage >= 80) return "Excellent work! You have a strong understanding! 🌟";
    if (percentage >= 60) return "Good job! Consider reviewing the concepts you missed. 📚";
    return "Keep learning! Review the material and try again. 💪";
  };

  if (!questions || questions.length === 0) {
    return (
      <div className="quiz-container">
        <p>No quiz questions available.</p>
      </div>
    );
  }

  if (showResults) {
    return (
      <motion.div
        className="quiz-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="quiz-results">
          <h3>Quiz Complete!</h3>
          <div className="score-display">
            <div className="score-circle">
              <span className="score-text">{Math.round((score / questions.length) * 100)}%</span>
            </div>
            <p className="score-message">{getScoreMessage()}</p>
          </div>
          <div className="score-details">
            <p>You got {score} out of {questions.length} questions correct.</p>
          </div>
          <button className="quiz-btn primary" onClick={handleRestart}>
            Retake Quiz
          </button>
        </div>
      </motion.div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <motion.div
      className="quiz-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      key={currentQuestion}
    >
      <div className="quiz-header">
        <span className="question-progress">
          Question {currentQuestion + 1} of {questions.length}
        </span>
        <div className="progress-dots">
          {questions.map((_, index) => (
            <div
              key={index}
              className={`progress-dot ${index === currentQuestion ? 'active' : ''} ${answers[index] !== null ? 'answered' : ''}`}
              onClick={() => {
                if (!showFeedback) {
                  setCurrentQuestion(index);
                  setSelectedOption(answers[index]);
                }
              }}
            />
          ))}
        </div>
      </div>

      <div className="quiz-question">
        <h4>{question.question}</h4>
        {question.code && (
          <pre className="question-code">
            <code>{question.code}</code>
          </pre>
        )}
      </div>

      <div className="quiz-options">
        <AnimatePresence>
          {question.options.map((option, index) => {
            const isSelected = selectedOption === index;
            const isCorrect = question.type === 'multiple-choice' && index === question.correctAnswer;
            const showCorrect = showFeedback && isCorrect;
            const showIncorrect = showFeedback && isSelected && !isCorrect;

            return (
              <motion.div
                key={index}
                className={`quiz-option ${isSelected ? 'selected' : ''} ${showCorrect ? 'correct' : ''} ${showIncorrect ? 'incorrect' : ''}`}
                onClick={() => handleOptionSelect(index)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
              >
                <span className="option-label">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
                {showCorrect && <span className="option-indicator correct">✓</span>}
                {showIncorrect && <span className="option-indicator incorrect">✗</span>}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {showFeedback && (
          <motion.div
            className={`quiz-feedback ${selectedOption === question.correctAnswer ? 'success' : 'error'}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <p>{question.explanation || (selectedOption === question.correctAnswer ? 'Correct!' : 'Incorrect. Try reviewing the material.')}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="quiz-navigation">
        <button
          className="quiz-btn secondary"
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
        >
          Previous
        </button>
        <button
          className="quiz-btn primary"
          onClick={handleNext}
          disabled={selectedOption === null}
        >
          {currentQuestion === questions.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </motion.div>
  );
};

export default Quiz;