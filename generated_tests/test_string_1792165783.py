from playwright.sync_api import expect

def test_page_title(page):
    """
    Étapes :
    1. Accéder à la page
    2. Vérifier le titre de la page

    Résultat attendu :
    Le titre de la page doit être "Mon Titre"
    """
    page.goto("URL")
    expect(page).to_have_title("Mon Titre")