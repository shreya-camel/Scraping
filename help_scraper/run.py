#!/usr/bin/env python3

import sys
import subprocess
import os
import re
from urllib.parse import urlparse

def get_folder_name(url):
    """Extract clean folder name from URL"""
    domain = urlparse(url).netloc
    domain = re.sub(r'^www\.', '', domain)  # Remove www
    domain = re.sub(r'[^\w\-]', '_', domain)  # Replace special chars
    return domain

def main():
    if len(sys.argv) != 3:
        print("Usage: python run.py [html|qa] <start_url>")
        print("\nExamples:")
        print("  python run.py html https://help.example.com")
        print("  python run.py qa https://support.example.com/faq")
        sys.exit(1)
    
    mode = sys.argv[1]
    start_url = sys.argv[2]
    
    if mode not in ['html', 'qa']:
        print("Error: Mode must be 'html' or 'qa'")
        sys.exit(1)
    
    if not os.path.exists('scrapy.cfg'):
        print("Error: Run this from the project root directory")
        sys.exit(1)
    
    folder_name = get_folder_name(start_url)
    cmd = ['scrapy', 'crawl', mode, '-a', f'start_url={start_url}']
    
    print(f"Starting {mode} scraper for: {start_url}")
    print(f"Output folder: {folder_name}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        subprocess.run(cmd, check=True)
        print("\nScraping completed!")
        
        if mode == 'html':
            print(f"HTML content saved to: {folder_name}/html_output/scraped_content.json")
        else:
            print(f"Q&A pairs saved to: {folder_name}/qa_output/qa_pairs.json")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running spider: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Scrapy not found. Install it with:")
        print("pip install scrapy")
        sys.exit(1)

if __name__ == '__main__':
    main() 