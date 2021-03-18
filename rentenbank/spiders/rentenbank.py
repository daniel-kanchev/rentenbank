import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from rentenbank.items import Article


class RentenbankSpider(scrapy.Spider):
    name = 'rentenbank'
    start_urls = ['https://www.rentenbank.de/presse/']

    def parse(self, response):
        link = 'https://www.rentenbank.de/presse/pressearchiv/'
        yield response.follow(link, self.parse_archive)
        yield response.follow(response.url, self.parse_year, dont_filter=True)

        next_page = response.xpath('//a[@class="special-char next1"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_year)

    def parse_archive(self, response):
        years = response.xpath('//div[@id="content_container"]//ul/li/a/@href').getall()
        yield from response.follow_all(years, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//div[@class="col-sm-9"]/a[@class="btn btn_underline btn_right"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="special-char next1"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_year)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@id="content_container"]//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="news_einleitung"]//text()').getall() + \
                  response.xpath('//div[@class="row more_content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
