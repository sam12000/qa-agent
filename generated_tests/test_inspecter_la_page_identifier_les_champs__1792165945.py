from playwright.sync_api import expect

def test_page_elements(page):
    """
    Étapes :
    1. Accéder à la page d'accueil d'Intermarché.
    2. Vérifier la présence des éléments suivants :
       - Un logo avec l'ID 'logo'
       - Un bouton de recherche avec le texte 'Rechercher'
       - Un lien vers la page 'Promotions' avec le texte 'Promotions'
       - Un lien vers la page 'Mon compte' avec le texte 'Mon compte'
       - Un lien vers la page 'Panier' avec le texte 'Panier'
    Résultat attendu : Tous les éléments doivent être présents et visibles.
    """
    page.goto("https://www.intermarche.com/accueil")
    expect(page.get_by_test_id("logo")).to_be_visible()
    expect(page.get_by_role(name="Rechercher")).to_be_visible()
    expect(page.get_by_text("Promotions")).to_be_visible()
    expect(page.get_by_text("Mon compte")).to_be_visible()
    expect(page.get_by_text("Panier")).to_be_visible()

def test_console_errors(page):
    """
    Étapes :
    1. Accéder à la page d'accueil d'Intermarché.
    2. Vérifier qu'il n'y a pas d'erreurs dans la console.
    Résultat attendu : La console doit être vide.
    """
    page.goto("https://www.intermarche.com/accueil")
    expect(page).to_have_no_console_errors()

def test_http_responses(page):
    """
    Étapes :
    1. Accéder à la page d'accueil d'Intermarché.
    2. Vérifier qu'il n'y a pas de réponses HTTP 5xx.
    Résultat attendu : Il ne doit pas y avoir de réponses HTTP 5xx.
    """
    page.goto("https://www.intermarche.com/accueil")
    expect(page).to_have_no_http_responses(status=500)

def test_accessibility(page):
    """
    Étapes :
    1. Accéder à la page d'accueil d'Intermarché.
    2. Vérifier la conformité à l'accessibilité.
    Résultat attendu : La page doit être conforme à l'accessibilité.
    """
    page.goto("https://www.intermarche.com/accueil")
    expect(page).to_have_no_accessibility_issues()