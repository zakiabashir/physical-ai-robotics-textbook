---
id: 002
title: Update Lesson Requirements
stage: spec
date: 2025-12-05
surface: agent
model: glm-4.6
feature: 001-physical-ai-textbook
branch: 001-physical-ai-textbook
user: user
command: /sp.specify
labels: ["specification","lesson-requirements","content-structure","update"]
links:
  spec: specs/001-physical-ai-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-physical-ai-textbook/spec.md
  - specs/001-physical-ai-textbook/checklists/requirements.md
tests:
  - Specification validation completed with lesson structure checks
---

## Prompt

update specify

1. Book Content Specification
   - 4 Chapters × 3 Lessons each (12 lessons total)
   - Chapter 1: Physical AI Foundations
   - Chapter 2: ROS 2 + Gazebo + Unity
   - Chapter 3: NVIDIA Isaac + VLA
   - Chapter 4: Humanoid Robotics Capstone

2. Lesson Requirements
   - Each lesson must include:
     • Learning objectives
     • Deep explanations
     • Code examples (ROS2, Gazebo, Isaac, VLA)
     • Diagrams or Mermaid charts
     • Labs and hands-on activities
     • Summary and quizzes

## Response snapshot

Updated specification to include detailed lesson requirements:

- Added "Lesson Content Requirements" section with 6 core components for all lessons
- Defined content structure mandates for each of the 4 chapters
- Added visual learning requirements for diagrams and charts
- Updated Key Entities to reflect lesson components
- Added 3 new educational outcomes (EO-005, EO-006, EO-007) for lesson completeness
- Updated quality checklist with lesson structure validation

## Outcome

- ✅ Impact: Established detailed requirements for every lesson component ensuring consistency and completeness
- 🧪 Tests: Validation completed - all lesson requirements are measurable and testable
- 📁 Files: Updated spec.md and requirements checklist
- 🔁 Next prompts: Ready for /sp.plan to create implementation architecture
- 🧠 Reflection: Successfully translated high-level course structure into specific, actionable lesson requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Specification includes comprehensive lesson requirements
- Prompt variant (if applicable): Standard specification update
- Next experiment (smallest change to try): Proceed to planning with detailed lesson architecture