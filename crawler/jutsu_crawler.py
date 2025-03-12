import scrapy
from bs4 import BeautifulSoup

class BlogSpider(scrapy.Spider):
    name = 'narutospider'
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        # Ensure we found the container
        container = response.css('.smw-columnlist-container').get()
        if not container:
            self.logger.error("Failed to find jutsu container.")
            return

        for href in response.css('.smw-columnlist-container a::attr(href)').extract():
            yield response.follow("https://naruto.fandom.com" + href, self.parse_jutsu)

        next_page = response.css('a.mw-nextlink::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_jutsu(self, response):
        # Get Jutsu Name
        jutsu_name = response.css("span.mw-page-title-main::text").get()
        if not jutsu_name:
            self.logger.error(f"Jutsu name not found for {response.url}")
            return
        jutsu_name = jutsu_name.strip()

        # Extract main content
        div_html = response.css("div.mw-parser-output").get()
        if not div_html:
            self.logger.error(f"Jutsu content not found for {response.url}")
            return

        soup = BeautifulSoup(div_html, "html.parser")
        jutsu_type = ""

        aside = soup.find('aside')
        if aside:
            for cell in aside.find_all('div', {'class': 'pi-data'}):
                header = cell.find('h3')
                if header and header.text.strip() == "Classification":
                    jutsu_type = cell.find('div').text.strip()

            aside.decompose()  # Remove aside to clean description text

        # Extract Jutsu Description
        jutsu_description = soup.get_text(separator=" ", strip=True)
        jutsu_description = jutsu_description.split('Trivia')[0].strip()

        yield {
            "jutsu_name": jutsu_name,
            "jutsu_type": jutsu_type,
            "jutsu_description": jutsu_description
        }
