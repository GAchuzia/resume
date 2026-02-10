"""
Replaces personal and identifying information with placeholders.
Usage:
  python anonymize_resume.py              # only write anonymized .tex to src_anonymized/
  python anonymize_resume.py --build      # anonymize and build PDF to build/Resume_Anonymized.pdf
"""

import subprocess
from pathlib import Path

RESUME_ROOT = Path(__file__).resolve().parent
SRC_DIR = RESUME_ROOT / "src"
OUT_DIR = RESUME_ROOT / "src_anonymized"
BUILD_DIR = RESUME_ROOT / "build"


REPLACEMENTS = [
    # --- Personal / contact (heading) ---
    ("Grant Achuzia", "[Your Name]"),
    ("grant.achuzia@gmail.com", "[your.email@example.com]"),
    ("gachuzia.com", "[yourwebsite.com]"),
    ("https://gachuzia.com/", "https://[yourwebsite.com]/"),
    ("linkedin.com/in/grant-achuzia-8259251b8", "linkedin.com/in/[your-profile]"),
    (
        "https://www.linkedin.com/in/grant-achuzia-8259251b8/",
        "https://www.linkedin.com/in/[your-profile]/",
    ),
    # --- Author / comments ---
    ("Grant Achuzia's Resume", "[Your Name]'s Resume"),
    ("Author : Grant Achuzia", "Author : [Your Name]"),
    ("Computer Systems Engineering", "Computer Engineering"),
    # --- Employers ---
    ("Lumentum", "[Employer 1]"),
    ("Maintenance Drone Co.", "[Employer 2]"),
    ("Roof Maintenance Solutions", "[Employer 3]"),
    # --- Education ---
    ("Carleton University", "[University Name]"),
    ("Ottawa, ON", "[City, Province]"),
    # --- Activities / certifications ---
    ("PC2214005330", "[Certificate Number]"),
    ("Calgary, AB", "[City, Province]"),
    # --- Project names (identifying) ---
    ("CU-Bytes", "[Project Name]"),
    ("Cell Reminders", "[Project Name]"),
    ("Fire Alarm Notification System (FANS)", "[Project Name]"),
]


EXTRA_REPLACEMENTS = [
    ("Ottawa", "[City]"),
]


def anonymize(text: str, extra: bool = False) -> str:
    """Apply all replacements to text."""
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if extra:
        for old, new in EXTRA_REPLACEMENTS:
            text = text.replace(old, new)
    return text


def main(extra_locations: bool = False) -> bool:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tex_files = sorted(SRC_DIR.glob("*.tex"))
    if not tex_files:
        print(f"No .tex files found in {SRC_DIR}")
        return False
    for path in tex_files:
        content = path.read_text(encoding="utf-8")
        anonymized = anonymize(content, extra=extra_locations)
        out_path = OUT_DIR / path.name
        out_path.write_text(anonymized, encoding="utf-8")
        print(f"  {path.name} -> {out_path}")
    print(f"Done. Anonymized sources are in: {OUT_DIR}")
    return True


def build_pdf() -> bool:
    """Run latexmk to build the anonymized PDF."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        "latexmk",
        "-cd",
        "-outdir=" + str(BUILD_DIR),
        "-jobname=Resume_Anonymized",
        "-pdf",
        "-interaction=nonstopmode",
        str(OUT_DIR / "resume.tex"),
    ]
    print("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=RESUME_ROOT)
    if result.returncode == 0:
        print(f"PDF written to: {BUILD_DIR / 'Resume_Anonymized.pdf'}")
    return result.returncode == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Anonymize resume LaTeX sources.")
    parser.add_argument(
        "--extra",
        action="store_true",
        help="Also replace standalone city names (e.g. Ottawa) with [City].",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="After anonymizing, build PDF to build/Resume_Anonymized.pdf",
    )
    args = parser.parse_args()
    if main(extra_locations=args.extra) and args.build:
        build_pdf()
