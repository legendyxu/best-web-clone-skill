#!/usr/bin/env python3
"""
Self-contained web cloning runner for the cloneit-web-cloning skill.

This script does not depend on clone_pipeline.py or other repository engine files.
It bootstraps its own runtime, verifies required packages/browser, captures a source
website, then asks Gemini to forge a single-file HTML replica.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import tomllib
import traceback
import venv
from pathlib import Path
from typing import Any, Optional

RUNTIME_ENV = "WEB_REPLICA_RUNTIME_ACTIVE"

SITE_TYPE_PROFILES: dict[str, dict[str, Any]] = {
    "media": {
        "display_name": "Media / Entertainment",
        "default_aesthetic": "an immersive content-browsing experience with strong hierarchy, engaging thumbnails, and fast scanning for repeat viewing",
        "default_color_scheme": "high-contrast media surfaces with one vibrant accent color and clear visual separation between content blocks",
        "default_typography": "bold display headings paired with readable interface labels and compact card metadata",
        "default_layout": "a hero-led layout with category navigation, featured rails, and repeatable thumbnail cards",
        "inspiration": ["YouTube", "YouTube Music", "Spotify"],
        "sections": [
            ("Hero / Featured Banner", "Spotlight the most important content or campaign with clear artwork and an immediate play CTA"),
            ("Primary Category Navigation", "Expose the most important browse categories above the fold"),
            ("Featured Collections", "Show curated rows of playlists, themes, or creator-led collections"),
            ("Popular Videos / Creators", "Use repeatable thumbnail cards with duration, title, and creator metadata"),
            ("New & Recommended", "Surface newly released, trending, or recommended content blocks"),
            ("Utility / Footer", "Keep support, help, account, and policy links easy to find"),
        ],
        "content_details": [
            "Featured content — hero videos, trending uploads, themed playlists, and creator spotlights",
            "Card metadata — thumbnail, title, creator/channel, duration, and lightweight engagement cues",
            "Browse taxonomy — categories such as trending, favorites, genres, or featured topics",
            "Visual language — artwork-led cards and strong thumbnail hierarchy",
        ],
        "features": [
            "Prominent search and browse entry points for repeat discovery",
            "Hover/tap affordances on cards, including quick-play or highlight states",
            "Consistent thumbnail ratios and media metadata hierarchy",
        ],
        "audience": "people browsing video, music, or entertainment content",
        "tone": "engaging, energetic, and easy to explore",
        "cta": "start watching and discover more content",
    },
    "travel": {
        "display_name": "Travel / Tourism",
        "default_aesthetic": "trust-building travel browsing with aspirational imagery and clear decision support",
        "default_color_scheme": "warm neutrals, sky tones, and accent colors that feel optimistic and travel-ready",
        "default_typography": "clean headings with practical, readable supporting text",
        "default_layout": "search-first hero followed by destinations, offers, and proof sections",
        "inspiration": ["Airbnb", "Booking.com", "Expedia"],
        "sections": [
            ("Hero / Search", "Lead with destination discovery and an obvious search or booking action"),
            ("Popular Destinations", "Show aspirational destination cards with strong imagery"),
            ("Featured Offers", "Highlight packages, deals, or guided tours with concise benefit summaries"),
            ("Trust Signals", "Use reviews, metrics, or guarantees to reduce booking hesitation"),
            ("Travel Tips / Guides", "Support exploration with useful destination content"),
            ("Footer / Contact", "Keep support, policies, and contact actions available"),
        ],
        "content_details": [
            "Destination cards — location, image, short value cue, and price or offer framing",
            "Booking cues — dates, travelers, quote requests, or availability summaries",
            "Social proof — ratings, reviews, trust badges, and repeat-customer cues",
        ],
        "features": [
            "Above-the-fold search or quote CTA",
            "Map-aware browsing cues or location context",
            "Mobile-first layout for quick travel browsing",
        ],
        "audience": "people researching trips, accommodations, or destination experiences",
        "tone": "aspirational, trustworthy, and helpful",
        "cta": "book now, explore, or request a quote",
    },
    "community": {
        "display_name": "Community / Organization",
        "default_aesthetic": "approachable, human, and real-photo-driven with clear participation cues",
        "default_color_scheme": "friendly greens, blues, and grounded brand colors that feel welcoming",
        "default_typography": "warm, readable headings with practical supporting copy",
        "default_layout": "mission-led landing flow with events, people, and join actions",
        "inspiration": ["Meetup", "university club pages", "nonprofit homepages"],
        "sections": [
            ("Hero / Mission", "Explain what the group is and why someone should join"),
            ("About", "Summarize history, purpose, and differentiators"),
            ("Activities / Events", "Show upcoming activities with dates and participation cues"),
            ("Members / Team", "Feature organizers or members with role clarity"),
            ("Gallery / Highlights", "Use real photos to show recent activity"),
            ("Join / Contact", "Provide a clear application or contact action"),
        ],
        "content_details": [
            "Event cards — date, title, location, summary, RSVP cue",
            "Member cards — photo, name, role, and short intro",
            "Milestones — achievements, years active, member count, or impact metrics",
        ],
        "features": [
            "Prominent join or contact CTA",
            "Easy-to-scan event list and announcements",
            "Mobile-friendly layout for members checking updates on phones",
        ],
        "audience": "members, prospective members, supporters, or volunteers",
        "tone": "welcoming, social, and credible",
        "cta": "join the community or get involved",
    },
    "ecommerce": {
        "display_name": "E-commerce / Product",
        "default_aesthetic": "product-first merchandising with clear price hierarchy and conversion focus",
        "default_color_scheme": "clean product surfaces with one strong merchandising accent",
        "default_typography": "clear commerce typography optimized for scannability and pricing clarity",
        "default_layout": "promo hero, category navigation, product grid, and trust-building merchandising sections",
        "inspiration": ["Nike", "Zara", "Amazon", "Shopify stores"],
        "sections": [
            ("Promo Hero", "Lead with the strongest offer, collection, or bestseller"),
            ("Category Navigation", "Expose product families with quick browse actions"),
            ("Featured Products", "Use repeatable product cards with pricing and quick actions"),
            ("Offer / Trust Banner", "Show shipping, returns, or time-limited promotions"),
            ("Reviews / Social Proof", "Reassure buyers with ratings and testimonials"),
            ("Footer / Policy Block", "Surface shipping, returns, FAQ, and support"),
        ],
        "content_details": [
            "Product cards — image, name, price, sale state, rating, add-to-cart",
            "Category tiles — strong image plus clear browse CTA",
            "Trust content — returns, shipping, guarantees, or sustainability claims",
        ],
        "features": [
            "Sticky shopping controls such as cart or filters",
            "Clear discount and pricing hierarchy",
            "Fast browse-to-product transitions with quick action states",
        ],
        "audience": "shoppers comparing products and deciding what to buy",
        "tone": "confident, clear, and conversion-oriented",
        "cta": "shop now or add to cart",
    },
    "portfolio": {
        "display_name": "Portfolio / Personal",
        "default_aesthetic": "brand-forward self-presentation with clear project storytelling and personality",
        "default_color_scheme": "personal-brand colors chosen to reflect craft and point of view",
        "default_typography": "high-identity headings paired with restrained supporting copy",
        "default_layout": "intro hero followed by work samples, background, and contact sections",
        "inspiration": ["Awwwards portfolios", "Dribbble profiles", "GitHub Pages portfolios"],
        "sections": [
            ("Intro Hero", "State identity, role, and strongest positioning statement"),
            ("About", "Explain background, process, or differentiators"),
            ("Projects / Work", "Show the most important case studies or project cards"),
            ("Skills / Experience", "Summarize craft areas, tools, or timeline milestones"),
            ("Testimonials / Recognition", "Use quotes or awards to add credibility"),
            ("Contact", "End with direct outreach actions and external links"),
        ],
        "content_details": [
            "Project cards — visual preview, title, summary, stack, and link out",
            "Experience items — role, timeframe, and impact summary",
            "Branding cues — headshot, monogram, visual motifs, or signature colors",
        ],
        "features": [
            "Strong project-card interactions and hover reveals",
            "Clear external links to portfolio destinations or social profiles",
            "Responsive layout that preserves project storytelling on mobile",
        ],
        "audience": "clients, employers, collaborators, or community peers",
        "tone": "confident, distinctive, and polished",
        "cta": "view work or get in touch",
    },
    "food": {
        "display_name": "Food / Restaurant",
        "default_aesthetic": "appetite-led hospitality design with strong atmosphere and menu storytelling",
        "default_color_scheme": "warm restaurant tones with rich contrast and food-friendly accents",
        "default_typography": "expressive headings with easy menu readability",
        "default_layout": "atmosphere hero, menu highlights, and reservation/order flow",
        "inspiration": ["premium bistro sites", "restaurant brand pages", "menu-first dining pages"],
        "sections": [
            ("Atmosphere Hero", "Set the mood and lead to reserve or order actions"),
            ("Restaurant Story", "Explain cuisine, concept, or chef point of view"),
            ("Menu Highlights", "Show standout dishes with photography and descriptions"),
            ("Menu Categories", "Organize food and drinks into browsable groups"),
            ("Reservations / Ordering", "Keep the main conversion path obvious"),
            ("Location / Hours", "Provide visit details and confidence cues"),
        ],
        "content_details": [
            "Dish cards — image, dish name, description, price, dietary tags",
            "Atmosphere content — interior, chef, plating, service moments",
            "Visit info — address, hours, reservation cues, or delivery options",
        ],
        "features": [
            "Obvious reserve or order CTA above the fold",
            "Readable menu presentation on mobile",
            "High-quality imagery that does most of the persuasive work",
        ],
        "audience": "diners deciding whether to visit, reserve, or order",
        "tone": "inviting, flavorful, and premium",
        "cta": "reserve a table or order now",
    },
    "corporate": {
        "display_name": "Corporate / Business",
        "default_aesthetic": "professional, high-trust marketing design with clear value hierarchy",
        "default_color_scheme": "calm business neutrals with one assertive brand accent",
        "default_typography": "clean, authoritative headings with clear functional copy",
        "default_layout": "value-proposition hero followed by services, proof, and conversion sections",
        "inspiration": ["Stripe", "Notion", "HubSpot", "Linear"],
        "sections": [
            ("Value Proposition Hero", "Explain what the company does and why it matters"),
            ("Services / Product Overview", "Break offerings into concise, scannable cards"),
            ("How It Works", "Show a clear process or onboarding sequence"),
            ("Social Proof / Results", "Use logos, metrics, and testimonials"),
            ("Resources / Case Studies", "Back up claims with deeper proof"),
            ("Contact / CTA", "End with a direct demo, contact, or signup action"),
        ],
        "content_details": [
            "Service cards — title, summary, and business benefit",
            "Results content — metrics, case studies, client logos, or testimonial quotes",
            "Conversion cues — demo CTA, contact CTA, or free-trial framing",
        ],
        "features": [
            "Strong above-the-fold CTA hierarchy",
            "Clear informational structure for scanning and trust building",
            "Responsive layout suitable for busy decision-makers on mobile",
        ],
        "audience": "buyers, leads, executives, or stakeholders evaluating a solution",
        "tone": "credible, clear, and outcome-driven",
        "cta": "book a demo, talk to sales, or get started",
    },
    "event": {
        "display_name": "Event / Landing Page",
        "default_aesthetic": "high-energy landing design focused on urgency, information, and conversion",
        "default_color_scheme": "bold event colors with strong contrast and standout CTA emphasis",
        "default_typography": "large-impact headings with dense but readable schedule information",
        "default_layout": "hero-first landing page with agenda, speakers, and registration emphasis",
        "inspiration": ["conference pages", "festival pages", "launch landing pages"],
        "sections": [
            ("Hero / Event Header", "State event name, timing, and main registration action"),
            ("Overview", "Explain who it is for and why it matters"),
            ("Speakers / Performers", "Feature the people that drive interest"),
            ("Agenda / Schedule", "Organize timing and sessions clearly"),
            ("Tickets / Registration", "Make conversion options obvious and comparable"),
            ("FAQ / Venue", "Reduce friction around attendance details"),
        ],
        "content_details": [
            "Speaker cards — photo, role, topic, and credibility",
            "Agenda rows — time, title, stage/room, and presenter",
            "Ticket tiers — benefits, pricing, and urgency cues",
        ],
        "features": [
            "Single clear conversion goal with repeated CTA exposure",
            "Urgency cues such as countdown, limited spots, or early-bird framing",
            "Mobile-friendly flow for shareable event traffic",
        ],
        "audience": "attendees deciding whether to register or participate",
        "tone": "energetic, urgent, and exciting",
        "cta": "register now or get tickets",
    },
    "other": {
        "display_name": "Other / Unknown",
        "default_aesthetic": "clear, modern, category-agnostic product presentation with flexible card-based content",
        "default_color_scheme": "clean light background, one strong accent color, and readable neutral text",
        "default_typography": "readable sans-serif hierarchy with clear section contrast",
        "default_layout": "hero-first flow with offer explanation, featured content, proof, and CTA sections",
        "inspiration": ["The Verge", "Coursera", "Zillow", "Peloton"],
        "sections": [
            ("Hero / Above the Fold", "Clearly state the main promise and primary action"),
            ("What We Offer", "Break the offer into concise, scannable value blocks"),
            ("Featured Content / Showcase", "Use the main cards, listings, or modules people browse"),
            ("Social Proof", "Support trust with numbers, reviews, or partners"),
            ("How It Works", "Clarify the main workflow if onboarding matters"),
            ("CTA / Footer", "Provide the next step plus support and legal links"),
        ],
        "content_details": [
            "Core cards — the main browsable items on the page, presented with strong hierarchy",
            "Proof elements — reviews, metrics, trust badges, or partner references",
            "Utility content — onboarding cues, secondary links, FAQ, or support access",
        ],
        "features": [
            "Clear above-the-fold CTA and readable section hierarchy",
            "Card-based browsing patterns that remain coherent on mobile",
            "Trust-building copy and layout defaults when the category is unclear",
        ],
        "audience": "general users exploring the page for value and next steps",
        "tone": "clear, modern, and trustworthy",
        "cta": "learn more, explore, or get started",
    },
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in _read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip()
        if not key:
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        out[key] = val
    return out


def _deep_get(cfg: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    cur: Any = cfg
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        data = tomllib.load(f)
    return data if isinstance(data, dict) else {}


def _resolve_config_path(raw: Optional[str], skill_root: Path) -> Path:
    default = skill_root / "assets" / "cloneit.skill.toml"
    if raw is None:
        return default
    p = Path(raw)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def _resolve_prompt_text(
    cfg: dict[str, Any],
    *,
    cfg_path: Path,
    inline_key: str,
    file_key: str,
) -> str:
    inline = str(_deep_get(cfg, inline_key, "") or "").strip()
    if inline:
        return inline
    file_raw = str(_deep_get(cfg, file_key, "") or "").strip()
    if not file_raw:
        return ""
    p = Path(file_raw)
    if not p.is_absolute():
        p = (cfg_path.parent / p).resolve()
    if not p.exists():
        return ""
    return _read_text(p).strip()


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _default_out_dir() -> Path:
    return (Path.cwd() / "outputs" / f"replica_run_{_now_stamp()}").resolve()


def _venv_python_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _runtime_browser_dir(runtime_dir: Path) -> Path:
    return runtime_dir / "pw-browsers"


def _managed_runtime_env(skill_root: Path, *, base_env: Optional[dict[str, str]] = None) -> dict[str, str]:
    env = (base_env or os.environ).copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(_runtime_browser_dir(skill_root / ".runtime").resolve())
    return env


def _is_git_lfs_pointer(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            first_line = handle.readline().strip()
            second_line = handle.readline().strip()
    except OSError:
        return False
    return first_line == "version https://git-lfs.github.com/spec/v1" and second_line.startswith("oid sha256:")


def _playwright_driver_node_path(venv_dir: Path) -> Optional[Path]:
    candidates: list[Path] = []
    lib_dir = venv_dir / "lib"
    if lib_dir.exists():
        for site_packages in lib_dir.glob("python*/site-packages"):
            candidates.append(site_packages / "playwright" / "driver" / "node")
    candidates.append(venv_dir / "Lib" / "site-packages" / "playwright" / "driver" / "node.exe")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _managed_runtime_rebuild_reason(venv_dir: Path, venv_python: Path) -> Optional[str]:
    if not venv_dir.exists():
        return None
    if not venv_python.exists():
        return "managed runtime is missing its python executable"

    activate = venv_dir / "bin" / "activate"
    if os.name != "nt" and activate.exists():
        activate_text = _read_text(activate)
        expected_path = str(venv_dir.resolve())
        if expected_path not in activate_text:
            return "managed runtime activation script points to a different machine path"

    driver_node = _playwright_driver_node_path(venv_dir)
    if driver_node is not None and _is_git_lfs_pointer(driver_node):
        return "Playwright driver binary was checked out as a Git LFS pointer"

    return None


def _reset_managed_runtime(runtime_dir: Path) -> None:
    for stale_path in (runtime_dir / "venv", _runtime_browser_dir(runtime_dir)):
        if stale_path.exists():
            print(f"[bootstrap] removing stale managed runtime path: {stale_path}")
            shutil.rmtree(stale_path)


def _using_managed_runtime_python(skill_root: Path) -> bool:
    managed_python = _venv_python_path(skill_root / ".runtime" / "venv")
    if not managed_python.exists():
        return False
    try:
        return Path(sys.executable).resolve() == managed_python.resolve()
    except OSError:
        return False


def _browser_glob_patterns(*, headed: bool) -> tuple[str, ...]:
    if headed:
        return (
            "chromium-*/chrome-linux64/chrome",
        )
    return (
        "chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
        "chromium-*/chrome-linux64/chrome",
    )


def _discover_browser_executable(
    *,
    env_map: Optional[dict[str, str]] = None,
    headed: bool = False,
) -> Optional[Path]:
    env_map = env_map or os.environ
    seen: set[str] = set()
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        try:
            resolved = str(path.resolve())
        except OSError:
            resolved = str(path)
        if resolved in seen or not path.exists():
            return
        seen.add(resolved)
        candidates.append(path)

    override = str(env_map.get("WEB_REPLICA_BROWSER_EXECUTABLE", "")).strip()
    if override:
        add_candidate(Path(override).expanduser())

    browser_roots: list[Path] = []
    browser_root_env = str(env_map.get("PLAYWRIGHT_BROWSERS_PATH", "")).strip()
    if browser_root_env:
        browser_roots.append(Path(browser_root_env).expanduser())
    browser_roots.append(Path.home() / ".cache" / "ms-playwright")

    for root in browser_roots:
        for pattern in _browser_glob_patterns(headed=headed):
            for candidate in sorted(root.glob(pattern), reverse=True):
                add_candidate(candidate)

    for binary_name in ("chromium-browser", "chromium", "google-chrome", "google-chrome-stable", "microsoft-edge"):
        path = shutil.which(binary_name)
        if path:
            add_candidate(Path(path))

    return candidates[0] if candidates else None


def _cmd_as_str(cmd: list[str]) -> str:
    return " ".join(shlex.quote(str(p)) for p in cmd)


def _print_error_hint(exc: Exception) -> None:
    message = str(exc)
    upper = message.upper()
    hints: list[str] = []

    if "GOOGLE_GEMINI_API_KEY" in message:
        hints.append("Set GOOGLE_GEMINI_API_KEY in the current shell or in a .env file next to the project.")

    if "ERR_TUNNEL_CONNECTION_FAILED" in upper or "ERR_PROXY_CONNECTION_FAILED" in upper:
        hints.append("The browser could not reach the target website through the current proxy/tunnel settings.")
        hints.append("Check whether the machine can open the target URL in a normal browser, or disable the broken proxy before rerunning.")
    elif "ERR_NAME_NOT_RESOLVED" in upper or "ERR_CONNECTION_TIMED_OUT" in upper or "ERR_CONNECTION_REFUSED" in upper:
        hints.append("The runtime is healthy, but the target website is not reachable from this machine right now.")
    elif "PLAYWRIGHT BROWSER BOOTSTRAP FAILED" in upper:
        hints.append("No usable browser was available. Install Chrome/Chromium locally or allow Playwright browser downloads.")

    if hints:
        print("[hint] Suggested next steps:", file=sys.stderr)
        for hint in hints:
            print(f"[hint] - {hint}", file=sys.stderr)


def _run_cmd(
    cmd: list[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    check: bool = True,
    stream: bool = False,
    timeout_s: Optional[int] = None,
) -> subprocess.CompletedProcess[str]:
    try:
        if stream:
            proc = subprocess.run(
                [str(p) for p in cmd],
                cwd=str(cwd) if cwd is not None else None,
                env=env,
                text=True,
                timeout=timeout_s,
            )
        else:
            proc = subprocess.run(
                [str(p) for p in cmd],
                cwd=str(cwd) if cwd is not None else None,
                env=env,
                text=True,
                capture_output=True,
                timeout=timeout_s,
            )
    except subprocess.TimeoutExpired as exc:
        timeout_info = f"{int(timeout_s)}s" if timeout_s is not None else "configured timeout"
        raise RuntimeError(f"runtime command timed out after {timeout_info}: {_cmd_as_str(cmd)}") from exc
    if check and proc.returncode != 0:
        print(f"[runtime] command failed ({proc.returncode}): {_cmd_as_str(cmd)}", file=sys.stderr)
        if (not stream) and proc.stdout.strip():
            print(proc.stdout, file=sys.stderr)
        if (not stream) and proc.stderr.strip():
            print(proc.stderr, file=sys.stderr)
        raise RuntimeError("runtime command failed")
    return proc


def _ensure_runtime(skill_root: Path, cfg: dict[str, Any], *, force_rebuild: bool = False) -> Path:
    runtime_dir = skill_root / ".runtime"
    venv_dir = runtime_dir / "venv"
    venv_python = _venv_python_path(venv_dir)
    runtime_env = _managed_runtime_env(skill_root)
    browser_dir = Path(runtime_env["PLAYWRIGHT_BROWSERS_PATH"])
    requirements = skill_root / "assets" / "requirements.txt"
    package_install_timeout_s = int(_deep_get(cfg, "runtime.package_install_timeout_seconds", 900))
    browser_install_timeout_s = int(_deep_get(cfg, "runtime.browser_install_timeout_seconds", 1200))
    pip_network_timeout_s = int(_deep_get(cfg, "runtime.pip_network_timeout_seconds", 45))
    pip_retries = int(_deep_get(cfg, "runtime.pip_retries", 2))

    rebuild_reason = "requested with --force-rebuild-runtime" if force_rebuild else _managed_runtime_rebuild_reason(venv_dir, venv_python)
    if rebuild_reason:
        print(f"[bootstrap] rebuilding managed runtime: {rebuild_reason}")
        _reset_managed_runtime(runtime_dir)

    if not venv_python.exists():
        print(f"[bootstrap] creating virtualenv at {venv_dir}")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True, clear=False, symlinks=True).create(str(venv_dir))

    check_code = (
        "import importlib\n"
        "mods=['google.genai','playwright.sync_api']\n"
        "missing=[]\n"
        "for m in mods:\n"
        "  try:\n"
        "    importlib.import_module(m)\n"
        "  except Exception as e:\n"
        "    missing.append(f'{m}: {e}')\n"
        "print('OK' if not missing else '\\n'.join(missing))\n"
        "raise SystemExit(0 if not missing else 2)\n"
    )

    needs_install = True
    probe = _run_cmd([str(venv_python), "-c", check_code], env=runtime_env, check=False)
    if probe.returncode == 0:
        needs_install = False
        print("[bootstrap] python packages already present")

    if needs_install:
        if not requirements.exists():
            raise RuntimeError(f"requirements file missing: {requirements}")
        print("[bootstrap] installing python packages (streaming logs)")
        pip_common = [
            "--retries",
            str(max(0, pip_retries)),
            "--timeout",
            str(max(1, pip_network_timeout_s)),
        ]
        try:
            _run_cmd(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", *pip_common],
                env=runtime_env,
                stream=True,
                timeout_s=package_install_timeout_s,
            )
            _run_cmd(
                [str(venv_python), "-m", "pip", "install", "-r", str(requirements), *pip_common],
                env=runtime_env,
                stream=True,
                timeout_s=package_install_timeout_s,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                "Python package bootstrap failed. Check network access to PyPI and retry, "
                "or preinstall dependencies from assets/requirements.txt."
            ) from exc

    install_playwright = bool(_deep_get(cfg, "runtime.install_playwright", True))
    browser_executable = _discover_browser_executable(env_map=runtime_env, headed=False)
    if install_playwright:
        browser_dir.mkdir(parents=True, exist_ok=True)
        print(f"[bootstrap] Playwright browser cache: {browser_dir}")
        if browser_executable is not None:
            print(
                "[bootstrap] reusing existing browser executable instead of downloading Chromium: "
                f"{browser_executable}"
            )
        else:
            print("[bootstrap] ensuring Chromium is installed for Playwright (streaming logs)")
            try:
                _run_cmd(
                    [str(venv_python), "-m", "playwright", "install", "chromium"],
                    env=runtime_env,
                    stream=True,
                    timeout_s=browser_install_timeout_s,
                )
            except RuntimeError as exc:
                fallback_browser = _discover_browser_executable(env_map=runtime_env, headed=False)
                if fallback_browser is None:
                    raise RuntimeError(
                        "Playwright browser bootstrap failed. Check network/system dependencies, "
                        "then retry `--bootstrap-only`."
                    ) from exc
                browser_executable = fallback_browser
                print(
                    "[bootstrap] Playwright browser download failed; "
                    f"falling back to existing browser executable: {fallback_browser}"
                )

    verify_browser = bool(_deep_get(cfg, "runtime.verify_browser_launch", True))
    if verify_browser:
        browser_executable = _discover_browser_executable(env_map=runtime_env, headed=False)
        launch_line = "  b=p.chromium.launch(headless=True"
        if browser_executable is not None:
            print(f"[bootstrap] using browser executable: {browser_executable}")
            launch_line += f", executable_path={str(browser_executable)!r}"
        launch_line += ")\n"
        browser_probe = "".join(
            [
                "from playwright.sync_api import sync_playwright\n",
                "with sync_playwright() as p:\n",
                launch_line,
                "  page=b.new_page()\n",
                "  page.goto('about:blank')\n",
                "  b.close()\n",
                "print('browser-ok')\n",
            ]
        )
        _run_cmd([str(venv_python), "-c", browser_probe], env=runtime_env)
        print("[bootstrap] browser launch verification passed")

    # Final package probe after install.
    _run_cmd([str(venv_python), "-c", check_code], env=runtime_env)
    return venv_python


def _discover_gemini_key(skill_root: Path) -> str:
    env_val = str(os.getenv("GOOGLE_GEMINI_API_KEY", "")).strip()
    if env_val:
        return env_val

    candidates = [
        Path.cwd() / ".env",
        skill_root / ".env",
        skill_root.parent / ".env",
    ]
    for p in candidates:
        data = _parse_dotenv(p)
        key = str(data.get("GOOGLE_GEMINI_API_KEY", "")).strip()
        if key:
            return key
    raise RuntimeError(
        "GOOGLE_GEMINI_API_KEY is missing. Set it in environment or in a .env file in current directory."
    )


def _extract_css_js() -> str:
    return r"""
