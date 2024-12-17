from datetime import date, datetime as dt

import scrapy
from scrapy import Selector

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_paraty"
    TERRITORY_ID = "3303807"
    allowed_domains = ["paraty.rj.gov.br"]
    start_date = date(2017, 8, 1)

    def start_requests(self):
        url_inicial = "https://www.paraty.rj.gov.br/multimidia/documentos"
        yield scrapy.Request(
            url=url_inicial, method="GET", callback=self.after_main_page
        )

    def after_main_page(self, response):
        url_api = "https://www.paraty.rj.gov.br/API/API/Documentos?PageNumber=1&PageSize=10000"
        yield scrapy.Request(
            url=url_api,
            method="GET",
            headers={"Accept": "application/xml"},
            callback=self.parse,
        )

    def parse(self, response):
        selector = Selector(text=response.text, type="xml")
        selector.register_namespace(
            "ns", "http://schemas.datacontract.org/2004/07/API.Api.ViewModels"
        )
        documentos = selector.xpath("//ns:DocumentoVm")
        self.logger.info(f"Documentos encontrados: {len(documentos)}")

        for doc in documentos:
            gazette_date_str = doc.xpath("./ns:DataPublicacao/text()").get()
            try:
                gazette_date = dt.strptime(gazette_date_str, "%d/%m/%Y").date()
            except ValueError:
                self.logger.error(f"Data inválida: {gazette_date_str}")
                continue

            # Verificando a data extraída
            self.logger.info(f"Processando documento com data {gazette_date}")

            if gazette_date < self.start_date:
                self.logger.info(
                    f"Pulando publicação com data {gazette_date} antes da start_date ({self.start_date})"
                )
                continue

            # Extração do arquivo e nome do arquivo
            file_url = doc.xpath(
                "./ns:DocumentoArquivoAtual/ns:CaminhoLogicoArquivo/text()"
            ).get()
            file_name = doc.xpath(
                "./ns:DocumentoArquivoAtual/ns:ArquivoNome/text()"
            ).get()

            if not file_url or not file_name:
                self.logger.error("URL do arquivo ou nome do arquivo não encontrados!")
                continue

            is_extra = "EXTRA" in file_name.upper()

            # Extração do título e número da edição
            title_tags = doc.xpath("./ns:Tag/ns:TagVm/ns:Descricao/text()").getall()
            title = " ".join(title_tags).strip() if title_tags else "Desconhecido"
            edition_number = title.split()[-1] if title else "Desconhecido"

            # Log para depuração
            self.logger.info(f"Título extraído: {title}")
            self.logger.info(f"Número da edição: {edition_number}")
            self.logger.info(f"Arquivo URL: {file_url}")
            self.logger.info(f"Nome do arquivo: {file_name}")

            # Gerar o item Gazette
            yield Gazette(
                date=gazette_date,
                edition_number=edition_number,
                is_extra_edition=is_extra,
                file_urls=[file_url],
                power="executive",
            )
