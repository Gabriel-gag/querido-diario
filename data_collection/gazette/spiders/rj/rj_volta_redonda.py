from datetime import date, datetime as dt

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class RjVoltaRedondaSpider(BaseGazetteSpider):
    name = "rj_volta_redonda"
    TERRITORY_ID = "3306305"
    allowed_domains = ["voltaredonda.rj.gov.br"]
    start_urls = ["https://www.voltaredonda.rj.gov.br/vrdestaque/index.php"]
    start_date = date(2019, 1, 4)

    def parse(self, response):
        options = response.xpath('//select[@id="search"]/option[@value]')
        for option in options:
            file_url = option.xpath("@value").get()
            title = option.xpath("text()").get().strip()

            date_match = file_url.split("/")[-1].split("_")[0]

            gazette_date = dt.strptime(date_match, "%Y-%m-%d").date()

            if gazette_date < self.start_date:
                continue

            is_extra = "EXTRA" in title.upper()
            edition_number = file_url.split("_")[1].split(".")[0]

            yield Gazette(
                date=gazette_date,
                edition_number=edition_number,
                is_extra_edition=is_extra,
                file_urls=[response.urljoin(file_url)],
                power="executive",
            )