() => {
  const blocks = [];
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const rules = Array.from(sheet.cssRules || []);
      if (rules.length) {
        blocks.push(rules.map((r) => r.cssText).join('\n'));
      }
    } catch (_) {
      // Ignore cross-origin stylesheet access errors.
    }
  }
  return blocks.join('\n\n');
}
"""


def _capture_matrix(
    *,
    url: str,
    snapshot_path: Path,
    styles_path: Path,
    video_path: Optional[Path],
    viewport_w: int,
    viewport_h: int,
    wait_ms: int,
    scroll_step_px: int,
    scroll_pause_ms: int,
    scroll_cap_px: int,
    headed: bool,
) -> None:
    from playwright.sync_api import sync_playwright

    video_tmp = snapshot_path.parent / ".video_tmp"
    if video_path is not None:
        video_tmp.mkdir(parents=True, exist_ok=True)

    print("[capture-matrix] launching browser")
    with sync_playwright() as p:
        launch_kwargs: dict[str, Any] = {"headless": not headed}
        browser_executable = _discover_browser_executable(headed=headed)
        if browser_executable is not None:
            print(f"[capture-matrix] using browser executable: {browser_executable}")
            launch_kwargs["executable_path"] = str(browser_executable)
        browser = p.chromium.launch(**launch_kwargs)
        context_kwargs: dict[str, Any] = {
            "viewport": {"width": int(viewport_w), "height": int(viewport_h)}
        }
        if video_path is not None:
            context_kwargs["record_video_dir"] = str(video_tmp)
            context_kwargs["record_video_size"] = {"width": int(viewport_w), "height": int(viewport_h)}

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        print(f"[capture-matrix] navigating {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(max(0, int(wait_ms)))

        print("[capture-matrix] executing progressive scroll")
        page.evaluate(
            f"""
