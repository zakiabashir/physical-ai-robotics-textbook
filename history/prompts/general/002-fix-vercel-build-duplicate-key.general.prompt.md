---
ID: 002
TITLE: Fix Vercel Build Duplicate Key Error
STAGE: general
DATE_ISO: 2025-12-08
SURFACE: agent
MODEL: glm-4.6
FEATURE: none
BRANCH: master
USER: User
COMMAND: Fix vercel-build script error - duplicate keys in package.json
LABELS: ["vercel", "build", "package.json", "duplicate-key", "fix"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
  - package.json
  - vercel.json
  - .vercelignore
TESTS_YAML:
  - npm run vercel-build
PROMPT_TEXT: |
  10:16:53.680
  npm error Missing script: "vercel-build"
  10:16:53.681
  npm error
  10:16:53.681
  npm error To see a list of scripts, run:
  10:16:53.681
  npm error   npm run
  10:16:53.683
  npm error A complete log of this found in /vercel/.npm/_logs/2025-12-08T05_16_53_620Z-debug-0.log
  10:16:53.690
  Error: Command "npm run vercel-build" exited with 1 ye vercel p deploy k waqat error a rhy hn
RESPONSE_TEXT: |
  Fixed the vercel-build script error by:
  1. Identified duplicate "build" keys in package.json scripts section which was causing JSON parsing issues
  2. Removed the duplicate build key, keeping only one entry
  3. Simplified vercel.json configuration
  4. Created .vercelignore file to exclude unnecessary files from deployment
  5. Successfully tested the vercel-build command - it now works correctly and builds the site

  The build now successfully generates static files in frontend/build directory for Vercel deployment.
OUTCOME: success
EVALUATION: Build script now works correctly. The duplicate key issue in package.json has been resolved.
---