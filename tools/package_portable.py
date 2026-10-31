"""Build a distribution ZIP for Windows users (called by the GitHub Actions workflow)."""
from __future__ import annotations
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256

ROOT = Path(__file__).resolve().parent.parent
NAMES = [
    "FIX_AURONUI.bat",
    "Check_Stage1_ONLY.bat",
    "Run_Stage1_Reset.bat",
    "Check_Stage2_ONLY.bat",
    "Run_Stage2_Reactivate.bat",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "auronui_reset.py", # inspectable source; no Python required to run the EXE
    "requirements.txt", # only required when running from Python source
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    exe = args.exe.resolve()
    if not exe.is_file():
        raise SystemExit(f"Windows executable was not found: {exe}")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    folder = "Auronui_Dispatch_Fix_v0.5.1_portable_beta"
    with ZipFile(args.output, "w", ZIP_DEFLATED, compresslevel=6) as z:
        z.write(exe, f"{folder}/AuronuiDispatchFix.exe")
        for filename in NAMES:
            p = ROOT / filename
            if not p.is_file():
                raise SystemExit(f"Required file missing: {p}")
            z.write(p, f"{folder}/{filename}")
    print(f"Created: {args.output}")
    print(f"SHA-256: {sha256(args.output.read_bytes()).hexdigest()}")

if __name__ == "__main__":
    main()
