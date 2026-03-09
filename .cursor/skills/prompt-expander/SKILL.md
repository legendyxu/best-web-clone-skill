---
name: prompt-expander
description: Expands vague user webpage requests into detailed, production-ready prompts for webpage cloning or generation workflows. Use when users provide short, casual, or non-technical website descriptions and you need a structured prompt before generating code.
---

# Prompt Expander - Webpage Generation

Convert a short user request into a detailed, AI-ready webpage prompt before code generation.

## When To Trigger

Use this skill before generating webpage code when user input is vague, short, or casual, for example:
- "I want a music website"
- "Make me a travel agency page"
- "Build a homepage for my student club"

If the user request is already specific and technical, this skill is optional.

## Workflow

### Step 1: Identify Website Type

Classify the request into one primary type:

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

### Step 3: Extract User Preferences

From the user message, extract:
- colors/theme (e.g. black background, light, minimal)
- style mood (elegant, playful, professional, bold)
- specific content/domain hints (artists, destinations, products, members)
- required features (booking, search, map, filter, timeline, etc.)
- audience and tone

If details are missing, use modern defaults appropriate for the chosen type.

### Step 4: Build Expanded Prompt

Use this output template:

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

### Step 5: Confirm Before Generation

After presenting the expanded prompt, ask:

> "Does this capture what you're looking for? You can adjust any details before I generate the webpage."

Only proceed to webpage generation after user approval.

## Quality Rules

- Do not use vague phrases like "nice colors" or "good layout"
- Preserve explicit user intent (never overwrite hard requirements)
- Include concrete examples relevant to the domain
- Match common industry conventions for the selected site type
- Scale complexity to request size (simple site -> fewer sections)

## Output Contract

When returning results for this skill, always provide:
1. inferred website type (+ assumptions if needed)
2. extracted user preferences
3. final expanded prompt
4. confirmation question before code generation

## Additional Resource

- Detailed domain references: [reference-library.md](reference-library.md)
