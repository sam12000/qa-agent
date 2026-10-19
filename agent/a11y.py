from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

def audit(url: str, channel: str | None = None) -> list[dict]:
    axe = Axe()
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        results = axe.run(page)
        browser.close()
    return [{
        "regle": v["id"],                 # ex. color-contrast, image-alt
        "impact": v["impact"],            # minor / moderate / serious / critical
        "description": v["help"],
        "elements": len(v["nodes"]),
        "exemple": v["nodes"][0]["target"] if v["nodes"] else None,
        "doc": v["helpUrl"],
    } for v in results.response["violations"]]