import json
from .llm import ask, extract_code

SYSTEM = """Tu es un SDET senior. Tu écris UN fichier de test pytest-playwright (Python).
Règles :
- utilise la fixture `page` et `from playwright.sync_api import expect` ;
- commence par page.goto(URL) ;
- locators dans cet ordre de préférence : get_by_test_id, get_by_role(name=...),
  get_by_label, get_by_placeholder, get_by_text ; jamais de XPath ;
- n'utilise QUE des éléments présents dans l'inventaire fourni ;
- chaque test a une docstring : Étapes + Résultat attendu ;
- assertions avec expect(...) ; jamais de time.sleep ;
- réponds uniquement avec le code, dans un bloc ```python```."""

def generate_test(request: str, inv: dict,
                  previous_code: str | None = None, error: str | None = None) -> str:
    user = (f"Demande du testeur : {request}\n"
            f"URL : {inv['url']}\nTitre : {inv['title']}\n"
            f"Inventaire JSON :\n{json.dumps(inv['elements'], ensure_ascii=False)[:12000]}")
    if error:
        user += (f"\n\nLe test précédent a échoué :\n```python\n{previous_code}\n```\n"
                 f"Erreur :\n{error[-3000:]}\n"
                 "Corrige uniquement les sélecteurs ou la syntaxe. "
                 "Ne supprime pas une assertion métier pour faire passer le test.")
    return extract_code(ask(SYSTEM, user))


from playwright.sync_api import Page, expect

def test_ajout_taches(page: Page):
    """Étapes : ajouter 2 tâches, cocher la première.
    Résultat attendu : le compteur affiche '1 item left'."""
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto("https://demo.playwright.dev/todomvc")
    champ = page.get_by_placeholder("What needs to be done?")
    champ.fill("Acheter du pain"); champ.press("Enter")
    champ.fill("Lancer la TNR"); champ.press("Enter")
    page.get_by_test_id("todo-item").first.get_by_role("checkbox").check()
    expect(page.get_by_test_id("todo-count")).to_have_text("1 item left")
    assert errors == [], f"Erreurs console : {errors}"