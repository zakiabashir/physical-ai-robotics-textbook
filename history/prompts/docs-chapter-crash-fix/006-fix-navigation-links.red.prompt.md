---
id: 006
title: Fix navigation links for available chapters
stage: red
date: 2025-12-06
surface: agent
model: glm-4.6
feature: docs-chapter-crash-fix
branch: 001-physical-ai-textbook
user: User
command: @src\pages\index.js and @sidebars.js in files ma links open nhi ho rhy
labels: ["navigation", "links", "missing-content", "404-errors"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/pages/index.js
  - sidebars.js
tests:
  - Verified website runs without errors
  - Verified navigation links work for available chapters
  - Verified server compiles successfully
---

## Prompt

@src\pages\index.js and @sidebars.js in files ma links open nhi ho rhy

## Response

Fixed navigation links by updating both index.js and sidebars.js to only include available chapters (1 and 4). Chapters 2 and 3 were missing from the docs directory, causing 404 errors when users clicked on those links.

## Changes Made

1. **Updated src/pages/index.js:**
   - Removed chapters 2 and 3 from the chapters array
   - Changed "Start Learning" and "Get Started Now" buttons to link to `/docs/introduction` instead of `/docs/chapter-1/lesson-1`
   - Only showing Chapter 1: Physical AI Foundations and Chapter 4: Humanoid Robotics Capstone

2. **Updated sidebars.js:**
   - Removed Chapter 2 and Chapter 3 categories from the sidebar configuration
   - Kept only available chapters in the navigation structure

## Outcome

- ✅ Impact: Fixed all navigation links - no more 404 errors
- 🧪 Tests: All links now work correctly
- 📁 Files: Modified src/pages/index.js and sidebars.js
- 🔁 Next prompts: Create content for missing chapters if needed

## Evaluation notes

- The issue was caused by chapter directories 2 and 3 not existing in the docs folder
- By removing references to non-existent content, all navigation now works properly
- Users can successfully navigate to Introduction, Chapter 1, and Chapter 4