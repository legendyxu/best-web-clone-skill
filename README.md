<a id="readme-top"></a>

<!-- Hero -->
<h1 align="center">🌐 Best Web Clone Skill</h1>

<h3 align="center">Clone any website into a standalone single-file HTML page</h3>

<p align="center">
  <span style="color:#8b949e;font-size:14px;">Playwright capture · Gemini generation · Cursor Agent Skills</span>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-Automation-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Google-Gemini-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Cursor-Agent%20Skill-000000?style=flat-square&logo=cursor&logoColor=white" alt="Cursor">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-blue?style=flat-square" alt="English"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/lang-简体中文-red?style=flat-square" alt="简体中文"></a>
</p>

<p align="center">
  <a href="https://github.com/legendyxu" title="legendyxu"><img src="https://github.com/legendyxu.png?size=80" width="44" height="44" alt="legendyxu"></a>
  &nbsp;
  <a href="https://github.com/SteveRapeseed" title="SteveRapeseed"><img src="https://github.com/SteveRapeseed.png?size=80" width="44" height="44" alt="SteveRapeseed"></a>
</p>

<p align="center">
  <sub>Built by <a href="https://github.com/legendyxu">legendyxu</a> & <a href="https://github.com/SteveRapeseed">SteveRapeseed</a></sub>
</p>

---

<a id="demo"></a>

## 📸 Demo

**Music Platform Clone** — cloned with prompt: `"Build a music website"`

<p align="center">
  <img src="images/case1.png" alt="Music Platform Clone" width="960">
</p>

**Luxury Travel Platform Clone** — cloned with prompt: `"Build a luxury travel website"`

<p align="center">
  <img src="images/case2.png" alt="Luxury Travel Clone" width="960">
</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📖 About The Project

