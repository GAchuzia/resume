#!/usr/bin/env python3
"""Generate build/Resume_GrantAchuzia.md from the LaTeX sources in src/.

Usage: python3 scripts/tex_to_md.py [output_path]
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
OUT = SRC.parent / "build" / "Resume_GrantAchuzia.md"


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def read_group(tex, i):
    """Return (content, end) for the {...} group starting at or after index i."""
    i = tex.index("{", i)
    depth = 0
    for j in range(i, len(tex)):
        if tex[j] == "{" and tex[j - 1] != "\\":
            depth += 1
        elif tex[j] == "}" and tex[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return tex[i + 1 : j], j + 1
    raise ValueError("unbalanced braces")


def replace_command(tex, name, fn, nargs=1):
    """Replace every \\name{a}{b}... with fn(a, b, ...)."""
    pattern = re.compile(r"\\" + name + r"(?![a-zA-Z])\s*")
    while (m := pattern.search(tex)):
        args, end = [], m.end()
        for _ in range(nargs):
            arg, end = read_group(tex, end)
            args.append(arg)
        tex = tex[: m.start()] + fn(*args) + tex[end:]
    return tex


def inline(tex):
    """Convert inline LaTeX to Markdown."""
    tex = replace_command(tex, "href", lambda url, text: f"[{inline(text)}]({url.replace(chr(92), '')})", 2)
    tex = replace_command(tex, "textbf", lambda s: f"**{inline(s).strip()}**")
    for cmd in ("textit", "emph"):
        tex = replace_command(tex, cmd, lambda s: f"*{inline(s).strip()}*")
    tex = replace_command(tex, "texttt", lambda s: f"`{inline(s)}`")
    tex = replace_command(tex, "textnormal", inline)
    tex = re.sub(r"\\(small|large|Large|Huge|footnotesize|scriptsize|normalfont|upshape)\b\s*", "", tex)
    tex = tex.replace("$|$", "|").replace("---", "—").replace("--", "–")
    tex = re.sub(r"\\([&%#_$])", r"\1", tex)
    tex = re.sub(r"\*\*\s*\*\*", "", tex)
    return re.sub(r"\s+", " ", tex).strip()


def link_title(title, link):
    """Use the right-hand link of a project heading as the title's link."""
    m = re.search(r"\]\(([^)]+)\)", link)
    return f"[{title}]({m.group(1)})" if m else title


def convert_section(tex):
    lines = []
    tokens = re.compile(
        r"\\(section|resumeSubheading|resumeProjectSubheading|resumeSubSubheading|resumeItem)(?![a-zA-Z])"
    )
    pos = 0
    while (m := tokens.search(tex, pos)):
        kind = m.group(1)
        if kind == "section":
            title, pos = read_group(tex, m.end())
            lines += ["", f"## {inline(title).strip('* ').title()}", ""]
        elif kind == "resumeSubheading":
            args = []
            pos = m.end()
            for _ in range(4):
                arg, pos = read_group(tex, pos)
                args.append(inline(arg))
            name, dates, role, place = args
            lines += [f"### {name}", f"*{role}* · {place} · {dates}".replace(" ·  · ", " · "), ""]
        elif kind == "resumeProjectSubheading":
            args = []
            pos = m.end()
            for _ in range(4):
                arg, pos = read_group(tex, pos)
                args.append(inline(arg))
            name, link, stack, _ = args
            lines += [f"### {link_title(name, link)}", f"*{stack}*", ""]
        elif kind == "resumeSubSubheading":
            role, pos = read_group(tex, m.end())
            dates, pos = read_group(tex, pos)
            lines += [f"*{inline(role)}* · {inline(dates)}", ""]
        else:
            item, pos = read_group(tex, m.end())
            lines.append(f"- {inline(item)}")
            nxt = tokens.search(tex, pos)
            if not nxt or nxt.group(1) != "resumeItem":
                lines.append("")
    # Skills: a plain itemize after the heading, one line per \\ row.
    rest = tex[pos:]
    if "itemize" in rest:
        body = re.sub(r"\\(begin|end)\{itemize\}(\[[^\]]*\])?|\\item\b", "", rest)
        for row in re.split(r"\\\\", body):
            row = inline(row).strip("{} ")
            if row:
                lines.append(f"- {row}")
    return lines


def heading(tex):
    name = re.search(r"\\Huge\s+([^}]+)\}", tex).group(1).strip()
    links = []
    pattern = re.compile(r"\\href")
    pos = 0
    while (m := pattern.search(tex, pos)):
        url, pos = read_group(tex, m.end())
        text, pos = read_group(tex, pos)
        links.append(f"[{inline(text)}]({url})")
    return [f"# {name}", "", " · ".join(links)]


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    root = strip_comments((SRC / "resume.tex").read_text())
    body = root.split("\\begin{document}", 1)[1]
    md = []
    for name in re.findall(r"\\input\{([^}]+)\}", body):
        path = SRC / (name if name.endswith(".tex") else f"{name}.tex")
        tex = strip_comments(path.read_text())
        if name == "custom-commands":
            continue
        md += heading(tex) if name == "heading" else convert_section(tex)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
