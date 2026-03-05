# Prompting Playbook (Web Replica Forge)

This playbook focuses on prompt-level quality control for the `replica-forge` stage.

## Prompt Surfaces

- System prompt: `assets/prompts/clone.system_prompt.txt`
- Clone prompt template: `assets/prompts/clone.pass1.prompt_template.txt`

## Editing Strategy

1. Keep output contract strict:
   - single HTML file
   - no markdown wrappers in final answer
2. Push visual fidelity requirements:
   - section-by-section coverage
   - spacing, stroke, and typography preservation
   - mobile compatibility
3. Avoid contradictory instructions:
   - if a line conflicts with output format, remove ambiguity
4. Change one cluster of prompt rules at a time, then re-run.

## Practical Iteration Loop

1. Clone a single URL with this skill.
2. Compare:
   - hero section geometry
   - typography hierarchy
   - card/grid rhythm
   - CTA prominence
   - responsive behavior
3. If fidelity issues persist:
   - strengthen specificity in prompt template first
   - increase `--max-output-tokens` if output is truncated
   - keep `--include-video` enabled for dynamic sites
4. Re-run the same URL after each prompt change.

## Failure Signatures and Fixes

- Missing sections:
  - enforce "copy every section" wording in template
- Flat typography:
  - add explicit hierarchy constraints (weights, contrast, spacing)
- Mobile breakage:
  - add explicit small-screen behavior requirements
- Incomplete HTML:
  - raise max output tokens and keep truncation-repair enabled in config
