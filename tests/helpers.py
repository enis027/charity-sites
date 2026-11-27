import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "skills" / "charity-site-build"
AUDIT = ROOT / "skills" / "charity-site-audit"
HANDOFF = ROOT / "skills" / "charity-site-handoff"
for p in (BUILD / "template", BUILD / "scripts", AUDIT / "scripts", HANDOFF / "scripts"):
    sys.path.insert(0, str(p))