() => new Promise((resolve) => {{
  const step = {int(scroll_step_px)};
  const pause = {int(scroll_pause_ms)};
  const cap = {int(scroll_cap_px)};
  let moved = 0;
  const tick = () => {{
    window.scrollBy(0, step);
    moved += step;
    const atBottom = window.scrollY + window.innerHeight >= document.body.scrollHeight - 2;
    if (atBottom || moved >= cap) {{
      window.scrollTo(0, 0);
      setTimeout(resolve, Math.max(400, pause));
      return;
    }}
    setTimeout(tick, pause);
  }};
  tick();
}})
"""
        )

        print(f"[capture-matrix] saving snapshot -> {snapshot_path}")
        page.screenshot(path=str(snapshot_path), full_page=True)

        print(f"[style-harvest] extracting CSS -> {styles_path}")
        css_text = page.evaluate(_extract_css_js()) or ""
        css_text = str(css_text).strip()
        if not css_text:
            css_text = "/* CSS extraction returned empty output. */"
        _write_text(styles_path, css_text)

        page.close()
        context.close()
        browser.close()

    if video_path is not None:
        webm_files = sorted(video_tmp.glob("*.webm"))
        if webm_files:
            shutil.move(str(webm_files[0]), str(video_path))
            print(f"[capture-matrix] saved video -> {video_path}")
        else:
            print("[capture-matrix] no video artifact found (continuing)")
        shutil.rmtree(video_tmp, ignore_errors=True)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in keywords)


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def _infer_site_type_from_url(url: str) -> str:
    """Infer website type from a source URL."""
    lower = url.lower()
    if _contains_any(
        lower,
        (
            "spotify",
            "apple.com/music",
            "tidal",
            "soundcloud",
            "youtube.com",
            "youtu.be",
            "youtube.",
            "bilibili",
            "b23.tv",
            "vimeo",
            "netflix",
            "twitch",
        ),
    ):
        return "media"
    if _contains_any(lower, ("airbnb", "booking", "expedia", "getyourguide", "viator", "travel", "trip")):
        return "travel"
    if _contains_any(lower, ("club", "meetup", "nonprofit", "society")):
        return "community"
    if _contains_any(lower, ("shop", "store", "amazon", "nike", "zara", "asos", "taobao", "tmall")):
        return "ecommerce"
    if _contains_any(lower, ("portfolio", "dribbble", "github.io", "behance")):
        return "portfolio"
    if _contains_any(lower, ("restaurant", "cafe", "menu", "nobu", "food", "bakery")):
        return "food"
    if _contains_any(lower, ("stripe", "linear", "notion", "hubspot", "saas", "agency", "slack", "atlassian")):
        return "corporate"
    if _contains_any(lower, ("event", "conference", "ted.com", "festival", "summit", "launch")):
        return "event"
    return "other"


def _infer_site_type_from_request(url: str, raw_instructions: str) -> str:
    url_guess = _infer_site_type_from_url(url)
    if url_guess != "other":
        return url_guess

    lower = raw_instructions.lower()
    keyword_map: dict[str, tuple[str, ...]] = {
        "media": ("music", "video", "podcast", "stream", "radio", "视频网站", "视频", "动画", "卡通", "儿歌"),
        "travel": ("travel", "trip", "hotel", "tour", "destination", "agency", "旅游", "旅行", "酒店"),
        "community": ("club", "society", "association", "team", "nonprofit", "school", "社团", "社区", "组织"),
        "ecommerce": ("shop", "store", "product", "buy", "sell", "marketplace", "商店", "商城", "电商"),
        "portfolio": ("portfolio", "resume", "personal", "freelance", "artist", "作品集", "个人主页"),
        "food": ("restaurant", "cafe", "food", "menu", "bakery", "bar", "餐厅", "咖啡", "菜单"),
        "corporate": ("company", "startup", "saas", "consulting", "agency", "企业", "公司", "官网"),
        "event": ("event", "conference", "festival", "launch", "concert", "活动", "大会", "发布会"),
    }
    for site_type, keywords in keyword_map.items():
        if _contains_any(lower, keywords):
            return site_type
    return "other"


def _collect_instruction_signals(raw_instructions: str) -> dict[str, bool]:
    lower = raw_instructions.lower()
    return {
        "dark": _contains_any(lower, ("dark", "dark mode", "暗色", "深色", "黑色")),
        "bright": _contains_any(lower, ("bright", "colorful", "鲜艳", "明亮", "彩色", "活泼")),
        "minimal": _contains_any(lower, ("minimal", "clean", "simple", "简洁", "极简", "简约")),
        "modern": _contains_any(lower, ("modern", "现代", "未来感")),
        "premium": _contains_any(lower, ("premium", "luxury", "高级", "高端", "精致")),
        "cute": _contains_any(lower, ("cute", "可爱", "萌", "童趣")),
        "kids": _contains_any(lower, ("kids", "kid", "children", "child", "小孩", "孩子", "儿童")),
        "cartoon": _contains_any(lower, ("cartoon", "卡通", "动画", "吉祥物", "mascot")),
        "mobile": _contains_any(lower, ("mobile", "phone", "手机", "移动端", "触屏")),
        "buttons": _contains_any(lower, ("button", "cta", "按钮", "更明显", "更突出")),
        "search": _contains_any(lower, ("search", "搜索")),
        "booking": _contains_any(lower, ("booking", "book now", "预订", "预约")),
        "map": _contains_any(lower, ("map", "地图")),
        "player": _contains_any(lower, ("player", "play", "播放器", "播放")),
    }


def _split_nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _count_design_constraint_categories(raw_instructions: str) -> int:
    lower = raw_instructions.lower()
    categories: dict[str, tuple[str, ...]] = {
        "color_theme": ("color", "theme", "palette", "dark", "light", "颜色", "配色", "暗色", "亮色", "鲜艳"),
        "typography": ("font", "typography", "字重", "字体", "字型", "排版"),
        "layout": ("layout", "grid", "hero", "sidebar", "card", "section", "布局", "栅格", "区块", "卡片", "导航"),
        "interaction": ("hover", "animation", "motion", "transition", "交互", "动效", "动画", "点击反馈"),
        "audience": ("audience", "tone", "kids", "family", "用户", "受众", "语气", "儿童", "家庭"),
        "responsive": ("responsive", "mobile", "desktop", "响应式", "移动端", "手机", "桌面"),
        "content": ("content", "feature", "category", "playlist", "gallery", "内容", "分类", "栏目", "推荐"),
        "cta": ("cta", "button", "register", "buy", "join", "按钮", "注册", "购买", "加入", "行动"),
    }
    return sum(1 for keywords in categories.values() if _contains_any(lower, keywords))


def _should_auto_expand_user_instructions(raw_instructions: str) -> tuple[bool, str]:
    text = raw_instructions.strip()
    if not text:
        return False, "no user instructions were provided"

    lines = _split_nonempty_lines(text)
    lower = text.lower()
    char_count = len(text)
    bullet_line_count = sum(1 for line in lines if re.match(r"^(?:[-*]|\d+[.)])\s+", line))
    heading_keywords = (
        "visual style",
        "page sections",
        "content details",
        "key features",
        "audience",
        "tone",
        "视觉风格",
        "页面区块",
        "内容细节",
        "交互",
        "目标用户",
        "受众",
    )
    heading_hits = sum(1 for keyword in heading_keywords if keyword in lower)
    constraint_categories = _count_design_constraint_categories(text)

    if heading_hits >= 2:
        return False, "detected structured prompt headings"
    if len(lines) >= 6 and bullet_line_count >= 3:
        return False, "detected a multi-line structured brief"
    if char_count >= 260 and constraint_categories >= 4:
        return False, "detected a long brief with many explicit design constraints"
    if char_count >= 180 and constraint_categories >= 5:
        return False, "detected enough explicit design requirements to use directly"

    if char_count <= 120:
        return True, "brief is short and likely underspecified"
    if len(lines) <= 2 and constraint_categories < 4:
        return True, "brief has too few explicit design constraints"
    if bullet_line_count == 0 and constraint_categories < 4:
        return True, "brief reads like a simple request rather than a full design prompt"

    return True, "brief is ambiguous, so defaulting to auto-expansion"


def _build_visual_style(profile: dict[str, Any], signals: dict[str, bool], site_type: str) -> dict[str, Any]:
    inspiration = list(profile["inspiration"])
    aesthetic = str(profile["default_aesthetic"])
    color_scheme = str(profile["default_color_scheme"])
    typography = str(profile["default_typography"])
    layout = str(profile["default_layout"])
    audience = str(profile["audience"])
    tone = str(profile["tone"])
    cta = str(profile["cta"])

    if signals["kids"] or signals["cartoon"]:
        aesthetic = (
            "a playful, safe, character-led interface that keeps the source site's browsing logic recognizable "
            "while making the overall experience feel more joyful and age-appropriate"
        )
        color_scheme = (
            "sunny yellow, coral, aqua, mint, and soft cream backgrounds with high-contrast action colors "
            "so the page feels vivid, cheerful, and easy for children to scan"
        )
        typography = (
            "rounded display lettering, large readable labels, and friendly interface copy that feels approachable "
            "for children without becoming hard to scan for adults"
        )
        layout = (
            "oversized card grid with soft corners, bold hero artwork, simplified category chips, and very obvious "
            "primary actions and touch targets"
        )
        audience = "children first, with parents or guardians still able to understand and trust the interface"
        tone = "joyful, safe, encouraging, and energetic"
        cta = "start watching fun, safe, age-appropriate content"
        if site_type == "media":
            inspiration = ["YouTube Kids", "PBS Kids", "Disney Junior"]

    if signals["dark"]:
        color_scheme = (
            "deep charcoal or graphite surfaces with vivid accent colors and strong contrast so the page feels "
            "cinematic without losing usability"
        )
    elif signals["bright"] and not (signals["kids"] or signals["cartoon"]):
        color_scheme = (
            "lively accent colors with stronger contrast than the source page, using clear section separation and "
            "high-energy highlights instead of muted tones"
        )

    if signals["minimal"]:
        layout = "a cleaner, more spacious layout with simplified chrome, more breathing room, and stronger block separation"

    if signals["modern"] and not (signals["kids"] or signals["cartoon"]):
        aesthetic = "a more contemporary version of the source experience with cleaner surfaces, sharper hierarchy, and fresher visual rhythm"

    if signals["premium"]:
        aesthetic = "a more polished, premium interpretation of the source page with tighter hierarchy and more deliberate visual restraint"

    return {
        "aesthetic": aesthetic,
        "color_scheme": color_scheme,
        "typography": typography,
        "layout": layout,
        "inspiration": inspiration,
        "audience": audience,
        "tone": tone,
        "cta": cta,
    }


def _build_sections(profile: dict[str, Any], signals: dict[str, bool], site_type: str) -> list[tuple[str, str]]:
    if site_type == "media" and (signals["kids"] or signals["cartoon"]):
        return [
            ("Hero / Featured Cartoon Banner", "Lead with the biggest child-friendly featured video, playlist, or mascot campaign"),
            ("Quick Category Navigation", "Expose obvious kid-friendly categories such as Cartoons, Songs, Animals, Learn, and Games"),
            ("Safe Picks / Trending for Kids", "Use large thumbnail cards for the most clickable age-appropriate content"),
            ("Learning, Songs, and Storytime Rows", "Separate educational, musical, and storytelling content into easy rails"),
            ("Character-Led Recommendations", "Use mascot-driven or illustrated recommendation blocks that feel playful and friendly"),
            ("Parent / Safety Utility Area", "Keep safe-mode, help, and guardian-facing links visible without dominating the page"),
        ]
    return list(profile["sections"])


def _build_content_details(profile: dict[str, Any], signals: dict[str, bool], site_type: str) -> list[str]:
    if site_type == "media" and (signals["kids"] or signals["cartoon"]):
        return [
            "Featured content — cartoons, sing-along videos, animal clips, beginner science explainers, craft videos, and storytime playlists",
            "Character system — more mascot illustrations, cartoon thumbnails, rounded avatars, and playful decorative accents around major modules",
            "Browse labels — simple, child-friendly labels such as Cartoons, Songs, Learn, Animals, Storytime, and Play",
            "Safety cues — safe-mode messaging, obvious trusted sections, and copy that feels friendly rather than overwhelming",
            "Card metadata — large titles, short supporting labels, and obvious duration/play cues that children can visually parse quickly",
        ]
    return list(profile["content_details"])


def _build_feature_list(profile: dict[str, Any], signals: dict[str, bool], site_type: str) -> list[str]:
    features = list(profile["features"])

    if signals["buttons"]:
        features.append("Make primary buttons, play triggers, and other key actions larger, higher-contrast, and more obvious at a glance")
    if signals["mobile"]:
        features.append("Prioritize mobile responsiveness with larger tap targets, simpler stacking, and fewer cramped controls")
    if signals["search"]:
        features.append("Keep search highly visible and easy to access from the first screen")
    if signals["booking"]:
        features.append("Make booking or reservation actions sticky, repeated, and visually dominant")
    if signals["map"]:
        features.append("Support location context with map-aware cues or address visibility")
    if signals["player"] and site_type == "media":
        features.append("Use clear play-state affordances and strong video-card interaction cues")

    if site_type == "media" and (signals["kids"] or signals["cartoon"]):
        features.extend(
            [
                "Use obvious category chips and simplified labels so children can browse without reading dense navigation",
                "Add playful hover/tap feedback, gentle motion, and friendly iconography that reinforces the child-focused direction",
            ]
        )

    return _dedupe_keep_order(features)


def _expand_user_instructions(
    raw_instructions: str,
    url: str,
    skill_root: Path,
) -> str:
    """
    Expand vague user instructions into a structured prompt-expander brief.
    """
    del skill_root  # Prompt-expander is now fully embedded in this script.

    site_type = _infer_site_type_from_request(url, raw_instructions)
    profile = SITE_TYPE_PROFILES.get(site_type, SITE_TYPE_PROFILES["other"])
    signals = _collect_instruction_signals(raw_instructions)
    visual_style = _build_visual_style(profile, signals, site_type)
    sections = _build_sections(profile, signals, site_type)
    content_details = _build_content_details(profile, signals, site_type)
    features = _build_feature_list(profile, signals, site_type)

    assumptions = [
        f"The source URL should remain recognizable as a {profile['display_name']} experience unless the user explicitly asks for a complete product-category change.",
        "The user provided a short brief, so defaults below are expanded from the built-in prompt-expander rules instead of being guessed ad hoc.",
        "The captured screenshot still defines the core information hierarchy, card density, and navigation purpose of the final page.",
    ]
    constraints = [
        f'Honor the user brief exactly: "{raw_instructions.strip()}"',
        "Preserve the recognizable structure and browsing logic of the captured source page while adapting styling and content emphasis.",
    ]
    if signals["kids"]:
        constraints.append("Shift the audience toward children and family-friendly browsing.")
    if signals["cartoon"]:
        constraints.append("Increase the presence of mascot-like, illustrated, or cartoon-driven visual elements.")
    if signals["bright"]:
        constraints.append("Use a brighter and more energetic palette than the default source styling.")
    if signals["buttons"]:
        constraints.append("Make primary buttons and major actions easier to notice and easier to tap.")
    if signals["mobile"]:
        constraints.append("Prioritize small-screen usability and touch-friendly spacing.")

    sections_text = "\n".join(
        f"{idx}. {title} — {description}" for idx, (title, description) in enumerate(sections, start=1)
    )
    content_text = "\n".join(f"{idx}. {item}" for idx, item in enumerate(content_details, start=1))
    features_text = "\n".join(f"- {item}" for item in features)
    assumptions_text = "\n".join(f"- {item}" for item in assumptions)
    constraints_text = "\n".join(f"- {item}" for item in _dedupe_keep_order(constraints))

    return textwrap.dedent(
        f"""\
