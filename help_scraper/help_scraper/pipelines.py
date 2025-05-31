import os
import json
from itemadapter import ItemAdapter
from help_scraper.items import HtmlItem, QAItem

class OutputPipeline:
    def open_spider(self, spider):
        self.html_items = []
        self.qa_items = []
        
        # Create website-specific folder with subfolders
        base_folder = getattr(spider, 'output_folder', 'default')
        self.html_dir = os.path.join(base_folder, 'html_output')
        self.qa_dir = os.path.join(base_folder, 'qa_output')
        
        os.makedirs(self.html_dir, exist_ok=True)
        os.makedirs(self.qa_dir, exist_ok=True)

    def close_spider(self, spider):
        if self.html_items:
            filepath = os.path.join(self.html_dir, 'scraped_content.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.html_items, f, indent=2, ensure_ascii=False)
        
        if self.qa_items:
            filepath = os.path.join(self.qa_dir, 'qa_pairs.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.qa_items, f, indent=2, ensure_ascii=False)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if isinstance(item, HtmlItem):
            self.html_items.append({
                'url': adapter['url'],
                'title': adapter['title'],
                'content': adapter['content']
            })
        elif isinstance(item, QAItem):
            self.qa_items.append({
                'url': adapter['url'],
                'question': adapter['question'],
                'answer': adapter['answer']
            })
        
        return item 