"""Non-destructive EXE smoke test. No personal game saves are needed."""
from pathlib import Path
import subprocess
import sys
import tempfile


def check_exe(exe: Path):
    help_result = subprocess.run([str(exe), "--help"], capture_output=True, text=True, timeout=45)
    if help_result.returncode != 0 or "--stage" not in help_result.stdout:
        raise RuntimeError(f"EXE help test failed:\n{help_result.stdout}\n{help_result.stderr}")
    with tempfile.TemporaryDirectory() as td:
        location = Path(td)
        broken = location / "not_a_real_game_save.save"
        original = b"NOT A SAVE: TEST FIXTURE ONLY"
        broken.write_bytes(original)
        for stage in ("auto", "1", "2"):
            result = subprocess.run(
                [str(exe), str(broken), "--stage", stage, "--check"],
                capture_output=True, text=True, timeout=45,
            )
            if result.returncode == 0:
                raise RuntimeError(f"Stage {stage}: should reject invalid data.")
            if "not a recognized Crimson Desert SAVE file" not in result.stderr:
                raise RuntimeError(f"Stage {stage}: unexpected rejection: {result.stderr}")
            if broken.read_bytes() != original or list(location.iterdir()) != [broken]:
                raise RuntimeError(f"Stage {stage}: unexpectedly changed or created a file.")
    print("PASS: --help, rejecting invalid saves at both stages, no files modified")
    print("NOTE: This is not a gameplay validation and does not test real save repair.")

if __name__ == "__main__":
    check_exe(Path(sys.argv[1]).resolve())
