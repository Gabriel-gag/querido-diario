from playwright.sync_api import sync_playwright
import time

import os


def rodar(date, codigo):

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(accept_downloads=True)
        pagina = contexto.new_page()

        # Diretório para os downloads
        caminho_diretorio = os.path.join(os.getcwd(), f"meus_downloads/{date}")
        os.makedirs(caminho_diretorio, exist_ok=True)

        pagina.goto(f"https://atos.teresopolis.rj.gov.br/diario/#/diario/{codigo}")

        # Espera pelo download
        with pagina.expect_download() as download_info:
            pagina.locator("pdf-download").click()
            time.sleep(1)
            pagina.locator("pdf-download").click()
        
        download = download_info.value

        # Salva o arquivo no diretório desejado
        arquivo_caminho = os.path.join(caminho_diretorio, download.suggested_filename)
        download.save_as(arquivo_caminho)
        print(f"Arquivo salvo em: {arquivo_caminho}")

        time.sleep(5)
        navegador.close()
        #for elemento in elementos.all_text_contents():  # Obtém o texto de cada elemento
        #    print(elemento)
        #navegador.close()s