**Prompt-expander output (auto-generated from a brief user request):**
**Inferred website type:** {profile["display_name"]}

**Assumptions:**
{assumptions_text}

**Extracted constraints:**
{constraints_text}

I want to create a {profile["display_name"]} webpage adapted from the referenced website capture.

**Visual Style:**
- Overall aesthetic: {visual_style["aesthetic"]}
- Color scheme: {visual_style["color_scheme"]}
- Typography: {visual_style["typography"]}
- Layout feel: {visual_style["layout"]}
- Inspiration: {", ".join(visual_style["inspiration"])}

**Page Sections:** (top to bottom)
{sections_text}

**Content Details:**
{content_text}

**Key Features & Interactions:**
{features_text}
- Responsive: mobile + desktop with preserved browsing hierarchy and comfortable tap targets

**Audience & Tone:**
- Target audience: {visual_style["audience"]}
- Emotional tone: {visual_style["tone"]}
- Call to action: {visual_style["cta"]}

**Source Adaptation Rules:**
- Preserve the recognizable information architecture, navigation purpose, and content density seen in the screenshot.
- Apply the user's requested style shift through palette, typography, iconography, imagery, labels, and CTA emphasis.
- Keep the final page coherent with the captured source instead of replacing the product category entirely.

---
"""
    ).strip()


def _format_direct_user_prompt(raw_instructions: str, url: str) -> str:
    site_type = _infer_site_type_from_request(url, raw_instructions)
    profile = SITE_TYPE_PROFILES.get(site_type, SITE_TYPE_PROFILES["other"])
    return textwrap.dedent(
        f"""\
