# Contributing

Thank you for considering contributing to this project. Every contribution — bug reports, documentation improvements, feature suggestions, and pull requests — is appreciated.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Conventions](#coding-conventions)
- [License](#license)

## Code of Conduct

This project is a small, focused tool. Be respectful and constructive. Unacceptable behavior will not be tolerated.

## Reporting Bugs

**Do not open a GitHub issue for security vulnerabilities.** See [SECURITY.md](SECURITY.md) for the security reporting process.

For non-security bugs:

1. **Search existing issues** — check if the bug has already been reported.
2. **Open a new issue** — include:
   - The exact command you ran
   - The full error output
   - Your environment: OS, Python version, whether you used Docker or host Python
   - The source URL you tried to clone (if applicable)
   - For visual bugs in cloned output, attach the generated HTML file if possible

## Suggesting Features

1. **Open an issue** describing the feature and its use case.
2. Indicate which skill it applies to: Clone or Expander.
3. If you have design ideas, include them.

We welcome suggestions, but not all features will be accepted. Complex features may need discussion before implementation.

## Pull Requests

### What we accept

- Bug fixes with clear reproduction steps
- Documentation improvements
- Changes that improve reliability or user experience

### What we do not currently accept

- Purely cosmetic changes (whitespace, style reformatting not aligned with project conventions)
- Large refactors without prior discussion

### Process

1. **Fork** the repository and create a branch from `main`.
2. **Run a smoke test** before opening a PR:

   ```bash
   python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only
   ```

3. **Keep PRs focused** — one change per PR.
4. **Write a clear commit message** explaining what and why.
5. **Update documentation** if your change affects a skill's behavior — update the corresponding `*_SKILL.md`.
6. **Open the PR** with a description that references the related issue, if any.

### Review process

- A maintainer will review your PR and may request changes.
- We aim to respond within one week.
- Once approved, a maintainer will merge.

## Development Setup

```bash
# Clone the repository
git clone git@github.com:legendyxu/best-web-clone-skill.git
cd best-web-clone-skill

# Set up your API key
cp .env.example .env
# Edit .env and fill in GOOGLE_GEMINI_API_KEY

# Verify your setup
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only
```

## Coding Conventions

- **Python**: 4-space indentation, type hints, `snake_case`.
- **Markdown**: 2-space indentation for lists. Wrap lines at about 100 characters.
- **Shell**: Prefer `python3` over `python` for portability.
- **Git**: Do not commit `.env` files, API keys, or runtime artifacts.

## License

By contributing, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
