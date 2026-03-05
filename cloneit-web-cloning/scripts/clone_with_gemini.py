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
import tomllib
import traceback
import venv
from pathlib import Path
from typing import Any, Optional

RUNTIME_ENV = "WEB_REPLICA_RUNTIME_ACTIVE"


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


def _cmd_as_str(cmd: list[str]) -> str:
    return " ".join(shlex.quote(str(p)) for p in cmd)


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


def _ensure_runtime(skill_root: Path, cfg: dict[str, Any]) -> Path:
    runtime_dir = skill_root / ".runtime"
    venv_dir = runtime_dir / "venv"
    venv_python = _venv_python_path(venv_dir)
    requirements = skill_root / "assets" / "requirements.txt"
    package_install_timeout_s = int(_deep_get(cfg, "runtime.package_install_timeout_seconds", 900))
    browser_install_timeout_s = int(_deep_get(cfg, "runtime.browser_install_timeout_seconds", 1200))
    pip_network_timeout_s = int(_deep_get(cfg, "runtime.pip_network_timeout_seconds", 45))
    pip_retries = int(_deep_get(cfg, "runtime.pip_retries", 2))

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
    probe = _run_cmd([str(venv_python), "-c", check_code], check=False)
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
                stream=True,
                timeout_s=package_install_timeout_s,
            )
            _run_cmd(
                [str(venv_python), "-m", "pip", "install", "-r", str(requirements), *pip_common],
                stream=True,
                timeout_s=package_install_timeout_s,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                "Python package bootstrap failed. Check network access to PyPI and retry, "
                "or preinstall dependencies from assets/requirements.txt."
            ) from exc

    install_playwright = bool(_deep_get(cfg, "runtime.install_playwright", True))
    if install_playwright:
        print("[bootstrap] ensuring Chromium is installed for Playwright (streaming logs)")
        try:
            _run_cmd(
                [str(venv_python), "-m", "playwright", "install", "chromium"],
                stream=True,
                timeout_s=browser_install_timeout_s,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                "Playwright browser bootstrap failed. Check network/system dependencies, "
                "then retry `--bootstrap-only`."
            ) from exc

    verify_browser = bool(_deep_get(cfg, "runtime.verify_browser_launch", True))
    if verify_browser:
        browser_probe = (
            "from playwright.sync_api import sync_playwright\n"
            "with sync_playwright() as p:\n"
            "  b=p.chromium.launch(headless=True)\n"
            "  page=b.new_page()\n"
            "  page.goto('about:blank')\n"
            "  b.close()\n"
            "print('browser-ok')\n"
        )
        _run_cmd([str(venv_python), "-c", browser_probe])
        print("[bootstrap] browser launch verification passed")

    # Final package probe after install.
    _run_cmd([str(venv_python), "-c", check_code])
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
        browser = p.chromium.launch(headless=not headed)
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


def _build_replica_prompt(prompt_template: str, css_text: str) -> str:
    first_sentence = (
        "Recreate the referenced website into one complete HTML file with high visual fidelity."
    )
    out = prompt_template
    out = out.replace("[first_sentence]", first_sentence)
    out = out.replace("[css_text]", css_text)
    return out


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
    prompt_text = _build_replica_prompt(prompt_template, css_text)
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

    if os.getenv(RUNTIME_ENV) != "1" and not args.skip_bootstrap:
        if active_venv:
            print(
                "[bootstrap] detected an active virtualenv, but using isolated skill runtime at .runtime/venv for consistency"
            )
        cfg = _load_config(cfg_path)
        venv_python = _ensure_runtime(skill_root, cfg)
        if args.bootstrap_only:
            print("[bootstrap] runtime ready")
            return 0
        cmd = [str(venv_python), str(script_path), *sys.argv[1:]]
        env = os.environ.copy()
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
        tb = traceback.format_exc()
        if tb:
            print(tb, file=sys.stderr)
        raise SystemExit(1)
