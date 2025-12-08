import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles.css';

const ProgressTracker = ({ chapterId, lessonId }) => {
  const [progress, setProgress] = useState(0);
  const [completedLessons, setCompletedLessons] = useState([]);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());
  const [isClient, setIsClient] = useState(false);

  const API_BASE_URL = 'http://localhost:8000/api/v1';

  useEffect(() => {
    // Set isClient to true after component mounts
    setIsClient(true);
  }, []);

  useEffect(() => {
    // Only run on client-side
    if (!isClient) return;

    // Load user progress from backend
    loadProgress();

    // Update time spent every minute
    const interval = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 60000));
    }, 60000);

    return () => clearInterval(interval);
  }, [chapterId, lessonId, startTime, isClient]);

  const loadProgress = async () => {
    try {
      // Check if we're in a browser environment and localStorage is available
      const isBrowser = typeof window !== 'undefined' && window.localStorage;
      const userId = isBrowser ? (localStorage.getItem('userId') || 'anonymous') : 'anonymous';
      const response = await axios.get(`${API_BASE_URL}/content/progress/${userId}`);
      const data = response.data;

      setProgress(data.overall_progress || 0);
      setCompletedLessons(data.completed_lessons || []);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const markLessonComplete = async () => {
    const lessonKey = `${chapterId}-${lessonId}`;

    if (completedLessons.includes(lessonKey)) {
      return; // Already marked as complete
    }

    try {
      // Check if localStorage is available
      const isBrowser = typeof window !== 'undefined' && window.localStorage;
      const userId = isBrowser ? (localStorage.getItem('userId') || 'anonymous') : 'anonymous';
      await axios.post(`${API_BASE_URL}/content/progress`, {
        user_id: userId,
        chapter_id: chapterId,
        lesson_id: lessonId,
        completed: true,
        time_spent: timeSpent
      });

      setCompletedLessons([...completedLessons, lessonKey]);

      // Recalculate progress
      const newProgress = Math.min(
        ((completedLessons.length + 1) / getTotalLessons()) * 100,
        100
      );
      setProgress(newProgress);
    } catch (error) {
      console.error('Error marking lesson complete:', error);
    }
  };

  const getTotalLessons = () => {
    // This should match the total number of lessons in your course
    return 12; // Example: 4 chapters × 3 lessons each
  };

  // Don't render anything on server-side
  if (!isClient) {
    return null;
  }

  return (
    <div className="progress-tracker">
      <div className="progress-header">
        <h3>Your Progress</h3>
        <div className="progress-stats">
          <span>Time spent: {timeSpent} min</span>
          <span>Lessons: {completedLessons.length}/{getTotalLessons()}</span>
        </div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <span className="progress-text">{Math.round(progress)}%</span>
      </div>

      <button
        className={`complete-button ${completedLessons.includes(`${chapterId}-${lessonId}`) ? 'completed' : ''}`}
        onClick={markLessonComplete}
        disabled={completedLessons.includes(`${chapterId}-${lessonId}`)}
      >
        {completedLessons.includes(`${chapterId}-${lessonId}`) ? '✓ Completed' : 'Mark as Complete'}
      </button>
    </div>
  );
};

export default ProgressTracker;