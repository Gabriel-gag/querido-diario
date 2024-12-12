from datetime import date

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_volta_redonda"
    TERRITORY_ID = "3306305"
    allowed_domains = ["www.voltaredonda.rj.gov.br"]
    start_urls = ["https://www.voltaredonda.rj.gov.br/vrdestaque/index.php"]
    start_date = date(2019, 1, 4)

    def parse(self, response):
        # Lógica de extração de metadados

        # partindo de response ...
        #
        # ... o que deve ser feito para coletar DATA DO DIÁRIO?
        # ... o que deve ser feito para coletar NÚMERO DA EDIÇÃO?
        # ... o que deve ser feito para coletar se a EDIÇÃO É EXTRA?
        # ... o que deve ser feito para coletar a URL DE DOWNLOAD do arquivo?

        yield Gazette(
            date=date(),
            edition_number="",
            is_extra_edition=False,
            file_urls=[""],
            power="executive",
        )
