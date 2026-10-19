import pathlib, subprocess, sys
from .generator import generate_test

def run_test(code: str, name: str, channel: str = "chromium") -> dict:
    path = pathlib.Path("generated_tests") / f"test_{name}.py"
    path.write_text(code, encoding="utf-8")
    out = pathlib.Path("reports") / name
    cmd = [sys.executable, "-m", "pytest", str(path), "-q",
           "--screenshot", "only-on-failure",      # preuve visuelle
           "--tracing", "retain-on-failure",       # trace Playwright rejouable
           "--output", str(out),
           f"--junitxml={out / 'junit.xml'}"]
    if channel != "chromium":
        cmd += ["--browser-channel", channel]   # 'chrome' ou 'msedge'
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {"passed": res.returncode == 0, "log": res.stdout + res.stderr,
            "test_file": str(path), "artifacts": str(out), "code": code}

def is_probable_bug(log: str) -> bool:
    """L'élément existe mais la valeur est fausse = anomalie probable de l'appli."""
    return ("AssertionError" in log and "Actual value" in log
            and "not found" not in log)

def run_agent(request: str, inv: dict, name: str,
              channel: str = "chromium", max_attempts: int = 3) -> dict:
    code = error = None
    for attempt in range(1, max_attempts + 1):
        code = generate_test(request, inv, code, error)
        result = run_test(code, name, channel)
        result["attempts"] = attempt
        if result["passed"] or is_probable_bug(result["log"]):
            break                     # succès, ou vraie anomalie : on s'arrête
        error = result["log"]         # sinon : le test est faux, on le corrige
    result["probable_bug"] = not result["passed"] and is_probable_bug(result["log"])
    return result