# Bugfix Playbook

Concrete recipes for common web-replica fidelity issues.

## 1) Image Stretching or Compression

Symptom:
- image appears squeezed or stretched

Likely cause:
- container and image dimensions are not coordinated

Fix pattern:

```css
.section-media {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.section-media > img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
```

## 2) Image Position Shift (Absolute/Floating)

Symptom:
- image drifts away from expected anchor position

Likely cause:
- absolutely positioned image without stable containing block

Fix pattern:

```css
.hero-media {
  position: relative;
}

.hero-media > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

## 3) Inline Image Baseline Gap

Symptom:
- extra gap appears under images

Likely cause:
- inline image baseline behavior

Fix pattern:

```css
img {
  display: block;
}
```

If global change is risky, scope it:

```css
.card img,
.hero img {
  display: block;
}
```

## 4) Grid/Flex Misalignment

Symptom:
- cards are not aligned in rows/columns

Likely cause:
- mixed width rules, missing `align-items`, or inconsistent gap values

Fix pattern:

```css
.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  align-items: stretch;
}
```

Or for flex:

```css
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.cards > .card {
  flex: 1 1 calc(33.333% - 16px);
}
```

## 5) Mobile Breakpoint Collapse

Symptom:
- desktop is fine, mobile layout overflows or overlaps

Likely cause:
- missing/incorrect media query overrides

Fix pattern:

```css
@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero img {
    width: 100%;
    height: auto;
  }
}
```

## 6) Safe Debug Procedure

1. Identify one broken section only.
2. Add temporary outline helpers (then remove):

```css
/* temporary debug */
.debug * {
  outline: 1px solid rgba(255, 0, 0, 0.25);
}
```

3. Check computed style and box model for the target nodes.
4. Change one variable at a time (size, fit, position, breakpoint).
5. Keep only the minimum patch that solves the issue.

## 7) Regression Guardrails

- Never patch multiple distant sections in one step.
- After each fix, verify:
  - hero
  - first content block
  - footer
- Confirm interactive elements still work (hover/click/scroll).
