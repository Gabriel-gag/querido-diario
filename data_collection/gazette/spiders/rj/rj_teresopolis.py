from datetime import date

import scrapy

from gazette.baixando_pdf import rodar
from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_teresopolis"
    TERRITORY_ID = "3305802"
    allowed_domains = ["atos.teresopolis.rj.gov.br"]
    start_urls = [
        "https://atos.teresopolis.rj.gov.br/recurso/diario/lista?dataInicial=2024-09-05T00:00:00&dataFinal=2024-12-05T00:00:00"
    ]
    start_date = date(2016, 7, 22)

    def start_requests(self):
        yield scrapy.Request(
            f"https://atos.teresopolis.rj.gov.br/recurso/diario/lista?dataInicial={self.start_date}T00:00:00&dataFinal={self.end_date}T00:00:00"
        )

    def parse(self, response):
        html = response.json()
        codigos = []

        # Extrai os códigos de cada diário
        for item in html:
            codigo = item.get("codigo", None)
            if codigo:
                codigos.append(codigo)

        self.logger.info(f"Códigos extraídos: {codigos}")

        for codigo in codigos:
            # Formatando a data para ser passada para a função 'rodar'
            date_str = self.start_date.strftime("%Y-%m-%d")  # Formato 'YYYY-MM-DD'
            rodar(date_str, str(codigo))

            yield Gazette(
                edition_number=codigo,
                is_extra_edition=False,
                file_urls=[
                    f"https://atos.teresopolis.rj.gov.br/diario/{codigo}/download"
                ],
                power="executive",
            )
