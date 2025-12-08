/**
 * Progress tracking utility for the Physical AI Textbook
 * Tracks user progress through lessons, chapters, and quizzes
 */

class ProgressTracker {
  constructor() {
    this.storageKey = 'physical_ai_textbook_progress';
    this.loadProgress();
  }

  /**
   * Load progress from localStorage
   */
  loadProgress() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      this.progress = saved ? JSON.parse(saved) : {
        chapters: {},
        lessons: {},
        quizzes: {},
        codeExercises: {},
        overallProgress: 0,
        lastAccessed: null,
        timeSpent: {},
        bookmarks: [],
        notes: {}
      };
    } catch (error) {
      console.error('Error loading progress:', error);
      this.resetProgress();
    }
  }

  /**
   * Save progress to localStorage
   */
  saveProgress() {
    try {
      this.progress.lastAccessed = new Date().toISOString();
      localStorage.setItem(this.storageKey, JSON.stringify(this.progress));
    } catch (error) {
      console.error('Error saving progress:', error);
    }
  }

  /**
   * Reset all progress
   */
  resetProgress() {
    this.progress = {
      chapters: {},
      lessons: {},
      quizzes: {},
      codeExercises: {},
      overallProgress: 0,
      lastAccessed: null,
      timeSpent: {},
      bookmarks: [],
      notes: {}
    };
    this.saveProgress();
  }

  /**
   * Mark a lesson as started
   */
  startLesson(chapterId, lessonId) {
    if (!this.progress.lessons[lessonId]) {
      this.progress.lessons[lessonId] = {
        chapterId,
        status: 'in_progress',
        startTime: new Date().toISOString(),
        timeSpent: 0,
        lastAccessed: new Date().toISOString()
      };
    } else {
      this.progress.lessons[lessonId].status = 'in_progress';
      this.progress.lessons[lessonId].lastAccessed = new Date().toISOString();
    }
    this.saveProgress();
  }

  /**
   * Mark a lesson as completed
   */
  completeLesson(lessonId, timeSpent = 0) {
    if (this.progress.lessons[lessonId]) {
      this.progress.lessons[lessonId].status = 'completed';
      this.progress.lessons[lessonId].completedAt = new Date().toISOString();
      this.progress.lessons[lessonId].timeSpent += timeSpent;
    }
    this.updateOverallProgress();
    this.saveProgress();
  }

  /**
   * Update lesson progress (for partial completion)
   */
  updateLessonProgress(lessonId, progressPercent, timeSpent = 0) {
    if (!this.progress.lessons[lessonId]) {
      this.progress.lessons[lessonId] = {
        progressPercent: 0,
        timeSpent: 0,
        status: 'in_progress'
      };
    }

    this.progress.lessons[lessonId].progressPercent = progressPercent;
    this.progress.lessons[lessonId].timeSpent += timeSpent;
    this.progress.lessons[lessonId].lastAccessed = new Date().toISOString();

    if (progressPercent >= 100) {
      this.progress.lessons[lessonId].status = 'completed';
      this.progress.lessons[lessonId].completedAt = new Date().toISOString();
    }

    this.updateOverallProgress();
    this.saveProgress();
  }

  /**
   * Record quiz results
   */
  recordQuiz(lessonId, quizId, score, answers, timeSpent) {
    if (!this.progress.quizzes[lessonId]) {
      this.progress.quizzes[lessonId] = [];
    }

    this.progress.quizzes[lessonId].push({
      quizId,
      score,
      maxScore: 100,
      answers,
      timeSpent,
      timestamp: new Date().toISOString(),
      passed: score >= 70
    });

    this.saveProgress();
  }

  /**
   * Track code exercise completion
   */
  completeCodeExercise(lessonId, exerciseId, code, output, success = true) {
    if (!this.progress.codeExercises[lessonId]) {
      this.progress.codeExercises[lessonId] = {};
    }

    this.progress.codeExercises[lessonId][exerciseId] = {
      completed: true,
      success,
      code,
      output,
      completedAt: new Date().toISOString()
    };

    this.saveProgress();
  }

  /**
   * Add or update a bookmark
   */
  addBookmark(chapterId, lessonId, sectionId, title, content) {
    const bookmark = {
      id: Date.now().toString(),
      chapterId,
      lessonId,
      sectionId,
      title,
      content: content.substring(0, 200) + '...',
      createdAt: new Date().toISOString()
    };

    // Remove existing bookmark for same section if exists
    this.progress.bookmarks = this.progress.bookmarks.filter(
      b => !(b.chapterId === chapterId && b.lessonId === lessonId && b.sectionId === sectionId)
    );

    this.progress.bookmarks.push(bookmark);
    this.saveProgress();

    return bookmark.id;
  }

  /**
   * Remove a bookmark
   */
  removeBookmark(bookmarkId) {
    this.progress.bookmarks = this.progress.bookmarks.filter(b => b.id !== bookmarkId);
    this.saveProgress();
  }

  /**
   * Add or update a note
   */
  saveNote(chapterId, lessonId, sectionId, note) {
    const noteId = `${chapterId}-${lessonId}-${sectionId}`;

    this.progress.notes[noteId] = {
      id: noteId,
      chapterId,
      lessonId,
      sectionId,
      note,
      updatedAt: new Date().toISOString()
    };

    this.saveProgress();

    return noteId;
  }

  /**
   * Delete a note
   */
  deleteNote(noteId) {
    delete this.progress.notes[noteId];
    this.saveProgress();
  }

  /**
   * Get user's current streak
   */
  getStreak() {
    const today = new Date();
    const lastAccess = this.progress.lastAccessed ? new Date(this.progress.lastAccessed) : null;

    if (!lastAccess) return 0;

    const daysDiff = Math.floor((today - lastAccess) / (1000 * 60 * 60 * 24));

    if (daysDiff === 0) {
      // Check if there was activity yesterday
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const lastStreakDate = localStorage.getItem('last_streak_date');

      if (lastStreakDate) {
        const streakDate = new Date(lastStreakDate);
        if (streakDate.toDateString() === yesterday.toDateString()) {
          return parseInt(localStorage.getItem('current_streak') || '1');
        }
      }
      return 1;
    }

    if (daysDiff === 1) {
      return parseInt(localStorage.getItem('current_streak') || '1');
    }

    // Reset streak if more than 1 day
    localStorage.setItem('current_streak', '0');
    return 0;
  }

  /**
   * Update streak
   */
  updateStreak() {
    const currentStreak = this.getStreak();
    const today = new Date().toDateString();
    const lastStreakDate = localStorage.getItem('last_streak_date');

    if (lastStreakDate !== today) {
      const newStreak = lastStreakDate === new Date(Date.now() - 86400000).toDateString()
        ? currentStreak + 1
        : 1;

      localStorage.setItem('current_streak', newStreak.toString());
      localStorage.setItem('last_streak_date', today);
    }
  }

  /**
   * Calculate overall progress percentage
   */
  updateOverallProgress() {
    // Define total lessons and chapters
    const totalLessons = 13; // Based on our content structure
    const totalChapters = 4;

    // Count completed lessons
    const completedLessons = Object.values(this.progress.lessons)
      .filter(lesson => lesson.status === 'completed').length;

    // Count completed chapters (all lessons in chapter completed)
    const chapterProgress = {};
    Object.values(this.progress.lessons).forEach(lesson => {
      if (lesson.chapterId && lesson.status === 'completed') {
        chapterProgress[lesson.chapterId] = (chapterProgress[lesson.chapterId] || 0) + 1;
      }
    });

    const completedChapters = Object.values(chapterProgress)
      .filter(count => count >= 3).length; // Assuming 3 lessons per chapter

    // Calculate weighted progress
    const lessonWeight = 0.7; // 70% from lessons
    const chapterWeight = 0.3; // 30% from chapters

    const lessonProgressPercent = (completedLessons / totalLessons) * 100 * lessonWeight;
    const chapterProgressPercent = (completedChapters / totalChapters) * 100 * chapterWeight;

    this.progress.overallProgress = Math.round(lessonProgressPercent + chapterProgressPercent);

    // Update achievement badges
    this.checkAchievements();
  }

  /**
   * Check and award achievement badges
   */
  checkAchievements() {
    const achievements = [];

    // First lesson completed
    if (Object.values(this.progress.lessons).filter(l => l.status === 'completed').length === 1) {
      achievements.push({ id: 'first_steps', name: 'First Steps', description: 'Complete your first lesson' });
    }

    // Chapter completed
    const completedLessons = Object.values(this.progress.lessons).filter(l => l.status === 'completed').length;
    if (completedLessons === 3) {
      achievements.push({ id: 'chapter_master', name: 'Chapter Master', description: 'Complete a full chapter' });
    }

    // Perfect quiz score
    Object.values(this.progress.quizzes).forEach(quizzes => {
      quizzes.forEach(quiz => {
        if (quiz.score === 100) {
          achievements.push({ id: 'perfect_score', name: 'Perfect Score', description: 'Get 100% on a quiz' });
        }
      });
    });

    // Streak achievements
    const streak = this.getStreak();
    if (streak >= 7) {
      achievements.push({ id: 'week_warrior', name: 'Week Warrior', description: '7-day streak' });
    }
    if (streak >= 30) {
      achievements.push({ id: 'monthly_master', name: 'Monthly Master', description: '30-day streak' });
    }

    // Store achievements
    if (!this.progress.achievements) {
      this.progress.achievements = [];
    }

    achievements.forEach(achievement => {
      if (!this.progress.achievements.find(a => a.id === achievement.id)) {
        this.progress.achievements.push({
          ...achievement,
          earnedAt: new Date().toISOString()
        });
      }
    });
  }

  /**
   * Get progress summary
   */
  getProgressSummary() {
    const totalLessons = 13;
    const completedLessons = Object.values(this.progress.lessons)
      .filter(lesson => lesson.status === 'completed').length;

    const quizzesTaken = Object.values(this.progress.quizzes).flat().length;
    const averageQuizScore = quizzesTaken > 0
      ? Math.round(Object.values(this.progress.quizzes).flat().reduce((sum, q) => sum + q.score, 0) / quizzesTaken)
      : 0;

    const totalTimeSpent = Object.values(this.progress.lessons)
      .reduce((sum, lesson) => sum + (lesson.timeSpent || 0), 0);

    return {
      overallProgress: this.progress.overallProgress,
      completedLessons,
      totalLessons,
      lessonsInProgress: Object.values(this.progress.lessons).filter(l => l.status === 'in_progress').length,
      quizzesTaken,
      averageQuizScore,
      totalTimeSpent,
      streak: this.getStreak(),
      bookmarksCount: this.progress.bookmarks.length,
      notesCount: Object.keys(this.progress.notes).length,
      achievements: this.progress.achievements || []
    };
  }

  /**
   * Export progress for backup
   */
  exportProgress() {
    return {
      ...this.progress,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
  }

  /**
   * Import progress from backup
   */
  importProgress(data) {
    try {
      this.progress = { ...data };
      delete this.progress.exportedAt;
      delete this.progress.version;
      this.saveProgress();
      return true;
    } catch (error) {
      console.error('Error importing progress:', error);
      return false;
    }
  }
}

// Create and export singleton instance
export default new ProgressTracker();