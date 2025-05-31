import scrapy
from urllib.parse import urljoin, urlparse
from help_scraper.items import QAItem
from langdetect import detect, LangDetectException
import re

class QASpider(scrapy.Spider):
    name = 'qa'
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(QASpider, self).__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("start_url required")
        
        self.start_urls = [start_url]
        self.start_url = start_url
        self.allowed_domains = [urlparse(start_url).netloc]
        self.visited = set()
        self.seen = set()
        
        # Create clean folder name from domain
        domain = urlparse(start_url).netloc
        domain = re.sub(r'^www\.', '', domain)  # Remove www
        domain = re.sub(r'[^\w\-]', '_', domain)  # Replace special chars
        self.output_folder = domain

    def is_english(self, text):
        if not text or len(text.strip()) < 30:
            return True
        try:
            return detect(text) == 'en'
        except LangDetectException:
            return True

    def clean_text(self, text):
        if not text:
            return ""
        return ' '.join(text.split()).strip()

    def valid_question(self, text):
        if not text or len(text) < 10:
            return False
        
        nav_patterns = [r'^learn more$', r'^more info', r'^click here', r'^read more', 
                       r'^see also', r'^related', r'^next', r'^previous', r'^home$', r'^back$']
        
        text_lower = text.lower()
        for pattern in nav_patterns:
            if re.match(pattern, text_lower):
                return False
        
        return (len(text) >= 10 and 
                not text_lower.startswith(('http', 'www', '@')) and
                text.count(' ') >= 2)

    def valid_answer(self, text):
        if not text or len(text) < 20:
            return False
        if text.count('http') > 3 or text.lower().count('learn more') > 2:
            return False
        return len(text.split()) >= 5

    def extract_pairs(self, response):
        pairs = []
        
        # FAQ headings
        for heading in response.css('h1, h2, h3, h4, h5, h6'):
            question = heading.css('::text').get()
            if not question:
                continue
                
            question = self.clean_text(question)
            if not self.valid_question(question):
                continue
            
            answer_elem = heading.xpath('./following-sibling::*[1]')
            if not answer_elem:
                answer_elem = heading.xpath('./following-sibling::text()[normalize-space()][1]')
            
            if answer_elem:
                answer = self.clean_text(' '.join(answer_elem.css('::text').getall()))
                if self.valid_answer(answer):
                    pairs.append((question, answer))
        
        # Definition lists
        for dt in response.css('dt'):
            question = self.clean_text(dt.css('::text').get() or "")
            dd = dt.xpath('./following-sibling::dd[1]')
            
            if question and dd and self.valid_question(question):
                answer = self.clean_text(' '.join(dd.css('::text').getall()))
                if self.valid_answer(answer):
                    pairs.append((question, answer))
        
        # Q&A sections
        for section in response.css('.faq-item, .qa-item, .question-answer'):
            q_elem = section.css('.question, .faq-question, h3, h4')
            a_elem = section.css('.answer, .faq-answer, p')
            
            if q_elem and a_elem:
                question = self.clean_text(q_elem.css('::text').get() or "")
                answer = self.clean_text(' '.join(a_elem.css('::text').getall()))
                
                if self.valid_question(question) and self.valid_answer(answer):
                    pairs.append((question, answer))
        
        return pairs

    def parse(self, response):
        if response.url in self.visited:
            return
        self.visited.add(response.url)
        
        pairs = self.extract_pairs(response)
        
        for question, answer in pairs:
            key = question.lower()
            if key in self.seen:
                continue
            self.seen.add(key)
            
            if self.is_english(question) and self.is_english(answer):
                item = QAItem()
                item['url'] = response.url
                item['question'] = question
                item['answer'] = answer
                yield item
        
        if response.url == self.start_url:
            for link in response.css('a::attr(href)').getall():
                url = urljoin(response.url, link)
                parsed = urlparse(url)
                
                if (parsed.netloc in self.allowed_domains and 
                    url not in self.visited and
                    any(k in url.lower() for k in ['help', 'support', 'faq', 'doc', 'guide', 'tutorial'])):
                    yield response.follow(link, self.parse) 