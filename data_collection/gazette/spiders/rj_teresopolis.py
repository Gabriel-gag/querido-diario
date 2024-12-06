from datetime import date
import scrapy
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#import baixando_pdf

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider

class UFMunicipioSpider(BaseGazetteSpider): #BaseGazetteSpider):
    name = "rj_teresopolis"
    TERRITORY_ID = "3305802"
    allowed_domains = ["atos.teresopolis.rj.gov.br"]
    start_urls = ["https://atos.teresopolis.rj.gov.br/recurso/diario/lista?dataInicial=2024-09-05T00:00:00&dataFinal=2024-12-05T00:00:00"]
    start_date = date(2016, 7, 22)

    #baixando_pdf.rodar('2016-7-22', '2808')
    def start_requests(self):
            yield scrapy.Request(
                    f"https://atos.teresopolis.rj.gov.br/recurso/diario/lista?dataInicial={self.start_date}T00:00:00&dataFinal={self.end_date}T00:00:00"
                )

    def parse(self, response):
        html = response.json()
        codigos = []
        
        for item in html:
            codigo = item.get("codigo", None)
            if codigo:
                codigos.append(codigo)
                
        self.logger.info(f"Código extraído: {codigos}")

        # partindo de response ...
        #
        # ... o que deve ser feito para coletar DATA DO DIÁRIO?
        # ... o que deve ser feito para coletar NÚMERO DA EDIÇÃO?
        # ... o que deve ser feito para coletar se a EDIÇÃO É EXTRA?
        # ... o que deve ser feito para coletar a URL DE DOWNLOAD do arquivo?

        yield Gazette(
            date = date(),
            edition_number = "",
            is_extra_edition = False,
            file_urls = [""],
            power = "executive",
        )