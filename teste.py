from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto("https://atos.teresopolis.rj.gov.br/diario/#/diarios")
    time.sleep(5)
    elementos = pagina.locator("ion-text")  # Localiza todos os elementos <ion-text>
    for elemento in elementos.all_text_contents():  # Obtém o texto de cada elemento
        print(elemento)
    navegador.close()