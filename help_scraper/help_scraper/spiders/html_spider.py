import scrapy
from urllib.parse import urljoin, urlparse
from help_scraper.items import HtmlItem
from langdetect import detect, LangDetectException
import re

class HtmlSpider(scrapy.Spider):
    name = 'html'
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(HtmlSpider, self).__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("start_url required")
        
        self.start_urls = [start_url]
        self.start_url = start_url
        self.allowed_domains = [urlparse(start_url).netloc]
        self.visited = set()
        
        # Create clean folder name from domain
        domain = urlparse(start_url).netloc
        domain = re.sub(r'^www\.', '', domain)  # Remove www
        domain = re.sub(r'[^\w\-]', '_', domain)  # Replace special chars
        self.output_folder = domain

    def is_english(self, text):
        if not text or len(text.strip()) < 50:
            return True
        try:
            return detect(text) == 'en'
        except LangDetectException:
            return True

    def clean_text(self, text):
        if not text:
            return ""
        return ' '.join(text.split())

    def get_content(self, response):
        selectors = ['main', 'article', '.content', '.main-content', '#content', '.help-content', '.page-content']
        
        for sel in selectors:
            elements = response.css(sel)
            if elements:
                content = self.clean_text(' '.join(elements.css('::text').getall()))
                if len(content) > 100:
                    return content
        
        content = self.clean_text(' '.join(response.css('body ::text').getall()))
        return content if len(content) > 100 else ""

    def parse(self, response):
        if response.url in self.visited:
            return
        self.visited.add(response.url)
        
        title = response.css('title::text').get() or response.css('h1::text').get() or ""
        title = self.clean_text(title)
        content = self.get_content(response)
        
        if content and self.is_english(content):
            item = HtmlItem()
            item['url'] = response.url
            item['title'] = title
            item['content'] = content
            yield item
        
        if response.url == self.start_url:
            for link in response.css('a::attr(href)').getall():
                url = urljoin(response.url, link)
                parsed = urlparse(url)
                
                if (parsed.netloc in self.allowed_domains and 
                    url not in self.visited and
                    any(k in url.lower() for k in ['help', 'support', 'faq', 'doc', 'guide', 'tutorial'])):
                    yield response.follow(link, self.parse) 