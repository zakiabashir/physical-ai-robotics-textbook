---
id: 001
title: Create Constitution
stage: constitution
date: 2025-12-05
surface: agent
model: glm-4.6
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution","setup","physical-ai","robotics","textbook"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  -
---

## Prompt

You are an AI Textbook Engineer with 20 years of technical writing and prompt-engineering experience. Your mission is to create a complete, production-ready technical textbook titled **"Physical AI & Humanoid Robotics"** using **Spec-Kit Plus**, **Claude Code**, and **Docusaurus**.

Project Identity:
- This book is part of Panaversity's AI-native textbook series.
- It aligns with the hackathon requirements for:
  (1) AI/Spec-driven book generation
  (2) Integrated RAG chatbot
  (3) Optional personalization, translation, and reusable intelligence
- The textbook must teach the full **Physical AI & Humanoid Robotics Course**, including ROS 2, Humanoid Robots, Gazebo, Unity, NVIDIA Isaac, and Vision-Language-Action systems.

Rules:
- Produce all content using Docusaurus markdown.
- Organize chapters into 14–16 full modules based on the course outline.
- Include labs, weekly breakdowns, hardware requirements, capstone, diagrams, and code blocks.
- Maintain an expert academic + industry tone suita

## Response snapshot

Created a comprehensive constitution for the Physical AI & Humanoid Robotics textbook project with seven core principles:
1. Content-First Architecture
2. Interactive-First Design
3. Test-Driven Learning (NON-NEGOTIABLE)
4. Integration Validation
5. Observability & Analytics
6. Version-Controlled Curriculum
7. Accessibility First

The constitution includes Educational Standards, Development Workflow, and Governance sections tailored for creating an AI-native technical textbook with hands-on robotics content.

## Outcome

- ✅ Impact: Established foundational governance for the Physical AI textbook project, defining educational quality standards and development practices
- 🧪 Tests: Constitution validation completed - all placeholders filled with concrete values aligned to educational technology requirements
- 📁 Files: Created .specify/memory/constitution.md (version 1.0.0)
- 🔁 Next prompts: Plan template updates, spec template updates, tasks template updates
- 🧠 Reflection: Successfully transformed generic SpecKit template into educational technology-specific constitution for Physical AI & Humanoid Robotics textbook

## Evaluation notes (flywheel)

- Failure modes observed: None - template conversion completed successfully
- Graders run and results (PASS/FAIL): PASS - All placeholder tokens replaced with concrete values
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Update templates to align with new constitution principles