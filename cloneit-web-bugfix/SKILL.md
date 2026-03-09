---
name: web-replica-bug-fixer
description: Diagnoses and repairs visual bugs in cloned websites, including image misalignment, spacing drift, overlap, overflow, and responsive breakage. Use when users report clone fidelity problems or ask to fix generated replica HTML/CSS.
license: Apache-2.0
---

# Web Replica Bug Fixer

Repair fidelity bugs after webpage cloning, with emphasis on visual consistency and responsive behavior.

## When To Use

Use this skill when:
- cloned page "looks off" compared with source
- images are misaligned, stretched, cropped incorrectly, or shifted
- blocks overlap, spacing rhythm is broken, or text wraps unexpectedly
- desktop looks acceptable but mobile/tablet is broken

Typical trigger words:
- `图片错位`, `布局错乱`, `响应式崩了`, `克隆不一致`, `还原度低`, `重叠`, `溢出`

## Core Workflow

Follow this loop in order:

1. Reproduce and capture evidence
   - open source page and cloned page side by side
   - compare at least two breakpoints: desktop (`1920x1080`) and mobile (`390x844`)
   - capture before-fix screenshots for the affected section
2. Classify the defect
   - image positioning / sizing
   - spacing and alignment
   - stacking and overlap (`z-index`, `position`)
   - responsive rule conflict
3. Patch minimally
   - prefer scoped CSS fixes for the target section first
   - avoid global resets unless root cause is truly global
   - keep semantic HTML structure stable; adjust structure only if CSS alone cannot resolve
4. Validate quickly after each patch
   - desktop + mobile visual check
   - verify no regression in neighboring sections
5. Report
   - summarize root cause, applied changes, and verification outcome

## Image Misalignment Playbook (Priority)

When images are wrong, apply checks in this order:

1. Container constraints
   - ensure image wrapper has explicit dimensions strategy (`width`, `height`, or `aspect-ratio`)
   - add `overflow: hidden` when cropping is intended
2. Image rendering behavior
   - use `display: block` to remove baseline gaps
   - set `width: 100%` and `height: 100%` when filling container
   - choose correct `object-fit` (`cover` or `contain`) and `object-position`
3. Positioning context
   - if image uses absolute positioning, ensure parent has `position: relative`
   - check for unintended transforms on ancestor elements
4. Responsive rules
   - verify media queries do not overwrite width/height unexpectedly
   - align breakpoint values with source layout behavior

## Patch Rules

- Make the smallest safe change first.
- Favor section-scoped selectors over global selectors.
- Do not rewrite whole page CSS for a local issue.
- Keep typography, spacing scale, and component rhythm consistent with source.
- If a fix introduces new drift, revert that patch and use a narrower selector.

## Verification Checklist

- [ ] Target bug is visually fixed on desktop.
- [ ] Target bug is visually fixed on mobile.
- [ ] No new overlap/overflow in adjacent sections.
- [ ] CTA/buttons remain clickable and visible.
- [ ] Images preserve intended focal area.

## Output Format

Return repair results using this structure:

```markdown
Issue:
- type:
- affected area:
- symptom:

Root cause:
- ...

Fixes:
- file:
  changes:

Verification:
- desktop:
- mobile:
- regression check:

Residual risk:
- ...
```

## Additional Resources

- Detailed fix recipes: [references/bugfix-playbook.md](references/bugfix-playbook.md)
