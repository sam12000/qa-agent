from playwright.sync_api import sync_playwright

INVENTORY_JS = """
() => [...document.querySelectorAll(
    'a,button,input,select,textarea,label,h1,h2,[role],[data-testid]')]
  .filter(e => e.offsetParent !== null)          // visibles uniquement
  .slice(0, 150)
  .map(e => ({
    tag: e.tagName.toLowerCase(),
    id: e.id || null,
    testid: e.dataset.testid || null,
    role: e.getAttribute('role'),
    type: e.getAttribute('type'),
    name: e.getAttribute('name'),
    aria: e.getAttribute('aria-label'),
    placeholder: e.getAttribute('placeholder'),
    text: (e.innerText || e.value || '').trim().slice(0, 60)
  }))
"""

def inspect_page(url: str, channel: str | None = None) -> dict:
    """channel = None (Chromium), 'chrome' ou 'msedge'."""
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        data = {"url": url, "title": page.title(),
                "elements": page.evaluate(INVENTORY_JS)}
        browser.close()
    return data


