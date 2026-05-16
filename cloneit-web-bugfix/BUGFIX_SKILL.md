---
name: bugfix-skill
description: Diagnoses and repairs visual fidelity bugs in generated website clones, including image misalignment, spacing drift, overlap, overflow, layering issues, and responsive breakage. Use whenever the user says a cloned page looks wrong, differs from the source, breaks on mobile, or asks to fix replica HTML/CSS. Make sure to use this skill whenever the user reports that a cloned website has visual issues — for example "the images are stretched", "the layout is broken on mobile", "cards are overlapping", "the spacing looks off", or "it doesn't look like the original page."
license: Apache-2.0
---

# Bugfix Skill — Web Replica Bug Fixer

This skill repairs fidelity bugs after webpage cloning. It is for cases where the cloned output is close to the source but specific sections still look wrong.

At a high level, the process is:

- reproduce the problem with evidence at multiple breakpoints
- classify the defect type (image, spacing, stacking, overflow, responsive, or typography)
- patch the narrowest possible CSS surface area
- validate the fix across both desktop and mobile
- report root cause, applied changes, and verification outcome

## Communicating With the User

Prefer concrete visual language over vague statements.

- Good: "The hero image is stretched because the wrapper lost its aspect ratio and the image is filling an auto-height container."
- Avoid: "The layout looks a bit broken."

If the user only gives a symptom, help them clarify by identifying:

1. which page or output file is broken
2. which section is affected
3. what the expected behavior is
4. what the actual behavior is
5. which breakpoints show the issue

If the user's description is underspecified, start by opening the source page and cloned page side by side at two breakpoints (desktop `1920x1080` and mobile `390x844`), then infer the defect from what you see.

## Defect Classification

Every visual bug should be assigned to exactly one primary category. Choosing the narrowest accurate label is important because it guides the fix strategy.

| Category | Symptoms | Typical Root Cause |
|----------|----------|-------------------|
| Image positioning or sizing | Stretched, cropped, misaligned, or shifted images | Missing `object-fit`, wrong container dimensions, or baseline gaps |
| Spacing and alignment | Broken rhythm, uneven gutters, text too close or too far | Margin/padding drift, flex/grid alignment mismatch |
| Stacking and overlap | Elements overlapping or hidden | Wrong `z-index`, missing `position: relative`, or clipping |
| Overflow and clipping | Content cut off, scrollbars appearing unexpectedly | Fixed heights, `overflow: hidden` on wrong element |
| Responsive rule conflict | Desktop OK but mobile broken | Media query override clashes, wrong breakpoint values |
| Typography or text wrapping drift | Text wraps oddly, sizes mismatch, line-height inconsistent | Font-size, line-height, or `word-break` inheritance mismatch |

## Repair Workflow

### Step 1: Reproduce And Capture Evidence

- Open the source page and cloned page side by side.
- Compare at minimum two breakpoints:
  - desktop: `1920x1080`
  - mobile: `390x844`
- Capture before-fix screenshots for the affected section.
- Note whether the problem is deterministic or only appears after scrolling, resizing, or lazy loading.

### Step 2: Classify The Defect

Use the table in the Defect Classification section above. Pick one primary category.

### Step 3: Patch Minimally

- **First try**: section-scoped CSS fixes. Target the affected section with a narrow selector.
- **Avoid**: global resets unless the root cause is genuinely global (e.g., a box-sizing issue affecting every element).
- **Preserve**: semantic HTML structure when CSS alone can resolve the issue. Only change structure if the CSS approach is genuinely impossible.
- **If a fix introduces new drift**: revert it and use a narrower selector or a more accurate root-cause approach.

### Step 4: Validate After Every Patch

- Re-check the target section on desktop and mobile.
- Inspect neighboring sections for spacing or overlap regressions.
- Verify interactive elements (buttons, links, CTAs) remain visible and clickable.
- Confirm the fix did not distort typography, image focal area, or layout rhythm.
- Re-test after window resize, not just on initial load.

### Step 5: Report The Outcome

Summarize:

- the observed defect
- the root cause
- the exact files changed
- the validation result
- any remaining risk or follow-up work

## Image Misalignment Playbook

When images are wrong, check these in order:

1. **Container constraints**
   - Ensure the wrapper has a clear sizing strategy (`width`, `height`, `min-height`, or `aspect-ratio`).
   - Add `overflow: hidden` when cropping is intentional.
2. **Image rendering behavior**
   - Use `display: block` to remove inline baseline gaps.
   - Set `width: 100%` and `height: 100%` when the image should fill the container.
   - Choose the correct `object-fit` and `object-position`.
3. **Positioning context**
   - If the image is absolutely positioned, ensure the parent uses `position: relative`.
   - Check for unintended transforms on ancestor elements.
4. **Responsive overrides**
   - Verify media queries do not overwrite width, height, or alignment unexpectedly.
   - Align breakpoint behavior with the source layout.

## Spacing And Alignment Playbook

When spacing feels wrong, inspect:

1. **Margin and padding drift** — Compare section spacing, card gutters, and text block padding with the source. Check for collapsed margins or inherited spacing.
2. **Flex and grid alignment** — Verify `align-items`, `justify-content`, `gap`, `grid-template-columns`, and `place-items`. Confirm child widths are not forcing unintended wrapping.
3. **Width constraints** — Check `max-width`, `min-width`, and fixed widths that may break centering or alignment.

## Stacking And Overflow Playbook

When elements overlap or disappear, inspect:

1. **Stacking context** — Compare `position`, `z-index`, `isolation`, `transform`, and `opacity` on the affected subtree.
2. **Clipping** — Check whether `overflow: hidden`, fixed heights, or masked containers are cutting off content.
3. **Absolute positioning** — Confirm offsets are anchored to the intended parent and still make sense at smaller breakpoints.

## Responsive Conflict Playbook

When desktop looks acceptable but mobile breaks:

1. Inspect media queries from largest to smallest breakpoint.
2. Identify which rule overrides the expected layout.
3. Prefer fixing the specific breakpoint conflict rather than rewriting the full responsive system.
4. Re-test the section after resize, not only on initial load.

## Report Structure

Always return repair results using this template:

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

## Verification Checklist

- [ ] The target bug is fixed on desktop.
- [ ] The target bug is fixed on mobile.
- [ ] No new overlap or overflow appears in adjacent sections.
- [ ] Buttons, links, and calls to action remain clickable and visible.
- [ ] Images preserve the intended focal area.
- [ ] Text wrapping still looks natural after the patch.

## Examples

**Example 1: Stretched hero banner**

Input: "The cloned hero banner image is stretched on mobile and the text block is lower than the source."

Expected approach:

- compare desktop and mobile
- inspect the hero wrapper sizing strategy
- verify `object-fit`, `height`, and breakpoint overrides
- patch the hero section only
- report before and after validation

**Example 2: Overlapping cards**

Input: "Cards overlap in the cloned features section after the tablet breakpoint."

Expected approach:

- reproduce at the tablet width where the overlap begins
- inspect grid or flex rules plus width constraints
- patch the section-specific responsive rules
- verify adjacent sections and click targets

## Reference Files

For more detailed CSS fix recipes, read [references/bugfix-playbook.md](references/bugfix-playbook.md). Read it only when you need deeper guidance beyond the playbooks above.