**Prompt-expander output (direct use):**
**Inferred website type:** {profile["display_name"]}

**Decision:**
- The user brief already looks detailed enough, so use it directly instead of auto-expanding it.

**User provided detailed brief:**
{raw_instructions.strip()}

**Source Adaptation Rules:**
- Preserve the recognizable information architecture, navigation purpose, and content density seen in the screenshot.
- Respect the user's detailed instructions as the primary creative direction.
- Keep the final page coherent with the captured source instead of replacing the product category entirely.

---
"""
    ).strip()


def _build_replica_prompt(
    prompt_template: str,
    css_text: str,
    expanded_user_prompt: str = "",
) -> str:
    first_sentence = (
        "Recreate the referenced website into one complete HTML file with high visual fidelity."
    )
    out = prompt_template
    out = out.replace("[first_sentence]", first_sentence)
    out = out.replace("[css_text]", css_text)

    out = out.replace("[user_instructions]", expanded_user_prompt.strip())
    return out


def _handle_expanded_prompt_confirmation(
    expanded_user_prompt: str,
    expanded_prompt_path: Path,
    *,
    require_confirmation: bool,
    approved: bool,
) -> bool:
    if not expanded_user_prompt.strip():
        return True

    if approved:
        print(f"[prompt-expander] using pre-approved prepared prompt: {expanded_prompt_path}")
        return True

    if not require_confirmation:
        return True

    print(f"[prompt-expander] prepared prompt written to {expanded_prompt_path}")
    print("[prompt-expander] review the prepared prompt below before clone generation:\n")
    print(expanded_user_prompt)
    print("")

    if sys.stdin is not None and sys.stdin.isatty():
        try:
            reply = input("[prompt-expander] Continue with this prepared prompt? [y/N]: ").strip().lower()
        except EOFError:
            reply = ""
        if reply in {"y", "yes"}:
            print("[prompt-expander] confirmed. Continuing with capture and clone generation.")
            return True
        print("[prompt-expander] cancelled. Update the instructions and rerun when ready.")
        return False

    print(
        "[prompt-expander] non-interactive mode detected. Review the expanded prompt file, "
        "then rerun with --approve-expanded-prompt to continue."
    )
    return False


def _extract_html(raw_text: str) -> str:
    text = str(raw_text or "").strip()
    if not text:
        return ""

    fence_re = re.compile(r"```(?:html)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
    for m in fence_re.finditer(text):
        body = m.group(1).strip()
        if "<html" in body.lower() or "<!doctype" in body.lower():
            return body

    lower = text.lower()
    start = lower.find("<!doctype")
    if start == -1:
        start = lower.find("<html")
    end = lower.rfind("</html>")
    if start != -1 and end != -1 and end > start:
        return text[start : end + len("</html>")].strip()

    return text


def _usage_to_dict(usage_obj: Any) -> dict[str, Optional[int]]:
    if usage_obj is None:
        return {"prompt_tokens": None, "output_tokens": None, "total_tokens": None}

    def _get(name: str) -> Optional[int]:
        v = getattr(usage_obj, name, None)
        if isinstance(v, int):
            return v
        return None

    prompt = _get("prompt_token_count") or _get("promptTokenCount")
    output = _get("candidates_token_count") or _get("candidatesTokenCount") or _get("output_token_count")
    total = _get("total_token_count") or _get("totalTokenCount")
    return {"prompt_tokens": prompt, "output_tokens": output, "total_tokens": total}


def _response_to_jsonable(resp: Any) -> dict[str, Any]:
    for meth in ("model_dump", "to_dict"):
        fn = getattr(resp, meth, None)
        if callable(fn):
            try:
                data = fn()
                if isinstance(data, dict):
                    return data
            except Exception:
                continue
    return {"text": str(getattr(resp, "text", "") or "")}


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"__bytes_b64__": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    return str(value)


def _replica_forge(
    *,
    api_key: str,
    model: str,
    max_output_tokens: int,
    temperature: float,
    system_prompt: str,
    prompt_text: str,
    snapshot_path: Path,
) -> tuple[str, dict[str, Optional[int]], dict[str, Any]]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    image_bytes = snapshot_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    contents = [
        types.Content(
            role="user",
            parts=[image_part, types.Part(text=prompt_text)],
        )
    ]
    cfg_kwargs: dict[str, Any] = {
        "max_output_tokens": int(max_output_tokens),
        "temperature": float(temperature),
    }
    if str(system_prompt).strip():
        cfg_kwargs["system_instruction"] = str(system_prompt).strip()

    config = types.GenerateContentConfig(**cfg_kwargs)
    response = client.models.generate_content(model=model, contents=contents, config=config)
    raw_text = str(getattr(response, "text", "") or "").strip()
    if not raw_text:
        raw_text = json.dumps(_response_to_jsonable(response), ensure_ascii=False, indent=2)
    usage_obj = getattr(response, "usage_metadata", None) or getattr(response, "usageMetadata", None)
    usage = _usage_to_dict(usage_obj)
    return raw_text, usage, _to_jsonable(_response_to_jsonable(response))


def _write_legacy_aliases(
    *,
    out_dir: Path,
    snapshot_path: Path,
    styles_path: Path,
    replica_path: Path,
    video_path: Optional[Path],
) -> None:
    # Keep compatibility with environments that expect prior filenames.
    shutil.copy2(snapshot_path, out_dir / "page_stitched.png")
    shutil.copy2(styles_path, out_dir / "page_html_styles.css")
    shutil.copy2(replica_path, out_dir / "cloned_site.html")

    if video_path is not None and video_path.exists():
        shutil.copy2(video_path, out_dir / "page_scroll.webm")

    lines = [
        f"  - screenshot: {(out_dir / 'page_stitched.png').as_posix()}",
        f"  - css: {(out_dir / 'page_html_styles.css').as_posix()}",
    ]
    if (out_dir / "page_scroll.webm").exists():
        lines.append(f"  - video: {(out_dir / 'page_scroll.webm').as_posix()}")
    _write_text(out_dir / "output_manifest.txt", "\n".join(lines) + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a standalone web cloning pipeline (capture-matrix + replica-forge)."
    )
    parser.add_argument("url", nargs="?", help="Target URL to clone.")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: ./outputs/replica_run_<ts>).")
    parser.add_argument("--config", default=None, help="Config path (default: bundled assets/cloneit.skill.toml).")
    parser.add_argument("--model", default=None, help="Override Gemini model id.")
    parser.add_argument("--thinking-level", choices=["low", "high"], default=None, help="Metadata only for run manifest.")
    parser.add_argument("--max-output-tokens", type=int, default=None, help="Override max output tokens.")
    parser.add_argument("--temperature", type=float, default=None, help="Override sampling temperature.")
    parser.add_argument("--include-video", action=argparse.BooleanOptionalAction, default=None, help="Capture scroll video.")
    parser.add_argument("--headed", action=argparse.BooleanOptionalAction, default=None, help="Run browser headed.")
    parser.add_argument("--instructions", default=None, help="Optional user instructions (short/vague OK). Will be expanded using prompt-expander reference.")
    parser.add_argument(
        "--confirm-expanded-prompt",
        action="store_true",
        help="Pause after generating the expanded prompt and require explicit confirmation before clone generation.",
    )
    parser.add_argument(
        "--approve-expanded-prompt",
        action="store_true",
        help="Continue using a previously reviewed expanded prompt without prompting again.",
    )
    parser.add_argument(
        "--force-rebuild-runtime",
        action="store_true",
        help="Delete the managed .runtime and rebuild it from scratch before running.",
    )
    parser.add_argument("--bootstrap-only", action="store_true", help="Install/verify runtime only; do not execute clone.")
    parser.add_argument("--verify-runtime", action="store_true", help="Verify runtime is available before running.")
    parser.add_argument("--skip-bootstrap", action="store_true", help="Run directly in current Python without runtime bootstrap.")
    return parser


def _run_pipeline(args: argparse.Namespace, *, skill_root: Path, cfg_path: Path) -> int:
    cfg = _load_config(cfg_path)
    if args.url is None:
        raise RuntimeError("url is required for pipeline execution.")

    out_dir = Path(args.out_dir).expanduser() if args.out_dir else _default_out_dir()
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    artifact_manifest = str(_deep_get(cfg, "artifact_map.manifest", "run_manifest.txt") or "run_manifest.txt")
    artifact_snapshot = str(_deep_get(cfg, "artifact_map.snapshot", "source_snapshot.png") or "source_snapshot.png")
    artifact_styles = str(_deep_get(cfg, "artifact_map.styles", "source_styles.css") or "source_styles.css")
    artifact_video = str(_deep_get(cfg, "artifact_map.video", "source_scroll.webm") or "source_scroll.webm")
    artifact_replica = str(_deep_get(cfg, "artifact_map.replica", "web_replica.html") or "web_replica.html")
    write_legacy_aliases = bool(_deep_get(cfg, "artifact_map.legacy_aliases", True))

    manifest_path = out_dir / artifact_manifest
    snapshot_path = out_dir / artifact_snapshot
    styles_path = out_dir / artifact_styles
    video_path = out_dir / artifact_video
    replica_path = out_dir / artifact_replica
    replica_prompt_path = out_dir / (Path(artifact_replica).stem + ".prompt.txt")
    expanded_prompt_path = out_dir / "expanded_user_prompt.txt"
    replica_raw_path = out_dir / (Path(artifact_replica).stem + ".raw.txt")
    replica_json_path = out_dir / (Path(artifact_replica).stem + ".response.json")

    viewport_w = int(_deep_get(cfg, "capture_matrix.viewport_width", 1920))
    viewport_h = int(_deep_get(cfg, "capture_matrix.viewport_height", 1080))
    wait_ms = int(_deep_get(cfg, "capture_matrix.initial_wait_ms", 1800))
    scroll_step_px = int(_deep_get(cfg, "capture_matrix.scroll_step_px", 720))
    scroll_pause_ms = int(_deep_get(cfg, "capture_matrix.scroll_pause_ms", 140))
    scroll_cap_px = int(_deep_get(cfg, "capture_matrix.scroll_cap_px", 40000))
    include_video_cfg = bool(_deep_get(cfg, "capture_matrix.include_video", True))
    include_video = include_video_cfg if args.include_video is None else bool(args.include_video)
    headed_cfg = bool(_deep_get(cfg, "capture_matrix.headed", False))
    headed = headed_cfg if args.headed is None else bool(args.headed)

    model = str(args.model or _deep_get(cfg, "replica_forge.gemini_model", "gemini-3.1-pro-preview"))
    thinking_level = str(args.thinking_level or _deep_get(cfg, "replica_forge.thinking_level", "high"))
    max_output_tokens = int(args.max_output_tokens or _deep_get(cfg, "replica_forge.max_output_tokens", 100000))
    temperature = float(args.temperature if args.temperature is not None else _deep_get(cfg, "replica_forge.temperature", 1.0))

    system_prompt = _resolve_prompt_text(
        cfg,
        cfg_path=cfg_path,
        inline_key="replica_forge.system_prompt",
        file_key="replica_forge.system_prompt_file",
    )
    prompt_template = _resolve_prompt_text(
        cfg,
        cfg_path=cfg_path,
        inline_key="replica_forge.prompt_template",
        file_key="replica_forge.prompt_template_file",
    )
    if not prompt_template.strip():
        raise RuntimeError("replica_forge prompt template is empty; check config and bundled prompt files.")

    api_key = _discover_gemini_key(skill_root)

    user_instructions = str(args.instructions or _deep_get(cfg, "replica_forge.user_instructions", "") or "").strip()
    expanded_user_prompt = ""
    prompt_expander_meta: dict[str, Any] = {}
    if user_instructions:
        inferred_site_type = _infer_site_type_from_request(args.url, user_instructions)
        should_expand, decision_reason = _should_auto_expand_user_instructions(user_instructions)
        print(f"[web-replica] user instructions: {user_instructions[:80]}{'...' if len(user_instructions) > 80 else ''}")
        print(f"[prompt-expander] inferred site type: {inferred_site_type}")
        print(
            f"[prompt-expander] decision: {'auto-expand' if should_expand else 'direct-use'} "
            f"({decision_reason})"
        )
        if should_expand:
            expanded_user_prompt = _expand_user_instructions(user_instructions, args.url, skill_root)
        else:
            expanded_user_prompt = _format_direct_user_prompt(user_instructions, args.url)
        _write_text(expanded_prompt_path, expanded_user_prompt + "\n")
        prompt_expander_meta = {
            "decision": "expanded" if should_expand else "direct_use",
            "reason": decision_reason,
            "inferred_site_type": inferred_site_type,
            "user_instructions": user_instructions,
            "prepared_prompt_path": str(expanded_prompt_path),
        }
        if should_expand:
            if not _handle_expanded_prompt_confirmation(
                expanded_user_prompt,
                expanded_prompt_path,
                require_confirmation=bool(args.confirm_expanded_prompt),
                approved=bool(args.approve_expanded_prompt),
            ):
                return 0
        elif args.confirm_expanded_prompt:
            print("[prompt-expander] user instructions already look detailed enough; skipping expansion confirmation.")
    elif args.confirm_expanded_prompt or args.approve_expanded_prompt:
        print("[prompt-expander] confirmation flags ignored because no user instructions were provided.")

    print(f"[web-replica] skill_root={skill_root}")
    print(f"[web-replica] config={cfg_path}")
    print(f"[web-replica] out_dir={out_dir}")
    print(f"[web-replica] url={args.url}")
    print(f"[web-replica] model={model} thinking_level={thinking_level} max_output_tokens={max_output_tokens}")
    print("[web-replica] stages=capture-matrix -> replica-forge -> artifact-sync")

    t0 = dt.datetime.now()
    _capture_matrix(
        url=args.url,
        snapshot_path=snapshot_path,
        styles_path=styles_path,
        video_path=(video_path if include_video else None),
        viewport_w=viewport_w,
        viewport_h=viewport_h,
        wait_ms=wait_ms,
        scroll_step_px=scroll_step_px,
        scroll_pause_ms=scroll_pause_ms,
        scroll_cap_px=scroll_cap_px,
        headed=headed,
    )

    css_text = _read_text(styles_path)
    prompt_text = _build_replica_prompt(
        prompt_template,
        css_text,
        expanded_user_prompt=expanded_user_prompt,
    )
    _write_text(replica_prompt_path, prompt_text)

    print("[replica-forge] generating HTML with Gemini")
    FALLBACK_MODEL = "gemini-3.0-pro-preview"
    _forge_attempts = [(model, 1), (model, 2), (FALLBACK_MODEL, 1)]
    raw_response_text = usage = response_jsonable = None
    last_exc: Optional[Exception] = None
    for _attempt_model, _attempt_num in _forge_attempts:
        if _attempt_model == model and _attempt_num > 1:
            print(f"[replica-forge] retry {_attempt_num}/2 with model={_attempt_model}")
        elif _attempt_model != model:
            print(f"[replica-forge] primary model exhausted — falling back to model={_attempt_model}")
        else:
            print(f"[replica-forge] attempt 1/2 with model={_attempt_model}")
        try:
            raw_response_text, usage, response_jsonable = _replica_forge(
                api_key=api_key,
                model=_attempt_model,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                system_prompt=system_prompt,
                prompt_text=prompt_text,
                snapshot_path=snapshot_path,
            )
            last_exc = None
            break
        except Exception as exc:
            print(f"[replica-forge] attempt failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            last_exc = exc
    if last_exc is not None:
        raise RuntimeError(
            f"All replica-forge attempts failed. Last error: {type(last_exc).__name__}: {last_exc}"
        ) from last_exc
    _write_text(replica_raw_path, raw_response_text)
    _write_text(replica_json_path, json.dumps(response_jsonable, ensure_ascii=False, indent=2))

    html_text = _extract_html(raw_response_text)
    if not html_text.strip():
        raise RuntimeError("Gemini response did not contain clone HTML.")
    _write_text(replica_path, html_text)

    if write_legacy_aliases:
        _write_legacy_aliases(
            out_dir=out_dir,
            snapshot_path=snapshot_path,
            styles_path=styles_path,
            replica_path=replica_path,
            video_path=(video_path if include_video else None),
        )

    t1 = dt.datetime.now()
    elapsed_s = (t1 - t0).total_seconds()
    manifest = {
        "schema": "web-replica-run/v1",
        "created_at": t1.isoformat(),
        "elapsed_seconds": elapsed_s,
        "source_url": args.url,
        "stages": ["capture-matrix", "replica-forge", "artifact-sync"],
        "config_path": str(cfg_path),
        "artifacts": {
            "manifest": str(manifest_path),
            "snapshot": str(snapshot_path),
            "styles": str(styles_path),
            "video": str(video_path if include_video else ""),
            "replica": str(replica_path),
            "replica_prompt": str(replica_prompt_path),
            "expanded_user_prompt": str(expanded_prompt_path if expanded_user_prompt else ""),
            "replica_raw": str(replica_raw_path),
            "replica_response_json": str(replica_json_path),
        },
        "gemini": {
            "model": model,
            "thinking_level": thinking_level,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "usage_tokens": usage,
        },
        "prompt_expander": prompt_expander_meta,
        "legacy_aliases_written": bool(write_legacy_aliases),
    }
    _write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print("[artifact-sync] completed")
    print(f"[artifact-sync] manifest={manifest_path}")
    print(f"[artifact-sync] snapshot={snapshot_path}")
    print(f"[artifact-sync] styles={styles_path}")
    if include_video:
        print(f"[artifact-sync] video={video_path}")
    print(f"[artifact-sync] replica={replica_path}")
    print(
        f"[artifact-sync] usage_tokens prompt={usage.get('prompt_tokens')} output={usage.get('output_tokens')} total={usage.get('total_tokens')}"
    )
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    skill_root = script_path.parent.parent
    cfg_path = _resolve_config_path(args.config, skill_root)
    active_venv = str(os.getenv("VIRTUAL_ENV", "")).strip()
    if os.getenv(RUNTIME_ENV) == "1" or _using_managed_runtime_python(skill_root):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_runtime_browser_dir(skill_root / ".runtime").resolve())

    if os.getenv(RUNTIME_ENV) != "1" and not args.skip_bootstrap:
        if active_venv:
            print(
                "[bootstrap] detected an active virtualenv, but using isolated skill runtime at .runtime/venv for consistency"
            )
        cfg = _load_config(cfg_path)
        venv_python = _ensure_runtime(skill_root, cfg, force_rebuild=args.force_rebuild_runtime)
        if args.bootstrap_only:
            print("[bootstrap] runtime ready")
            return 0
        cmd = [str(venv_python), str(script_path), *sys.argv[1:]]
        env = _managed_runtime_env(skill_root, base_env=os.environ.copy())
        env[RUNTIME_ENV] = "1"
        print(f"[bootstrap] re-executing in managed runtime: {_cmd_as_str(cmd)}")
        proc = subprocess.run(cmd, env=env)
        return int(proc.returncode)

    if args.bootstrap_only:
        print("[bootstrap] already inside runtime")
        return 0

    if args.verify_runtime:
        missing = []
        if importlib.util.find_spec("google.genai") is None:
            missing.append("google.genai")
        if importlib.util.find_spec("playwright.sync_api") is None:
            missing.append("playwright.sync_api")
        if missing:
            raise RuntimeError(f"runtime verification failed, missing imports: {', '.join(missing)}")
        print("[runtime] import verification passed")
        if args.url is None:
            return 0

    if args.url is None:
        parser.error("url is required unless --bootstrap-only or --verify-runtime")

    return _run_pipeline(args, skill_root=skill_root, cfg_path=cfg_path)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[error] {type(exc).__name__}: {exc}", file=sys.stderr)
        _print_error_hint(exc)
        tb = traceback.format_exc()
        if tb:
            print(tb, file=sys.stderr)
        raise SystemExit(1)
