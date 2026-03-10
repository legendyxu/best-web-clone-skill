---
name: prompt-expander
description: Expands user-written raw webpage prompts into detailed, production-ready prompts for webpage generation workflows. Use when users ask to call this skill, request prompt optimization/expansion, or provide short non-technical website ideas before code generation.
---

# Prompt Expander

Convert a raw user prompt into a structured, high-fidelity prompt before webpage code generation.

## Trigger Rules

Trigger this skill in either mode:

1. Explicit invocation (highest priority)
   - User says: "call prompt-expander", "use prompt-expander", "expand my prompt", "optimize this prompt"
2. Implicit invocation
   - User gives a short/casual website request and asks for generation

Do not generate webpage code before prompt expansion is completed and approved.

## Input Contract

Expected user input:
- Required: raw prompt text (the user's original intention)
- Optional: constraints for style, sections, audience, features, brand tone, and must-keep details

If required details are missing, ask up to 3 short clarifying questions, then continue.

## Workflow

### Step 1: Identify Website Type

Classify into one primary type:

| Type | Common Keywords |
|------|------------------|
| Media / Entertainment | music, podcast, video, streaming, radio |
| Travel / Tourism | travel, trip, tour, hotel, destination, agency |
| Community / Organization | club, society, nonprofit, team, school |
| Ecommerce / Product | shop, store, product, buy, sell, marketplace |
| Portfolio / Personal | portfolio, resume, personal, freelance, artist |
| Food / Restaurant | restaurant, cafe, menu, bakery, bar |
| Corporate / Business | company, startup, SaaS, consulting, agency |
| Event / Landing Page | event, conference, festival, launch, concert |
| Other / Unknown | anything not matching above |

If ambiguous, infer the closest type and explicitly state the assumption.

### Step 2: Pull Type Reference

Read the matching section in `reference-library.md`:
- `REF: Media`
- `REF: Travel`
- `REF: Community`
- `REF: Ecommerce`
- `REF: Portfolio`
- `REF: Food`
- `REF: Corporate`
- `REF: Event`
- `REF: Other`

Use it to choose:
- expected section order
- common content structure
- common interaction patterns

### Step 3: Extract User Constraints

From the user message, extract:
- hard constraints (must keep): colors, style words, forbidden elements
- content constraints: named entities, domain items, priority sections
- feature constraints: booking, search, map, filter, timeline, player, etc.
- audience and tone

If details are missing, use modern defaults appropriate for the chosen type.

### Step 4: Build Expanded Prompt

Use this template:

```markdown
I want to create a [WEBSITE TYPE] webpage.

**Visual Style:**
- Overall aesthetic: [type + preference based]
- Color scheme: [specific colors]
- Typography: [style direction]
- Layout feel: [grid / editorial / card / immersive]
- Inspiration: [1-2 known products/sites]

**Page Sections:** (top to bottom)
1. [Section name] - [purpose + content]
2. [Section name] - [purpose + content]
3. [Section name] - [purpose + content]

**Content Details:**
1. [Category] - [concrete examples]
2. [Category] - [concrete examples]
3. [Category] - [concrete examples]

**Key Features & Interactions:**
- [Feature + behavior]
- [Feature + behavior]
- Navigation: [structure]
- Hover effects: [specific behavior]
- Responsive: mobile + desktop

**Audience & Tone:**
- Target audience: [...]
- Emotional tone: [...]
- Primary CTA: [...]
```

### Step 5: Quality Gate

Before returning:
- ensure no vague words (for example: "nice", "good", "cool")
- ensure explicit user intent is preserved
- ensure at least one concrete inspiration and concrete content examples
- ensure responsive requirement is present

### Step 6: Confirm Before Generation

After presenting the expanded prompt, always ask:

> "Does this capture what you're looking for? You can adjust any details before I generate the webpage."

Only proceed to webpage generation after user approval.

## Output Contract

Always return these 4 blocks:
1. inferred website type (+ assumptions)
2. extracted constraints
3. expanded final prompt
4. confirmation question before generation

## Explicit Invocation Examples

Example 1:
- User: "call prompt-expander: make a dark music website for indie artists"
- Skill action: classify -> expand -> return final prompt -> request confirmation

Example 2:
- User: "use prompt-expander on this prompt: travel landing page for Japan cherry blossom tours"
- Skill action: preserve user intent -> apply travel conventions -> return expanded prompt

## Additional Resource

- Detailed domain references: [reference-library.md](reference-library.md)
