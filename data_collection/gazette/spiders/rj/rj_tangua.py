import re
from datetime import datetime as dt

import scrapy

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class RjTanguaSpider(BaseGazetteSpider):
    name = "rj_tangua"
    TERRITORY_ID = "3305752"
    allowed_domains = ["tangua.rj.gov.br", "webtangua.supernova.com.br"]
    start_urls = [
        "https://webtangua.supernova.com.br:8443/contaspublicas/pages/publicacao_demais_relatorio.xhtml?faces-redirect=true"
    ]
    start_date = dt(2017, 1, 1).date()

    def start_requests(self):
        # Normaliza as datas de inicio e fim
        if isinstance(self.start_date, str):
            self.start_date = dt.strptime(self.start_date, "%Y-%m-%d").date()

        end_date_arg = getattr(self, "end_date", None)
        if end_date_arg:
            if isinstance(end_date_arg, str):
                self.end_date = dt.strptime(end_date_arg, "%Y-%m-%d").date()
            else:
                self.end_date = end_date_arg
        else:
            self.end_date = dt.today().date()

        self.logger.info(f"Executando spider de {self.start_date} até {self.end_date}")

        # Requisição inicial para capturar o ViewState
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        view_state = response.xpath(
            '//input[@name="javax.faces.ViewState"]/@value'
        ).get()

        # Calcula o intervalo de anos
        anos = range(self.start_date.year, self.end_date.year + 1)

        for ano in anos:
            # Primeiro, submete o formulário para alterar o ano
            formdata_ano = {
                "j_idt25": "j_idt25",
                "campo_alterar_exercicio": str(ano),
                "cmdAlterarExercicio": "cmdAlterarExercicio",
                "javax.faces.ViewState": view_state,
            }

            yield scrapy.FormRequest(
                url=response.url,
                formdata=formdata_ano,
                callback=self.submit_diario_form,
                cb_kwargs={"ano": ano, "view_state": view_state},
                dont_filter=True,
            )

    def submit_diario_form(self, response, ano, view_state):
        # valor para Diário Oficial é 2 no HTML
        formdata_diario = {
            "formCenter": "formCenter",
            "formCenter:j_idt37_input": "2",
            "formCenter:j_idt41": "formCenter:j_idt41",
            "javax.faces.ViewState": view_state,
        }

        yield scrapy.FormRequest(
            url=response.url,
            formdata=formdata_diario,
            callback=self.parse_results,
            cb_kwargs={"ano": ano},
            dont_filter=True,
        )

    def parse_results(self, response, ano):
        gazettes = response.xpath('//a[contains(@href, ".pdf")]')

        for gazette in gazettes:
            gazette_url = gazette.xpath("./@href").get()

            gazette_date = None
            title_attr = gazette.xpath("@title").get(default="")
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", title_attr)

            if date_match:
                try:
                    gazette_date = dt.strptime(date_match.group(1), "%d/%m/%Y").date()
                except ValueError:
                    continue

            if not gazette_date:
                continue

            if gazette_date > self.end_date:
                continue
            if gazette_date < self.start_date:
                return

            edition_number = None
            try:
                edition_number_text = gazette.xpath(
                    "./ancestor::tr/td[1]//span/text()"
                ).get()
                if edition_number_text and edition_number_text.isdigit():
                    edition_number = edition_number_text
            except Exception:
                pass

            yield Gazette(
                date=gazette_date,
                edition_number=edition_number,
                is_extra_edition=False,
                file_urls=[response.urljoin(gazette_url)],
                power="executive",
            )
