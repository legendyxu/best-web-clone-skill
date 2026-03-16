---
name: web-replica-bug-fixer
description: Diagnoses and repairs visual fidelity bugs in generated website clones, including image misalignment, spacing drift, overlap, overflow, layering issues, and responsive breakage. Use whenever the user says a cloned page looks wrong, differs from the source, breaks on mobile, or asks to fix replica HTML/CSS.
license: Apache-2.0
---

# Web Replica Bug Fixer

This skill repairs fidelity bugs after webpage cloning. It is for cases where the cloned output is close, but specific sections still look wrong compared with the source page.

At a high level, the process is:

- reproduce the problem with evidence
- classify the defect type
- patch the narrowest possible surface area
- validate the fix across breakpoints
- report root cause, fix, and residual risk

## Communicating With the User

Prefer concrete visual language over vague statements.

- Good: "The hero image is stretched because the wrapper lost its aspect ratio and the image is filling an auto-height container."
- Avoid: "The layout looks a bit broken."

If the user only gives a symptom, translate it into a testable defect before editing:

1. Which page or output file is broken
2. Which section is affected
3. What the expected behavior is
4. What the actual behavior is
5. Which breakpoints show the issue

## Starting The Repair

Begin by understanding:

1. Whether the defect is visible on desktop, mobile, or both
2. Whether the problem is image rendering, spacing, stacking, overflow, or responsive logic
3. Whether the issue is local to one section or caused by a broader layout rule
4. Whether a CSS-only patch is enough or the HTML structure also needs adjustment

If the request is underspecified, infer the likely defect from screenshots, generated HTML/CSS, and side-by-side comparison with the source page.

## Repair Workflow

Follow this sequence without skipping validation.

### Step 1: Reproduce And Capture Evidence

- Open the source page and cloned page side by side.
- Compare at minimum two breakpoints:
  - desktop: `1920x1080`
  - mobile: `390x844`
- Capture before-fix screenshots for the affected section.
- Note whether the problem is deterministic or only appears after scrolling, resizing, or lazy loading.

### Step 2: Classify The Defect

Use one of these primary categories:

- image positioning or sizing
- spacing and alignment
- stacking and overlap
- overflow and clipping
- responsive rule conflict
- typography or text wrapping drift

Choose the narrowest accurate label. Precise diagnosis makes minimal fixes easier.

### Step 3: Patch Minimally

- Prefer section-scoped CSS fixes first.
- Avoid global resets unless the root cause is genuinely global.
- Preserve semantic HTML structure when CSS alone can solve the issue.
- If structure changes are required, keep them as small and local as possible.

### Step 4: Validate After Every Patch

- Re-check the target section on desktop and mobile.
- Inspect neighboring sections for spacing or overlap regressions.
- Verify interactive elements remain visible and clickable.
- Confirm the fix did not distort typography, image focal area, or layout rhythm.

### Step 5: Report The Outcome

Summarize:

- the observed defect
- the root cause
- the exact files changed
- the validation result
- any remaining risk or follow-up work

## Image Misalignment Playbook

When images are wrong, check these in order:

1. Container constraints
   - Ensure the wrapper has a clear sizing strategy such as `width`, `height`, `min-height`, or `aspect-ratio`.
   - Add `overflow: hidden` when cropping is intentional.
2. Image rendering behavior
   - Use `display: block` to remove inline baseline gaps.
   - Set `width: 100%` and `height: 100%` when the image should fill the container.
   - Choose the correct `object-fit` and `object-position`.
3. Positioning context
   - If the image is absolutely positioned, ensure the parent uses `position: relative`.
   - Check for unintended transforms on ancestor elements.
4. Responsive overrides
   - Verify media queries do not overwrite width, height, or alignment unexpectedly.
   - Align breakpoint behavior with the source layout.

## Spacing And Alignment Playbook

When spacing feels wrong, inspect:

1. Margin and padding drift
   - Compare section spacing, card gutters, and text block padding with the source.
   - Check whether collapsed margins or inherited spacing rules changed the rhythm.
2. Flex and grid alignment
   - Verify `align-items`, `justify-content`, `gap`, `grid-template-columns`, and `place-items`.
   - Confirm child widths are not forcing unintended wrapping.
3. Width constraints
   - Check `max-width`, `min-width`, and fixed widths that may break centering or alignment.

## Stacking And Overflow Playbook

When elements overlap or disappear, inspect:

1. Stacking context
   - Compare `position`, `z-index`, `isolation`, `transform`, and `opacity` on the affected subtree.
2. Clipping
   - Check whether `overflow: hidden`, fixed heights, or masked containers are cutting off content.
3. Absolute positioning
   - Confirm offsets are anchored to the intended parent and still make sense at smaller breakpoints.

## Responsive Conflict Playbook

When desktop looks acceptable but mobile breaks:

1. Inspect media queries from largest to smallest breakpoint.
2. Identify which rule overrides the expected layout.
3. Prefer fixing the specific breakpoint conflict rather than rewriting the full responsive system.
4. Re-test the section after resize, not only on initial load.

## Patch Rules

- Make the smallest safe change first.
- Favor section-scoped selectors over global selectors.
- Do not rewrite whole-page CSS for a local issue.
- Keep typography, spacing scale, and component rhythm aligned with the source.
- If a fix introduces new drift, revert it and choose a narrower selector or a more accurate root-cause fix.

## Verification Checklist

- [ ] The target bug is fixed on desktop.
- [ ] The target bug is fixed on mobile.
- [ ] No new overlap or overflow appears in adjacent sections.
- [ ] Buttons, links, and calls to action remain clickable and visible.
- [ ] Images preserve the intended focal area.
- [ ] Text wrapping still looks natural after the patch.

## Report Structure

Always return repair results using this exact template:

```markdown
Issue:
- type:
- affected area:
- symptom:

Root cause:
- ...

Fixes:
- file:
- changes:

Verification:
- desktop:
- mobile:
- regression check:

Residual risk:
- ...
```

## Examples

**Example 1:**

Input: "The cloned hero banner image is stretched on mobile and the text block is lower than the source."

Expected approach:
- compare desktop and mobile
- inspect the hero wrapper sizing strategy
- verify `object-fit`, `height`, and breakpoint overrides
- patch the hero section only
- report before and after validation

**Example 2:**

Input: "Cards overlap in the cloned features section after the tablet breakpoint."

Expected approach:
- reproduce at the tablet width where the overlap begins
- inspect grid or flex rules plus width constraints
- patch the section-specific responsive rules
- verify adjacent sections and click targets

## Reference Files

Read additional guidance only when needed:

- Detailed fix recipes: [references/bugfix-playbook.md](references/bugfix-playbook.md)
