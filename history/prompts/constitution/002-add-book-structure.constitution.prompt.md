---
id: 002
title: Add Book Structure
stage: constitution
date: 2025-12-05
surface: agent
model: glm-4.6
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution","book-structure","content-organization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution validation completed
---

## Prompt

update this
Your specification must include:

1. Book Content Specification
   - 4 Chapters × 3 Lessons each (12 lessons total)
   - Chapter 1: Physical AI Foundations
   - Chapter 2: ROS 2 + Gazebo + Unity
   - Chapter 3: NVIDIA Isaac + VLA
   - Chapter 4: Humanoid Robotics Capstone

## Response snapshot

Added Book Content Structure section to constitution with:

- Fixed 4-chapter structure with exactly 3 lessons per chapter (12 lessons total)
- Specific chapter titles and lesson numbers mapped to Physical AI curriculum
- Content mandates requiring each lesson to include: learning objectives, interactive code examples, hands-on lab exercises, assessment mechanisms, real-world applications, and weekly time allocation guidance
- Updated version from 1.0.0 to 1.1.0 (minor version bump for new section)

## Outcome

- ✅ Impact: Established mandatory book structure ensuring consistency across all Physical AI textbook content
- 🧪 Tests: Constitution validation completed - all requirements clearly defined
- 📁 Files: Updated .specify/memory/constitution.md with Book Content Structure section
- 🔁 Next prompts: Plan and spec templates require updates to reflect structure compliance
- 🧠 Reflection: Successfully formalized the course structure into constitutional requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Constitution updated with clear structure requirements
- Prompt variant (if applicable): Standard constitution amendment
- Next experiment (smallest change to try): Update templates to enforce Book Content Structure compliance in planning and specification phases