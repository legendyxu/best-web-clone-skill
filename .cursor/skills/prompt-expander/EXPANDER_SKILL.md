---
name: expander-skill
description: Expands user-written raw webpage prompts into detailed, production-ready prompts for webpage generation or cloning workflows. Use when users ask to call this skill, request prompt optimization or expansion, or provide short non-technical website ideas before code generation — for example "make a music website", "build a travel agency page", "create a club homepage", or any other brief webpage request. Make sure to use this skill whenever the user provides a short or casual description of a webpage they want built, even if they don't explicitly ask for expansion.
---

# Expander Skill — Prompt Expander

This skill transforms a user's simple or vague webpage description into a detailed, structured prompt that produces higher-quality results from AI generation tools.

At a high level, the process is:

- identify the website type from the user's description
- pull the relevant domain conventions from the reference library
- extract explicit and implied user constraints
- build a structured expanded prompt covering style, sections, content, interactions, and audience
- confirm with the user before proceeding to generation

## Communicating With the User

This skill may be used by people with very different levels of technical familiarity. Adapt your language accordingly.

- If the user says "I want a music website", treat that as a valid starting point. Do not ask for more detail before starting the expansion.
- If the user gives detailed constraints ("dark theme, card layout, grid with hover effects"), integrate them directly rather than overwriting them.
- When the expanded prompt is ready, always ask for confirmation: "Does this capture what you're looking for? You can adjust any details before I generate the webpage."
- **Do not generate webpage code** before prompt expansion is completed and approved.

If required details are genuinely missing (the user hasn't said anything about the website type), ask up to 3 short clarifying questions, then continue.

## Trigger Rules

This skill should trigger in either mode:

1. **Explicit invocation** (highest priority)
   - User says: "call prompt-expander", "use prompt-expander", "expand my prompt", "optimize this prompt"
2. **Implicit invocation**
   - User gives a short or casual website request and asks for generation — for example "make a dark music website" or "build a travel landing page"

## Input Contract

Expected user input:

- **Required**: raw prompt text (the user's original intention, even if short)
- **Optional**: constraints for style, sections, audience, features, brand tone, and must-keep details

## Workflow

### Step 1: Identify Website Type

Classify into one primary type. If ambiguous, infer the closest type and explicitly state the assumption.

| Type | Common Keywords |
|------|-----------------|
| Media / Entertainment | music, podcast, video, streaming, radio |
| Travel / Tourism | travel, trip, tour, hotel, destination, agency |
| Community / Organization | club, society, nonprofit, team, school |
| Ecommerce / Product | shop, store, product, buy, sell, marketplace |
| Portfolio / Personal | portfolio, resume, personal, freelance, artist |
| Food / Restaurant | restaurant, cafe, menu, bakery, bar |
| Corporate / Business | company, startup, SaaS, consulting, agency |
| Event / Landing Page | event, conference, festival, launch, concert |
| Other / Unknown | anything not matching above |

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

Use it to determine:

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

Before returning the expanded prompt, ensure:

- no vague words like "nice", "good", or "cool"
- explicit user intent is preserved
- at least one concrete inspiration and concrete content examples are included
- the responsive requirement is present

### Step 6: Confirm Before Generation

After presenting the expanded prompt, always ask:

> "Does this capture what you're looking for? You can adjust any details before I generate the webpage."

Only proceed to webpage generation after user approval.

## Output Contract

Always return these 4 blocks:

1. inferred website type (plus any assumptions made)
2. extracted constraints
3. expanded final prompt
4. confirmation question before generation

## Examples

**Example 1: Dark music website**

Input: "call prompt-expander: make a dark music website for indie artists"

Expected action:

- classify as Media / Entertainment
- pull `REF: Media` reference
- extract constraints: dark theme, indie artists focus
- build expanded prompt with sections (Hero, Featured Artists, New Releases, Genres, Player)
- return all 4 output blocks and request confirmation

**Example 2: Travel landing page**

Input: "use prompt-expander on this prompt: travel landing page for Japan cherry blossom tours"

Expected action:

- classify as Travel / Tourism
- pull `REF: Travel` reference
- preserve user intent: Japan, cherry blossom tours
- apply travel conventions (hero search bar, destinations, testimonials, footer)
- return all 4 output blocks and request confirmation

## Additional Resources

- Detailed domain conventions per type: [reference-library.md](reference-library.md)
