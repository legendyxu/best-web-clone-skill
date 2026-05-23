# Prompt Expansion

## Overview

The workflow accepts short user instructions and expands them only when that improves generation quality.

Examples of short instructions:

- `make it darker and cleaner`
- `emphasize mobile readability`
- `turn this into an anime-style landing page`

## Expansion Rules

When `--instructions` is provided, the workflow:

1. infers the likely website type from the source URL and the user brief
2. decides whether the input is already specific enough
3. expands short or vague instructions into a more structured prompt when needed
4. leaves already detailed instructions unchanged

## Output

The prepared prompt is written to:

- `expanded_user_prompt.txt`

## Confirmation Flow

If `--confirm-expanded-prompt` is used and auto-expansion actually occurs, the workflow pauses so the user can review the prepared prompt before generation continues.

## Purpose

This allows non-expert users to provide concise style hints without losing clarity in the final generation prompt.
