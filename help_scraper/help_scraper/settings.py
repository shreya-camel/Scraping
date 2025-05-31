BOT_NAME = 'help_scraper'

SPIDER_MODULES = ['help_scraper.spiders']
NEWSPIDER_MODULE = 'help_scraper.spiders'

# Respectful crawling
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Enable pipelines
ITEM_PIPELINES = {
    'help_scraper.pipelines.OutputPipeline': 300,
}

# Required settings
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'

# User agent
USER_AGENT = 'help_scraper (+http://www.yourdomain.com)' 