import json, sys
from agent.inspector import inspect_page
from agent.runner import run_agent
from agent.a11y import audit
from agent.report import build_report

url, request = sys.argv[1], sys.argv[2]
inv = inspect_page(url)
result = run_agent(request, inv, name="demo")
print(json.dumps({k: result[k] for k in ("passed", "attempts", "probable_bug", "test_file")},
                 indent=2, ensure_ascii=False))


# ... après run_agent :
rapport = build_report(result, url, audit(url))
print("Rapport :", rapport)