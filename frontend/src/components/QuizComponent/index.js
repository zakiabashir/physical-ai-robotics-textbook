import React, { useState } from 'react';
import './styles.css';

const QuizComponent = ({ quizData, onComplete }) => {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);

  const handleAnswerSelect = (questionId, answerIndex) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const handleSubmit = () => {
    let correctAnswers = 0;
    quizData.questions.forEach(question => {
      if (selectedAnswers[question.id] === question.correct) {
        correctAnswers++;
      }
    });
    setScore(correctAnswers);
    setShowResults(true);
    if (onComplete) {
      onComplete(correctAnswers, quizData.questions.length);
    }
  };

  const resetQuiz = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setScore(0);
  };

  return (
    <div className="quizContainer">
      <h3>{quizData.title}</h3>
      <div className="quizContent">
        {quizData.questions.map((question, qIndex) => (
          <div key={question.id} className="questionBlock">
            <h4>Question {qIndex + 1}: {question.question}</h4>
            <div className="options">
              {question.options.map((option, oIndex) => (
                <label key={oIndex} className="optionLabel">
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={oIndex}
                    checked={selectedAnswers[question.id] === oIndex}
                    onChange={() => handleAnswerSelect(question.id, oIndex)}
                    disabled={showResults}
                  />
                  <span className={showResults && oIndex === question.correct ? 'correctAnswer' : ''}>
                    {option}
                  </span>
                  {showResults && selectedAnswers[question.id] === oIndex && oIndex !== question.correct && (
                    <span className="incorrectAnswer"> (Your answer)</span>
                  )}
                </label>
              ))}
            </div>
            {showResults && selectedAnswers[question.id] !== question.correct && (
              <p className="explanation">{question.explanation}</p>
            )}
          </div>
        ))}
      </div>

      <div className="quizActions">
        {!showResults ? (
          <button
            onClick={handleSubmit}
            className="submitButton"
            disabled={Object.keys(selectedAnswers).length !== quizData.questions.length}
          >
            Submit Quiz
          </button>
        ) : (
          <div>
            <p className="scoreText">
              Your Score: {score} out of {quizData.questions.length} ({Math.round(score/quizData.questions.length * 100)}%)
            </p>
            <button onClick={resetQuiz} className="resetButton">
              Retake Quiz
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizComponent;