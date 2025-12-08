import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Survey.css';

const OnboardingSurvey = ({ onComplete, initialData = {} }) => {
  const [step, setStep] = useState(0);
  const [surveyData, setSurveyData] = useState({
    // Background Information
    experience: initialData.experience || [],
    education: initialData.education || '',
    goals: initialData.goals || [],

    // Hardware Setup
    hasRobot: initialData.hasRobot || false,
    robotType: initialData.robotType || '',
    hasGPU: initialData.hasGPU || false,
    platform: initialData.platform || '',

    // Learning Preferences
    learningStyle: initialData.learningStyle || '',
    backgroundLevel: initialData.backgroundLevel || '',
    interests: initialData.interests || [],

    // Notification Preferences
    emailNotifications: initialData.emailNotifications !== false,
    browserNotifications: initialData.browserNotifications || false
  });

  const questions = [
    {
      id: 'experience',
      title: 'Programming Experience',
      subtitle: 'Select all that apply',
      type: 'checkbox',
      options: [
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'cpp', label: 'C++' },
        { value: 'robotics', label: 'Robotics' },
        { value: 'machine-learning', label: 'Machine Learning' },
        { value: 'none', label: 'No programming experience' }
      ]
    },
    {
      id: 'education',
      title: 'Education Level',
      subtitle: 'What is your highest level of education?',
      type: 'radio',
      options: [
        { value: 'high-school', label: 'High School' },
        { value: 'bachelor', label: 'Bachelor\'s Degree' },
        { value: 'master', label: 'Master\'s Degree' },
        { value: 'phd', label: 'PhD' },
        { value: 'other', label: 'Other' }
      ]
    },
    {
      id: 'goals',
      title: 'Learning Goals',
      subtitle: 'What do you hope to achieve? (Select all that apply)',
      type: 'checkbox',
      options: [
        { value: 'research', label: 'Academic Research' },
        { value: 'industry', label: 'Industry Application' },
        { value: 'hobby', label: 'Personal Interest/Hobby' },
        { value: 'career-change', label: 'Career Change' },
        { value: 'teaching', label: 'Teaching' }
      ]
    },
    {
      id: 'learningStyle',
      title: 'Learning Style',
      subtitle: 'How do you prefer to learn?',
      type: 'radio',
      options: [
        { value: 'visual', label: 'Visual - Diagrams and videos help me understand' },
        { value: 'kinesthetic', label: 'Hands-on - I learn by doing' },
        { value: 'textual', label: 'Reading - Text explanations work best' },
        { value: 'mixed', label: 'Mixed - I like variety' }
      ]
    },
    {
      id: 'backgroundLevel',
      title: 'Technical Background',
      subtitle: 'How would you rate your technical background?',
      type: 'radio',
      options: [
        { value: 'beginner', label: 'Beginner - Just starting out' },
        { value: 'intermediate', label: 'Intermediate - Some experience' },
        { value: 'advanced', label: 'Advanced - Experienced developer/engineer' }
      ]
    },
    {
      id: 'platform',
      title: 'Development Platform',
      subtitle: 'What operating system are you using?',
      type: 'radio',
      options: [
        { value: 'windows', label: 'Windows' },
        { value: 'linux', label: 'Linux' },
        { value: 'macos', label: 'macOS' }
      ]
    }
  ];

  const handleNext = () => {
    // Skip hardware questions if not relevant
    if (step === 2) { // After goals
      if (surveyData.goals.includes('hobby') && !surveyData.hasRobot) {
        setStep(step + 3); // Skip robot questions
      } else {
        setStep(step + 1);
      }
    } else {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step === 4) { // Before platform
      setStep(step - 2); // Skip robot questions
    } else {
      setStep(step - 1);
    }
  };

  const handleChange = (value) => {
    const currentQuestion = questions[step];

    if (currentQuestion.type === 'checkbox') {
      if (currentQuestion.id === 'experience') {
        // Handle "none" option mutually exclusive with others
        if (value === 'none') {
          setSurveyData({
            ...surveyData,
            [currentQuestion.id]: ['none']
          });
        } else {
          const newExperience = surveyData[currentQuestion.id].filter(e => e !== 'none');
          if (!newExperience.includes(value)) {
            newExperience.push(value);
          }
          setSurveyData({
            ...surveyData,
            [currentQuestion.id]: newExperience
          });
        }
      } else {
        const currentValues = surveyData[currentQuestion.id] || [];
        if (!currentValues.includes(value)) {
          setSurveyData({
            ...surveyData,
            [currentQuestion.id]: [...currentValues, value]
          });
        }
      }
    } else {
      setSurveyData({
        ...surveyData,
        [currentQuestion.id]: value
      });
    }
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        // Save locally for unauthenticated users
        localStorage.setItem('user_survey_data', JSON.stringify(surveyData));
        onComplete(surveyData);
        return;
      }

      // Send to backend for authenticated users
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/auth/survey`,
        surveyData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      onComplete(surveyData);
    } catch (error) {
      console.error('Error submitting survey:', error);
      // Still complete the survey even if API call fails
      onComplete(surveyData);
    }
  };

  const progress = Math.round(((step + 1) / questions.length) * 100);

  return (
    <div className="survey-container">
      <div className="survey-header">
        <h2>Welcome to Physical AI & Humanoid Robotics</h2>
        <p>Help us personalize your learning experience</p>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <div className="question-card">
        <h3>{questions[step].title}</h3>
        {questions[step].subtitle && (
          <p className="question-subtitle">{questions[step].subtitle}</p>
        )}

        <div className="options">
          {questions[step].options.map((option) => (
            <label key={option.value} className="option-label">
              {questions[step].type === 'checkbox' ? (
                <input
                  type="checkbox"
                  checked={surveyData[questions[step].id]?.includes(option.value) || false}
                  onChange={() => handleChange(option.value)}
                />
              ) : (
                <input
                  type="radio"
                  name={questions[step].id}
                  checked={surveyData[questions[step].id] === option.value}
                  onChange={() => handleChange(option.value)}
                />
              )}
              <span className="option-text">{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="survey-actions">
        {step > 0 && (
          <button className="btn-secondary" onClick={handleBack}>
            Back
          </button>
        )}
        {step < questions.length - 1 ? (
          <button className="btn-primary" onClick={handleNext}>
            Next
          </button>
        ) : (
          <button className="btn-primary" onClick={handleSubmit}>
            Complete Setup
          </button>
        )}
      </div>
    </div>
  );
};

export default OnboardingSurvey;