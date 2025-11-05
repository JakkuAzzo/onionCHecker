#!/usr/bin/env python3
"""
Onion Site Accessibility Checker

This script accesses a .onion site listing via Tor and tests the accessibility
of listed .onion sites, saving accessible ones to a JSON file.
"""

import requests
import json
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import sys
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onion_checker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OnionSiteChecker:
    def __init__(self, output_file='accessible_onion_sites.json'):
        """Initialize the OnionSiteChecker with Tor proxy configuration."""
        self.output_file = output_file
        self.accessible_sites = self.load_existing_sites()
        
        # Tor proxy configuration (default Tor SOCKS proxy port)
        self.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers to mimic a regular browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def load_existing_sites(self):
        """Load existing accessible sites from JSON file."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'accessible_sites' in data:
                        return data['accessible_sites']
                    elif isinstance(data, list):
                        return data
                    else:
                        return []
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading existing sites: {e}")
                return []
        return []
    
    def save_sites(self):
        """Save accessible sites to JSON file with metadata."""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_accessible_sites': len(self.accessible_sites),
            'accessible_sites': self.accessible_sites
        }
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.accessible_sites)} accessible sites to {self.output_file}")
        except IOError as e:
            logger.error(f"Error saving sites: {e}")
    
    def test_tor_connection(self):
        """Test if Tor connection is working by checking IP."""
        try:
            response = self.session.get(
                'http://httpbin.org/ip',
                proxies=self.proxies,
                timeout=30
            )
            if response.status_code == 200:
                ip_info = response.json()
                logger.info(f"Tor connection successful. Current IP: {ip_info.get('origin', 'Unknown')}")
                return True
        except Exception as e:
            logger.error(f"Tor connection test failed: {e}")
            logger.error("Make sure Tor is running on port 9050")
            return False
        return False
    
    def extract_onion_sites(self, html_content):
        """Extract .onion sites from the HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        onion_sites = []
        
        # Look for the link_list element
        link_list = soup.find(id='link_list')
        if not link_list:
            logger.warning("Could not find element with id='link_list'")
            return onion_sites
        
        # Extract all links that end with .onion
        links = link_list.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.endswith('.onion') or '.onion/' in href:
                # Clean and normalize the URL
                if not href.startswith('http'):
                    href = 'http://' + href.lstrip('/')
                
                # Extract just the domain part
                parsed = urlparse(href)
                onion_domain = parsed.netloc
                
                if onion_domain and onion_domain.endswith('.onion'):
                    onion_sites.append({
                        'domain': onion_domain,
                        'url': href,
                        'text': link.get_text().strip()
                    })
        
        return onion_sites
    
    def fetch_onion_listing_page(self, page_number):
        """Fetch the onion listing page for a given page number."""
        base_url = "http://jptvwdeyknkv6oiwjtr2kxzehfnmcujl7rf7vytaikmwlvze773uiyyd.onion/"
        url = f"{base_url}?page={page_number}"
        
        try:
            logger.info(f"Fetching listing page: {page_number}")
            response = self.session.get(
                url,
                proxies=self.proxies,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch page {page_number}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching page {page_number}: {e}")
            return None
    
    def test_onion_site_accessibility(self, site_info):
        """Test if an onion site is accessible."""
        url = site_info['url']
        domain = site_info['domain']
        
        # Skip if we already tested this domain
        for existing_site in self.accessible_sites:
            if existing_site['domain'] == domain:
                logger.debug(f"Already tested {domain}, skipping")
                return False
        
        try:
            logger.info(f"Testing accessibility: {domain}")
            response = self.session.get(
                url,
                proxies=self.proxies,
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                logger.info(f"✓ {domain} is accessible")
                site_info['status'] = 'accessible'
                site_info['tested_at'] = datetime.now().isoformat()
                site_info['response_time'] = response.elapsed.total_seconds()
                return True
            else:
                logger.warning(f"✗ {domain} returned HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"✗ {domain} timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"✗ {domain} connection failed")
            return False
        except Exception as e:
            logger.warning(f"✗ {domain} error: {e}")
            return False
    
    def run_checker(self, start_page=1072722848287667155967, max_pages=10, delay_range=(5, 15)):
        """Run the main checker loop."""
        if not self.test_tor_connection():
            logger.error("Cannot proceed without Tor connection")
            return
        
        logger.info(f"Starting onion site checker from page {start_page}")
        logger.info(f"Will check up to {max_pages} pages")
        
        page_number = start_page
        pages_checked = 0
        sites_found = 0
        sites_accessible = 0
        
        try:
            while pages_checked < max_pages:
                # Fetch the listing page
                html_content = self.fetch_onion_listing_page(page_number)
                if not html_content:
                    logger.warning(f"Failed to fetch page {page_number}, trying next page")
                    page_number += 1
                    continue
                
                # Extract onion sites from the page
                onion_sites = self.extract_onion_sites(html_content)
                sites_found += len(onion_sites)
                
                if not onion_sites:
                    logger.warning(f"No onion sites found on page {page_number}")
                else:
                    logger.info(f"Found {len(onion_sites)} onion sites on page {page_number}")
                
                # Test each site for accessibility
                for site_info in onion_sites:
                    if self.test_onion_site_accessibility(site_info):
                        self.accessible_sites.append(site_info)
                        sites_accessible += 1
                        # Save progress after each accessible site found
                        self.save_sites()
                    
                    # Random delay between requests to avoid being blocked
                    delay = random.uniform(delay_range[0], delay_range[1])
                    logger.debug(f"Waiting {delay:.1f} seconds before next request")
                    time.sleep(delay)
                
                pages_checked += 1
                page_number += 1
                
                logger.info(f"Progress: {pages_checked}/{max_pages} pages, "
                          f"{sites_found} sites found, {sites_accessible} accessible")
                
                # Longer delay between pages
                if pages_checked < max_pages:
                    page_delay = random.uniform(15, 30)
                    logger.info(f"Waiting {page_delay:.1f} seconds before next page")
                    time.sleep(page_delay)
        
        except KeyboardInterrupt:
            logger.info("Checker interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            # Final save
            self.save_sites()
            logger.info(f"Checker finished. Total accessible sites: {len(self.accessible_sites)}")

def main():
    """Main function to run the onion site checker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check .onion site accessibility via Tor')
    parser.add_argument('--start-page', type=int, default=1072722848287667155967,
                      help='Starting page number (default: 1072722848287667155967)')
    parser.add_argument('--max-pages', type=int, default=10,
                      help='Maximum number of pages to check (default: 10)')
    parser.add_argument('--output', type=str, default='accessible_onion_sites.json',
                      help='Output JSON file (default: accessible_onion_sites.json)')
    parser.add_argument('--min-delay', type=int, default=5,
                      help='Minimum delay between requests in seconds (default: 5)')
    parser.add_argument('--max-delay', type=int, default=15,
                      help='Maximum delay between requests in seconds (default: 15)')
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Onion Site Accessibility Checker")
    logger.info("=" * 50)
    logger.info("IMPORTANT: Make sure Tor is running on port 9050")
    logger.info("On most systems, you can start Tor with: sudo systemctl start tor")
    logger.info("=" * 50)
    
    checker = OnionSiteChecker(output_file=args.output)
    checker.run_checker(
        start_page=args.start_page,
        max_pages=args.max_pages,
        delay_range=(args.min_delay, args.max_delay)
    )

if __name__ == "__main__":
    main()