**Best Web Clone Skill** is a portable Agent Skill pack for [Cursor](https://cursor.sh) that turns any website URL into a single, browser-ready HTML file.

It is **not** a traditional web scraper or static-site exporter. Instead, it runs a three-stage automated pipeline:

1. **Capture** — Playwright opens the target page, takes full-page scrolling screenshots, extracts CSS, and optionally records a scroll video to trigger lazy-loaded content.
2. **Generate** — Screenshots and page context are sent to Google Gemini, which reconstructs a high-fidelity HTML replica from the visual information.
3. **Sync** — All output artifacts are written to disk: `web_replica.html`, `source_snapshot.png`, `source_styles.css`, and `run_manifest.txt`.

The skill pack includes two skills. **For most users, only `clone-skill` is required** — prompt expansion is already built into the clone pipeline.

| Skill | Required? | Role |
|---|---|---|
| `clone-skill` | **Yes** | Main clone pipeline — capture, generate, sync |
| `expander-skill` | Optional | Standalone Cursor Agent skill for prompt expansion **before** cloning |

### Built-in expander inside `clone-skill`

You do **not** need to call `expander-skill` separately for normal cloning.

When you pass `--instructions` (or a short creative prompt in Cursor), `clone_with_gemini.py` automatically:

1. Infers the website type (music, travel, ecommerce, etc.)
2. Decides whether your input is too short and needs expansion
3. Expands it into a structured design brief
4. Saves the result to `expanded_user_prompt.txt`
5. Sends that brief to Gemini along with the page screenshot

Example — this already runs the built-in expander:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "Build a music website"
```

Use `--confirm-expanded-prompt` if you want to review the expanded brief before generation starts.

### When to use standalone `expander-skill`

The separate `expander-skill` (`EXPANDER_SKILL.md`) is optional. Use it when you want prompt expansion **outside** the clone command — typically in Cursor chat:

| Scenario | Use built-in expander (`clone-skill`) | Use standalone `expander-skill` |
|---|---|---|
| Have a URL and a detailed prompt | ✅ Default choice | Not needed |
| You already have a URL and want HTML now | ✅ | Not needed |
| You only have an idea, **no URL yet** | ❌ | ✅ Expand the prompt first |
| You want **multi-turn chat** to refine the brief | ❌ | ✅ Iterate in conversation |
| You want to review/edit the prompt **before** any clone run | Optional (`--confirm-expanded-prompt`) | ✅ Better for back-and-forth editing |
| You want output as a design brief only, **no HTML yet** | ❌ | ✅ |

Standalone `expander-skill` gives the Cursor Agent richer reference material (`reference-library.md`) and a conversational workflow: classify → pull reference → extract constraints → build prompt → confirm with you.

**Typical flow with standalone expander:**

```
Expand this prompt: "Build a dark music streaming dashboard"
→ review and edit the expanded brief in chat
→ then run clone-skill with the approved prompt
```

**Typical flow without standalone expander (most common):**

```
Clone https://example.com — build a music website
→ clone-skill expands the prompt automatically and generates HTML
```

**Use cases:** design reference, page archival, style remixing, rapid prototyping.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## ✨ Features

- **URL → Single-File HTML** — Input a URL, get a self-contained `.html` you can open offline with no server required.
- **Three-Stage Pipeline** — `capture-matrix → replica-forge → artifact-sync`; each stage is isolated so failures are easy to locate.
- **Deep Browser Capture** — Full-page scroll screenshots, CSS extraction, optional scroll recordings — lazy-loaded content included.
- **Smart Prompt Expansion** — Short instructions like `"make it darker"` or `"build a music website"` are automatically expanded into complete design briefs before generation (built into `clone-skill`).
- **Automatic Runtime Bootstrap** — Creates `.runtime/venv` automatically, or falls back to `.runtime/site-packages` when a venv is unavailable. No manual dependency setup.
- **Dual Execution Paths** — Runs on host Python or inside Docker; output contract is identical either way.
- **Complete Artifact Output** — Produces `web_replica.html`, `source_snapshot.png`, `source_styles.css`, `run_manifest.txt`, plus compatibility aliases.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🛠 Built With

| Category | Technology |
|---|---|
| Language & Runtime | Python 3.11+ (Docker image uses 3.12) |
| Core Dependencies | `google-genai` (Gemini SDK), `playwright` (browser automation) |
| AI Model | Google Gemini — default `gemini-3.1-pro-preview`, fallback `gemini-3.0-pro-preview` |
| Browser Engine | Playwright + Chromium; Docker base image `mcr.microsoft.com/playwright/python:v1.58.0-noble` |
| Configuration | TOML (`cloneit.skill.toml`), env vars / `.env` (`GOOGLE_GEMINI_API_KEY`) |
| Containerization | Docker — entrypoint `clone_with_gemini.py` |
| Agent Integration | Cursor Skill system (`CLONE_SKILL.md`, `EXPANDER_SKILL.md`) |
| CI | GitHub Actions (Python 3.12, runtime bootstrap verification) |
| License | Apache 2.0 |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))
- Cursor editor ([download](https://cursor.sh))
- *(Optional)* Docker, if you prefer the containerized path

### Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/legendyxu/best-web-clone-skill.git
   cd best-web-clone-skill
   ```

2. **Set your Gemini API key**

   Create a `.env` file in the project root:

   ```env
   GOOGLE_GEMINI_API_KEY=your_api_key_here
   ```

3. **Install dependencies** *(the skill bootstraps automatically, but you can also do it manually)*

   ```bash
   pip install google-genai playwright
   playwright install chromium
   ```

4. **Add skills to Cursor**

   - **Required:** [`cloneit-web-cloning/CLONE_SKILL.md`](cloneit-web-cloning/CLONE_SKILL.md) — this is the main skill and already includes built-in prompt expansion.
   - **Optional:** [`.cursor/skills/prompt-expander/EXPANDER_SKILL.md`](.cursor/skills/prompt-expander/EXPANDER_SKILL.md) — only if you want to expand prompts in Cursor chat **before** running a clone.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 💡 Usage

### Basic clone

In Cursor chat, invoke the clone skill with a URL:

```
Clone https://example.com
```

The skill will run the full pipeline and output:

```
outputs/
├── web_replica.html       ← open this in your browser
├── source_snapshot.png    ← full-page screenshot of the original
├── source_styles.css      ← extracted CSS
└── run_manifest.txt       ← pipeline run log
```

### With a creative prompt (built-in expander)

```
Clone https://example.com — make it dark mode with neon accents
```

Or from the command line:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark mode with neon accents"
```

The clone pipeline expands your short instruction automatically and writes `expanded_user_prompt.txt` before calling Gemini. **You do not need `expander-skill` for this.**

### Standalone expander (optional)

Only use `expander-skill` when you want to shape the design brief **before** cloning — for example, when you do not have a target URL yet, or when you want several rounds of chat to refine the prompt:

```
Expand this prompt: "Build a luxury travel landing page with warm tones and a search-first hero"
```

After you approve the expanded brief in chat, pass it to `clone-skill` when you are ready to generate HTML.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🗺 Roadmap

### ✅ Completed

- Core clone pipeline (capture → generate → sync)
- Built-in prompt expansion in clone workflow
- Docker execution path
- GitHub Actions CI

### 📋 Planned

- Multi-page site cloning
- Interactive element preservation (forms, modals)
- Figma export from cloned HTML
- More language support in README
- Further improve `expander-skill`

See the [open issues](https://github.com/legendyxu/best-web-clone-skill/issues) for the full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

**Before you start**, please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

### How to Contribute

1. **Fork** the repository
2. **Create a branch** for your change:
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/your-bug-description
   ```
3. **Make your changes** and stage specific files (avoid `git add .`):
   ```bash
   git add <file1> <file2>
   git commit -m 'feat: add some amazing feature'
   ```
4. **Push** to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** — describe what you changed and why.

### Ways to Contribute

- 🐛 **Report bugs** — open an [Issue](https://github.com/legendyxu/best-web-clone-skill/issues) with steps to reproduce
- 💡 **Suggest features** — open an [Issue](https://github.com/legendyxu/best-web-clone-skill/issues) with the `enhancement` label
- 📖 **Improve docs** — fix typos, clarify instructions, add examples
- 🧪 **Write tests** — help improve coverage for the clone pipeline
- 🌐 **Add clone examples** — share interesting sites you've cloned

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📬 Contact

**legendyxu** — [legendyxuzhihao@outlook.com](mailto:legendyxuzhihao@outlook.com) — [GitHub](https://github.com/legendyxu)

**SteveRapeseed** — [steverapeseed@gmail.com](mailto:steverapeseed@gmail.com) — [GitHub](https://github.com/SteveRapeseed)

Project Link: [https://github.com/legendyxu/best-web-clone-skill](https://github.com/legendyxu/best-web-clone-skill)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🙏 Acknowledgments

- [Google Gemini](https://deepmind.google/technologies/gemini/) — the multimodal AI powering the HTML generation
- [Playwright](https://playwright.dev/) — browser automation and screenshot capture
- [Shields.io](https://shields.io) — badges
- [Cursor](https://cursor.sh) — the AI editor this skill is built for

<p align="right">(<a href="#readme-top">back to top</a>)</p>

