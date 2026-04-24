from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
MYST_YML = ROOT / "myst.yml"

HEADING_CHARS = {"=": 1, "-": 2, "~": 3, "*": 4, "^": 5, "#": 6}


def convert_inline(text: str) -> str:
    text = re.sub(r"``([^`]+)``", r"`\1`", text)
    text = re.sub(r"`([^`<>]+) <([^>]+)>`_", r"[\1](\2)", text)
    return text


def is_heading_underline(line: str) -> bool:
    s = line.strip()
    return bool(s) and len(set(s)) == 1 and s[0] in HEADING_CHARS and len(s) >= 3


def to_heading(title: str, marker: str) -> str:
    level = HEADING_CHARS.get(marker, 2)
    return f"{'#' * level} {convert_inline(title.strip())}"


def convert_directive(lines: list[str], i: int) -> tuple[list[str], int]:
    line = lines[i]
    m = re.match(r"^(\s*)\.\.\s+([\w:-]+)::\s*(.*)$", line)
    if not m:
        return [convert_inline(line)], i + 1

    base_indent = m.group(1)
    name = m.group(2)
    arg = m.group(3).rstrip()

    block: list[str] = []
    j = i + 1
    body_prefix = f"{base_indent}   "

    # Capture indented content belonging to the directive.
    while j < len(lines):
        current = lines[j]
        if current.startswith(body_prefix):
            block.append(current[len(body_prefix):])
            j += 1
            continue
        if current.strip() == "":
            # Keep blank lines inside directive body if followed by more indented lines.
            k = j + 1
            if k < len(lines) and lines[k].startswith(body_prefix):
                block.append("")
                j += 1
                continue
        break

    # Merge continued signature lines ending with backslash.
    if arg.endswith("\\"):
        arg = arg[:-1].rstrip()
        while block and block[0].strip():
            arg += " " + block.pop(0).rstrip("\\").strip()
            if not block or not block[0].strip() or not block[0].strip().endswith("\\"):
                break

    # MyST fenced directives for common admonitions and C++ domain directives.
    if name in {"warning", "note", "important"}:
        out = [f"{base_indent}```{{{name}}}"]
        if arg:
            out.append(f"{base_indent}{convert_inline(arg)}")
        out.extend(f"{base_indent}{convert_inline(x)}" for x in block)
        out.append(f"{base_indent}```")
        return out, j

    if name.startswith("cpp:"):
        dname = name.replace(":", ":", 1)
        out = [f"{base_indent}```{{{dname}}} {convert_inline(arg)}".rstrip()]
        out.extend(f"{base_indent}{convert_inline(x)}" for x in block)
        out.append(f"{base_indent}```")
        return out, j

    if name in {"code-block", "code"}:
        lang = arg or "text"
        out = [f"{base_indent}```{lang}"]
        out.extend(f"{base_indent}{x}" for x in block)
        out.append(f"{base_indent}```")
        return out, j

    if name == "parsed-literal":
        out = [f"{base_indent}```text"]
        out.extend(f"{base_indent}{x}" for x in block)
        out.append(f"{base_indent}```")
        return out, j

    # Unknown directives: preserve via eval-rst so content still renders.
    out = [f"{base_indent}```{{eval-rst}}", f"{base_indent}{line.lstrip()}"]
    for b in block:
        out.append(f"{base_indent}   {b}" if b else "")
    out.append(f"{base_indent}```")
    return out, j


def is_grid_or_simple_table_line(line: str) -> bool:
    s = line.rstrip()
    if not s:
        return False
    return bool(re.match(r"^[+=|\-].*[+=|\-]$", s)) and ("|" in s or "+" in s or "=" in s)


def convert_table_block(lines: list[str], i: int) -> tuple[list[str], int]:
    block: list[str] = []
    j = i
    while j < len(lines):
        candidate = lines[j]
        if candidate.strip() == "":
            break
        if is_grid_or_simple_table_line(candidate) or candidate.startswith(" "):
            block.append(candidate)
            j += 1
            continue
        break

    if not block:
        return [lines[i]], i + 1

    out = ["```{eval-rst}"]
    out.extend(block)
    out.append("```")
    return out, j


def convert_rst_to_myst(text: str) -> str:
    src = text.splitlines()
    out: list[str] = []
    i = 0

    while i < len(src):
        line = src[i]

        # Overline + title + underline style.
        if i + 2 < len(src) and is_heading_underline(line) and src[i + 1].strip() and is_heading_underline(src[i + 2]):
            up = line.strip()[0]
            low = src[i + 2].strip()[0]
            if up == low:
                out.append(f"# {convert_inline(src[i + 1].strip())}")
                i += 3
                continue

        # Title + underline style.
        if i + 1 < len(src) and src[i].strip() and is_heading_underline(src[i + 1]):
            out.append(to_heading(src[i], src[i + 1].strip()[0]))
            i += 2
            continue

        if re.match(r"^\s*\.\.\s+[\w:-]+::", line):
            converted, i = convert_directive(src, i)
            out.extend(converted)
            continue

        if is_grid_or_simple_table_line(line):
            converted, i = convert_table_block(src, i)
            out.extend(converted)
            continue

        # Horizontal separators made of many dashes.
        if re.fullmatch(r"\s*-{6,}\s*", line):
            out.append("---")
            i += 1
            continue

        out.append(convert_inline(line))
        i += 1

    # Collapse excessive blank lines.
    result: list[str] = []
    blank_count = 0
    for line in out:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                result.append("")
        else:
            blank_count = 0
            result.append(line.rstrip())

    return "\n".join(result).rstrip() + "\n"


def main() -> None:
    rst_files = sorted(CONTENT.glob("*.rst"))
    for rst in rst_files:
        md = rst.with_suffix(".md")
        converted = convert_rst_to_myst(rst.read_text(encoding="utf-8"))
        md.write_text(converted, encoding="utf-8")

    cfg = MYST_YML.read_text(encoding="utf-8")
    cfg = re.sub(r"(file:\s+content/[\w-]+)\.rst\b", r"\1.md", cfg)
    MYST_YML.write_text(cfg, encoding="utf-8")


if __name__ == "__main__":
    main()
