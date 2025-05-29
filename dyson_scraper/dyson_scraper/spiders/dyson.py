import scrapy
from urllib.parse import urljoin


class DysonSpider(scrapy.Spider):
    name = "dyson"
    allowed_domains = ["support.dyson.com"]
    start_urls = [
        "https://support.dyson.com/support/"
    ]

    def parse(self, response):
        product_links = response.css("a::attr(href)").getall()
        for link in product_links:
            if "/support/" in link and not link.endswith((".pdf", ".jpg")):
                yield response.follow(urljoin(response.url, link), callback=self.parse_support_page)

    def parse_support_page(self, response):
        page_data = {
            "url": response.url,
            "title": response.css("title::text").get(),
            "headings": response.css("h1::text, h2::text, h3::text").getall(),
            "content": " ".join(response.css("p::text, li::text, div.support-content *::text").getall()).strip()
        }
        yield page_data

        next_links = response.css("a::attr(href)").getall()
        for link in next_links:
            if "/support/" in link and not link.endswith((".pdf", ".jpg")):
                yield response.follow(urljoin(response.url, link), callback=self.parse_support_page)
