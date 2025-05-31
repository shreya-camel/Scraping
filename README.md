# Help Scraper

Web scraper for extracting help documentation and Q&A content.

## Features

- HTML content extraction and Q&A pair extraction
- English-only content filtering  
- Depth-limited crawling (start page + 1 level)
- Duplicate prevention
- Content filtering
- Domain-based output folders

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# HTML content
python help_scraper/run.py html https://help.example.com

# Q&A pairs
python help_scraper/run.py qa https://help.example.com
```

## Output

Each website gets its own folder based on the domain:

```
example_com/
  html_output/
    scraped_content.json
  qa_output/
    qa_pairs.json
```

## How It Works

1. **Depth 1 crawling**: Only follows help-related links from the start URL
2. **Language detection**: Filters content to English only using `langdetect`
3. **Content extraction**: Uses multiple strategies to find valid Q&A pairs
4. **Quality filtering**: Removes navigation, "Learn More" links, and other noise
5. **Deduplication**: Prevents duplicate URLs and repeated Q&A pairs
