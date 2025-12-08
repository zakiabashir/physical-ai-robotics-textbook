---
id: 004
title: Fix CodeComponent runtime error
stage: red
date: 2025-12-06
surface: agent
model: glm-4.6
feature: docs-chapter-crash-fix
branch: 001-physical-ai-textbook
user: User
command: /sp.phr
labels: ["runtime-error", "debugging", "react-component"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/components/CodeComponent/index.js
tests:
  - none
---

## Prompt

Uncaught runtime errors:
×
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)

Uncaught runtime errors:
×
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)
ERROR
children.match is not a function
TypeError: children.match is not a function
    at eval (webpack-internal:///./src/components/CodeComponent/index.js:10:39)
    at commitHookEffectListMount (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:23185:26)
    at commitPassiveMountOnFiber (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24961:13)
    at commitPassiveMountEffects_complete (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24926:9)
    at commitPassiveMountEffects_begin (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24913:7)
    at commitPassiveMountEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:24901:3)
    at flushPassiveEffectsImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27074:3)
    at flushPassiveEffects (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:27019:14)
    at commitRootImpl (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26970:5)
    at commitRoot (webpack-internal:///./node_modules/react-dom/cjs/react-dom.development.js:26717:5)

## Response snapshot

Fixed the CodeComponent runtime error by updating the useEffect hook to properly handle React children. The issue was that the code was trying to call .match() on the children prop, which can be a React node or array rather than a string.

## Outcome

- ✅ Impact: Fixed runtime error that was causing multiple console errors and potentially breaking the CodeComponent functionality
- 🧪 Tests: Verified the server compiles successfully without errors after the fix
- 📁 Files: Modified src/components/CodeComponent/index.js
- 🔁 Next prompts: Consider adding proper TypeScript types for better type safety
- 🧠 Reflection: React children can be various types (string, array, ReactNode) and must be handled appropriately before string operations

## Evaluation notes (flywheel)

- Failure modes observed: The CodeComponent was not properly handling React children prop types, attempting to call string methods on non-string values
- Graders run and results (PASS/FAIL): PASS - Runtime error fixed and compilation successful
- Prompt variant (if applicable): Standard debugging prompt
- Next experiment (smallest change to try): Add TypeScript to the component to catch type errors at build time