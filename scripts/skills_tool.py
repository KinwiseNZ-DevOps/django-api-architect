#!/usr/bin/env python3
"""Validate skills and keep the README catalogue in sync. Stdlib only.

  python scripts/skills_tool.py validate     # exit 1 on any problem
  python scripts/skills_tool.py catalogue    # rewrite README catalogue block
  python scripts/skills_tool.py check        # validate + fail if catalogue is stale

Dashes are always checked (except in reference-content/, which holds raw source material). Ship checks (placeholders, leftover scaffolding)
run once skills/example-skill has been deleted.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
README = ROOT / "README.md"
EVALS = ROOT / "evals" / "cases.jsonl"
AGENT_SOURCES = ROOT / "resources" / "agents"
BEGIN, END = "<!-- catalogue:begin -->", "<!-- catalogue:end -->"
BADGE_RE = re.compile(r"(badge/agent_skills-)(\d+|<N>)(-)")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)")
MAX_BODY_LINES, MAX_DESC, MAX_NAME, MIN_EVALS = 500, 1024, 64, 3
BANNED_DASHES = (chr(0x2013), chr(0x2014))
PLACEHOLDER_RE = re.compile(r"<([A-Za-z][^<>\n]*)>")
HTML_TAGS = {"details", "summary", "div", "br", "p", "a", "img", "kbd", "sub", "sup"}
PLACEHOLDER_FILES = ("README.md", "LICENSE", "AGENTS.md", "evals/cases.jsonl")


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    fm, key, folded = {}, None, False
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if top and not line.startswith(" "):
            key, val = top.group(1), top.group(2).strip()
            folded = val in (">", "|")
            fm[key] = "" if folded else val.strip("\"'")
        elif key and line.startswith(" "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm, m.group(2)


def skill_dirs():
    if not SKILLS.is_dir():
        sys.exit("ERROR: skills/ directory not found")
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def validate():
    errors = []
    names = {p.name for p in skill_dirs()}
    for d in skill_dirs():
        f = d / "SKILL.md"
        if not f.exists():
            errors.append(f"{d.name}: missing SKILL.md")
            continue
        fm, body = parse(f)
        if fm is None:
            errors.append(f"{d.name}: no frontmatter")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != d.name:
            errors.append(f"{d.name}: name '{name}' != folder")
        if not NAME_RE.match(name) or len(name) > MAX_NAME:
            errors.append(f"{d.name}: invalid name")
        if not desc or len(desc) > MAX_DESC:
            errors.append(f"{d.name}: description empty or >{MAX_DESC} chars ({len(desc)})")
        if "<" in desc or ">" in desc:
            errors.append(f"{d.name}: description contains angle brackets")
        if not re.search(r"\bUse\b|\bUse when\b", desc):
            errors.append(f"{d.name}: description lacks a 'Use ...' trigger")
        lines = len(body.splitlines())
        if lines > MAX_BODY_LINES:
            errors.append(f"{d.name}: body {lines} lines > {MAX_BODY_LINES}")
        for md in [f, *d.rglob("references/*.md")]:
            for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
                path = target.split("#")[0]
                if path and not (md.parent / path).resolve().exists():
                    errors.append(f"{md.relative_to(ROOT)}: broken link {target}")
    if EVALS.exists():
        counts = {n: 0 for n in names}
        for i, line in enumerate(EVALS.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"evals/cases.jsonl:{i}: invalid JSON")
                continue
            for s in case.get("skills", []):
                if s in counts:
                    counts[s] += 1
                else:
                    errors.append(f"evals/cases.jsonl:{i}: unknown skill {s}")
            if not case.get("query") or not case.get("expected_behavior"):
                errors.append(f"evals/cases.jsonl:{i}: needs query and expected_behavior")
        for n, c in counts.items():
            if c < MIN_EVALS:
                errors.append(f"{n}: {c} eval cases < {MIN_EVALS}")
    else:
        errors.append("evals/cases.jsonl missing")
    return errors


def validate_agent_sources():
    errors = []
    scopes = {
        "shared": lambda stem: stem.startswith("shared-"),
        "skill-specific": lambda stem: any(stem.startswith(f"{path.name}-") for path in skill_dirs()),
    }
    if not AGENT_SOURCES.is_dir():
        return errors
    for host in sorted(path for path in AGENT_SOURCES.iterdir() if path.is_dir()):
        for scope, matches in scopes.items():
            folder = host / scope
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob("*.md")):
                stem = path.name[:-len(".agent.md")] if path.name.endswith(".agent.md") else path.stem
                if not matches(stem):
                    expected = "shared-<role>" if scope == "shared" else "<owning-skill-name>-<role>"
                    errors.append(f"{path.relative_to(ROOT)}: name must use {expected}")
    return errors


def dashes():
    errors = []
    for p in sorted(ROOT.rglob("*")):
        parts = p.relative_to(ROOT).parts
        if not p.is_file() or ".git" in parts or parts[0] == "reference-content":
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            if any(d in line for d in BANNED_DASHES):
                errors.append(f"{p.relative_to(ROOT)}:{i}: em or en dash (use a hyphen)")
    return errors


def strip_terms():
    f = ROOT / "reference-content" / "strip-terms.txt"
    if not f.exists():
        return []
    terms = [l.strip().lower() for l in f.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.lstrip().startswith("#")]
    if not terms:
        return []
    targets = [ROOT / n for n in ("README.md", "AGENTS.md")]
    for folder in ("skills", "evals", "reference-content/sources"):
        d = ROOT / folder
        if d.is_dir():
            targets += [x for x in d.rglob("*") if x.is_file()]
    errors = []
    for x in targets:
        try:
            lines = x.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for i, line in enumerate(lines, 1):
            low = line.lower()
            for term in terms:
                if term in low:
                    errors.append(f"{x.relative_to(ROOT)}:{i}: project-specific term '{term}' (see strip-terms.txt)")
    return errors


def ship_checks():
    if (SKILLS / "example-skill").exists():
        return [], True
    errors = []
    for rel in PLACEHOLDER_FILES:
        f = ROOT / rel
        if not f.exists():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in PLACEHOLDER_RE.finditer(line):
                inner = m.group(1)
                first = inner.split()[0].lower().rstrip("/")
                if first in HTML_TAGS:
                    continue
                if " " in inner or inner[0].isupper():
                    errors.append(f"{rel}:{i}: leftover placeholder <{inner}>")
    for leftover in ("SETUP.md", "templates", "reference-content"):
        if (ROOT / leftover).exists():
            errors.append(f"{leftover}: setup scaffolding still present (delete before shipping)")
    return errors, False


def build_catalogue():
    rows = ["| Skill | Purpose |", "|---|---|"]
    for d in skill_dirs():
        fm, _ = parse(d / "SKILL.md")
        desc = fm["description"]
        first = re.split(r"(?<=\.)\s", desc, maxsplit=1)[0]
        rows.append(f"| [`{d.name}`](skills/{d.name}/SKILL.md) | {first} |")
    return "\n".join(rows)


def catalogue(write):
    text = README.read_text(encoding="utf-8")
    pat = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    new = f"{BEGIN}\n{build_catalogue()}\n{END}"
    if not pat.search(text):
        return ["README.md: catalogue markers missing"]
    updated = pat.sub(lambda _: new, text)
    updated = BADGE_RE.sub(lambda m: f"{m.group(1)}{len(skill_dirs())}{m.group(3)}", updated)
    if updated == text:
        return []
    if write:
        README.write_text(updated, encoding="utf-8")
        return []
    return ["README.md: catalogue stale; run `python scripts/skills_tool.py catalogue`"]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    errors = []
    skipped = False
    if cmd in ("validate", "check"):
        errors += validate()
        errors += validate_agent_sources()
        errors += dashes()
        errors += strip_terms()
        ship_errors, skipped = ship_checks()
        errors += ship_errors
    if cmd == "catalogue":
        errors += catalogue(write=True)
    if cmd == "check":
        errors += catalogue(write=False)
    if cmd not in ("validate", "catalogue", "check"):
        print(__doc__)
        return 2
    for e in errors:
        print("ERROR:", e)
    note = " [ship checks skipped: example-skill present]" if skipped else ""
    print(f"{cmd}: {'FAILED' if errors else 'ok'} ({len(skill_dirs())} skills){note}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
