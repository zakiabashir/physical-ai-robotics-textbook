---
ID: {{ID}}
TITLE: {{TITLE}}
STAGE: {{STAGE}}
DATE_ISO: {{DATE_ISO}}
SURFACE: "agent"
MODEL: "{{MODEL}}"
FEATURE: "{{FEATURE}}"
BRANCH: "{{BRANCH}}"
USER: "{{USER}}"
COMMAND: "{{COMMAND}}"
LABELS: {{LABELS}}
LINKS:
  SPEC: {{SPEC_LINK}}
  TICKET: {{TICKET_LINK}}
  ADR: {{ADR_LINK}}
  PR: {{PR_LINK}}
FILES_YAML:
{{FILES_YAML}}
TESTS_YAML:
{{TESTS_YAML}}
OUTCOME:
  STATUS: "{{STATUS}}"
  EVALUATION: "{{EVALUATION}}"
---

# {{TITLE}} - Prompt History Record

## Prompt Text

```text
{{PROMPT_TEXT}}
```

## Response Summary

{{RESPONSE_TEXT}}

## Execution Details

### Context
- **Command**: {{COMMAND}}
- **Working Directory**: {{WORKING_DIR}}
- **Timestamp**: {{TIMESTAMP}}

### Key Actions Taken
{{KEY_ACTIONS}}

### Files Created/Modified
{{FILES_LIST}}

### Tests Performed
{{TESTS_LIST}}

### Challenges Encountered
{{CHALLENGES}}

### Lessons Learned
{{LESSONS}}

## Outcome Evaluation

### Success Metrics
{{SUCCESS_METRICS}}

### Areas for Improvement
{{IMPROVEMENTS}}

### Follow-up Actions
{{FOLLOW_UP}}

---

*Generated: {{GENERATED_DATE}}*
*Agent: {{AGENT_VERSION}}*