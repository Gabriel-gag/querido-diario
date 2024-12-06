from playwright.sync_api import sync_playwright
import time

import os


def rodar(date, codigo, territoy):

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(accept_downloads=True)
        pagina = contexto.new_page()

        # Diretório para os downloads
        caminho_diretorio = os.path.join(os.getcwd(), f"data_collection/data/{territoy}/{date}")
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

        pagina.goto(f"chrome://downloads/")
        pagina.locator('#copy-download-link').click()
        link_copiado = pagina.evaluate('navigator.clipboard.readText()')
        print(link_copiado)
        #pagina.locator('#copy-download-link').click()
        #time.sleep(5)
        navegador.close()
        return link_copiado
        #for elemento in elementos.all_text_contents():  # Obtém o texto de cada elemento
        #    print(elemento)
        #navegador.close()s

if __name__ == "__main__":
    pr = rodar("20-8-56", '2080', '306040')
    print(pr)