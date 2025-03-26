import scrapy
from bs4 import BeautifulSoup

class BlogSpider(scrapy.Spider):
    name = 'narutospider'
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        # Check if the container exists before accessing it
        container = response.css('.smw-columnlist-container')
        if not container:
            self.logger.error("No jutsu list found on the page.")
            return

        # Extract and follow each jutsu link
        for href in container[0].css("a::attr(href)").extract():
            yield response.follow(href, callback=self.parse_jutsu)

        # Follow pagination if there's a next page
        next_page = response.css('a.mw-nextlink::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_jutsu(self, response):
        # Extract the jutsu name
        jutsu_name = response.css("span.mw-page-title-main::text").get()
        if not jutsu_name:
            self.logger.warning(f"Jutsu name not found for URL: {response.url}")
            return
        jutsu_name = jutsu_name.strip()

        # Extract the main content div
        div_selector = response.css("div.mw-parser-output")
        if not div_selector:
            self.logger.warning(f"No content found for {jutsu_name}")
            return

        div_html = div_selector.get()
        soup = BeautifulSoup(div_html, "html.parser")

        # Extract classification (jutsu type)
        jutsu_type = ""
        aside = soup.find('aside')
        if aside:
            for cell in aside.find_all('div', {'class': 'pi-data'}):
                if cell.find('h3') and cell.find('div'):
                    cell_name = cell.find('h3').text.strip()
                    if cell_name == "Classification":
                        jutsu_type = cell.find('div').text.strip()
            aside.decompose()  # Remove aside from soup to avoid duplicate content

        # Extract the jutsu description
        jutsu_description = soup.text.strip()
        jutsu_description = jutsu_description.split('Trivia')[0].strip()

        # Yielding the result instead of returning
        yield {
            "jutsu_name": jutsu_name,
            "jutsu_type": jutsu_type,
            "jutsu_description": jutsu_description
        }
