from playwright.sync_api import expect

def test_web_page_blocked(page):
    """
    Étapes :
    1. Accéder à la page https://www.enpi-net.dz/LocauxEnpi/GreAgre.php
    2. Vérifier le titre de la page

    Résultat attendu :
    La page doit afficher le titre "WEB PAGE BLOCKED!"
    """
    page.goto("https://www.enpi-net.dz/LocauxEnpi/GreAgre.php")
    expect(page).to_have_title("WEB PAGE BLOCKED!")