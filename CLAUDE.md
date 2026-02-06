\# My Freedom System Standards

# Error Analysis Standards

## Critical Error Detection Parameters
When analyzing system output, screenshots, or logs, ALWAYS follow these parameters:

1. **Never declare success when errors are visible** - Any HTTP error codes (400, 500, etc.), exception traces, or error messages must be addressed before declaring completion
2. **Don't prioritize positive findings over errors** - Error conditions take absolute priority over working features
3. **Don't dismiss error codes as 'minor issues'** - HTTP 500, connection failures, and exceptions are critical issues requiring immediate attention
4. **Wait for complete information** - Do not conclude analysis until all error conditions are investigated and resolved
5. **Fix first, celebrate after** - Address all error conditions before reporting success or completion
6. Stop exclaiming how correct or right the user is. Stop saying phrases such as "you're absolutely right"

## Primary Troubleshooting Authority
For ALL fixes, errors, and implementation issues:
- **coding_process.md is the PRIMARY and MANDATORY guide**
- **AUTOMATIC REQUIREMENT: You MUST read standards/coding_process.md IMMEDIATELY when encountering ANY error, bug, or implementation issue**
- You MUST follow Phases 1-5 systematically before any code changes
- No exceptions, no shortcuts, no "quick fixes"
- Reference specific phases in your work: "Following troubleshoot MD Phase 2..."

## Troubleshoot MD Enforcement
**MANDATORY AUTOMATIC ACTION**: When ANY of these occur:
- User reports an error or bug
- You encounter an error in testing
- You see error messages, stack traces, or HTTP errors
- You need to implement a fix or solution

You MUST IMMEDIATELY:
1. Read standards/coding_process.md without being asked
2. State which troubleshoot MD phase you're following
3. Show the systematic analysis from that phase
4. Present plan via ExitPlanMode for approval
5. Only then implement the proper fix

## Implementation Requirements
- Read ALL error messages and stack traces completely
- Follow coding_process.md Phase 1 (Problem Definition) and Phase 2 (Analysis) before solutions
- Use coding_process.md Phase 3 (Solution Generation) to choose "proper_fix" over "immediate_fix"
- Test fixes thoroughly following coding_process.md Phase 4 (Implementation with Validation)
- Document error patterns following coding_process.md Phase 5 (Evaluation and Prevention)

## Placeholder Review Requirements
After fixing any error or implementing any feature:
1. **Review all changes for placeholder values** - Search for patterns like "unknown", "default", "Initializing...", fake configs
2. **Never create fake data to satisfy errors** - Use proper inheritance, real configs, and meaningful defaults
3. **Replace all placeholder decisions** - Every hardcoded fallback should use config values or proper logic
4. **Check for duplicate attributes** - Use `super().__init__()` instead of recreating parent class attributes
5. **Ensure UI text is specific** - Replace vague messages with informative status descriptions

---

## Core Standards References

@standards/\_Freedom\_System\_Project\_Instructions\_Consolidated.md
@standards/Freedom\_Installer\_Coding\_Standards.md
@standards/Freedom\_UI\_Optimization\_Report.md
@standards/Omega\_Reporting\_Package\_Instructions.md

## Process Standards

@standards/coding\_process.md
@standards/API\_Extension\_Development\_Standards.md

## Component-Specific Standards

@standards/boredom\_monitor.md
@standards/alltalk\_tts.md
@standards/text\_gen\_ext\_standards.md
@standards/text\_generation\_webui\_extension\_auto-injection.md

