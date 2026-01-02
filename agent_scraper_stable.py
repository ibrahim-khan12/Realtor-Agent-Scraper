#!/usr/bin/env python3
"""
Realtor.com Agent Scraper - STABLE VERSION with Progress Saving
Works for any number of agents - NO HEADLESS MODE (more stable)
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealtorAgentScraperStable:
    def __init__(self):
        logger.info("Initializing ChromeDriver...")
        self.driver = self.setup_driver()
        self.agents = []
        self.save_frequency = 50  # Save every 50 agents
        self.collected_urls = set()  # Store URLs collected during pagination

    def setup_driver(self):
        options = uc.ChromeOptions()
        
        # Optimize for speed - disable images
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = uc.Chrome(options=options, version_main=134)
        logger.info("ChromeDriver ready (Browser visible - more stable)")
        return driver

    def search_city(self, city, state):
        """Search for agents in specified city"""
        try:
            search_query = f"{city}, {state}"
            logger.info(f"\nSearching for agents in {search_query}...")
            
            # Navigate to search page
            self.driver.get("https://www.realtor.com/realestateagents")
            time.sleep(2)
            
            # Find and fill search input
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'City')]"))
            )
            search_input.click()
            time.sleep(0.3)
            search_input.clear()
            search_input.send_keys(search_query)
            time.sleep(0.5)
            search_input.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Wait for results to load
            logger.info("Waiting for search results to load...")
            time.sleep(2)
            
            # Load all pages with pagination
            self.load_all_pages()
            
            # Collect and scrape agents with progress saving
            agent_count = self.scrape_agents_with_progress_saving(city, state)
            logger.info(f"✓ Extracted {agent_count} agents from {search_query}")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
    
    def load_all_pages(self):
        """Load all pages by clicking through pagination and collect URLs from each"""
        page_num = 1
        all_agent_urls = set()
        
        while True:
            logger.info(f"\n{'='*70}")
            logger.info(f"LOADING PAGE {page_num}")
            logger.info(f"{'='*70}")
            
            # Scroll current page to load all agents on this page
            logger.info("Scrolling current page...")
            
            for _ in range(5):  # Scroll 5 times per page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
            
            # Collect URLs from THIS page before moving to next
            logger.info(f"Collecting URLs from page {page_num}...")
            agent_links = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="agent-name"]')
            if not agent_links:
                agent_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/realestateagents/5"]')
            
            page_url_count = 0
            for link in agent_links:
                try:
                    url = link.get_attribute('href')
                    if url and '/realestateagents/5' in url:
                        all_agent_urls.add(url)
                        page_url_count += 1
                except:
                    pass
            
            logger.info(f"✓ Collected {page_url_count} URLs from page {page_num} (Total: {len(all_agent_urls)})")
            
            # Look for "Next" button to go to next page
            try:
                next_button = None
                
                # Try different selectors for pagination
                next_selectors = [
                    '//a[@aria-label="Go to next page"]',
                    '//button[@aria-label="Go to next page"]',
                    '//a[contains(@class, "next")]',
                    '//button[contains(text(), "Next")]',
                    '//a[contains(text(), "Next")]',
                    '//a[@rel="next"]',
                ]
                
                for selector in next_selectors:
                    try:
                        next_button = self.driver.find_element(By.XPATH, selector)
                        if next_button and next_button.is_displayed() and next_button.is_enabled():
                            break
                        else:
                            next_button = None
                    except:
                        continue
                
                if next_button:
                    logger.info(f"Moving to page {page_num + 1}...")
                    
                    # Scroll to button and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.5)
                    
                    try:
                        next_button.click()
                    except:
                        # Try JavaScript click if regular click fails
                        self.driver.execute_script("arguments[0].click();", next_button)
                    
                    time.sleep(3)  # Wait for next page to load
                    page_num += 1
                else:
                    logger.info(f"✓ No more pages. Loaded {page_num} page(s) total.")
                    break
                    
            except Exception as e:
                logger.info(f"✓ Reached last page (Page {page_num})")
                break
            
            # Safety limit - realtor.com caps at ~42 pages
            if page_num >= 50:
                logger.info("Reached safety limit of 50 pages")
                break
        
        logger.info(f"\n{'='*70}")
        logger.info(f"FINISHED LOADING ALL {page_num} PAGES")
        logger.info(f"Total unique agent URLs collected: {len(all_agent_urls)}")
        logger.info(f"{'='*70}\n")
        
        # Store collected URLs for later use
        self.collected_urls = all_agent_urls
    
    def scrape_agents_with_progress_saving(self, city, state):
        """Collect URLs and scrape with progress saving every N agents"""
        
        # Check for existing progress file
        filename = f"agents_{city.replace(' ', '_')}_{state}_progress.csv"
        scraped_urls = set()
        
        if os.path.exists(filename):
            logger.info(f"Found existing file: {filename}")
            try:
                existing_df = pd.read_csv(filename)
                if 'profile_url' in existing_df.columns:
                    scraped_urls = set(existing_df['profile_url'].dropna())
                    logger.info(f"Already scraped {len(scraped_urls)} agents. Will skip these.")
                    self.agents = existing_df.to_dict('records')
            except Exception as e:
                logger.warning(f"Could not load existing file: {e}")
        
        # Use URLs collected during pagination
        agent_urls = self.collected_urls
        logger.info(f"Using {len(agent_urls)} URLs collected from pagination")
        
        # Filter out already scraped URLs
        urls_to_scrape = list(agent_urls - scraped_urls)
        total_urls = len(agent_urls)
        already_scraped = len(scraped_urls)
        
        logger.info(f"\nTotal agents found: {total_urls}")
        logger.info(f"Already scraped: {already_scraped}")
        logger.info(f"Remaining to scrape: {len(urls_to_scrape)}")
        
        if len(urls_to_scrape) == 0:
            logger.info("All agents already scraped!")
            return len(self.agents)
        
        # Scrape remaining agents with progress saving
        for idx, url in enumerate(urls_to_scrape, 1):
            try:
                logger.info(f"Scraping agent {idx}/{len(urls_to_scrape)} (Total: {already_scraped + idx}/{total_urls})")
                self.driver.get(url)
                time.sleep(0.8)
                
                # Extract data
                self.extract_agent_data_from_page(url)
                
                # Save progress every N agents
                if idx % self.save_frequency == 0:
                    self.save_progress(filename)
                    logger.info(f"✓ Progress saved ({idx} agents scraped in this session)")
                
            except Exception as e:
                logger.error(f"Error scraping agent {idx}: {e}")
        
        # Final save
        self.save_progress(filename)
        logger.info(f"✓ Final save complete!")
        
        return len(self.agents)
    
    def extract_agent_data_from_page(self, profile_url):
        """Extract agent data from current profile page"""
        try:
            time.sleep(0.3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract name
            agent_name = ''
            try:
                name_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                agent_name = name_elem.text.strip()
            except:
                pass
            
            # Extract other fields
            phone = self.extract_phone(text)
            address = self.extract_address(text)
            brokerage = self.extract_brokerage(text)
            license_num = self.extract_license(text)
            
            # Store with profile URL for resume capability
            self.agents.append({
                'name': agent_name,
                'phone_number': phone,
                'address': address,
                'brokerage': brokerage,
                'agent_license': license_num,
                'profile_url': profile_url
            })
            
            logger.info(f"  ✓ {agent_name} - Phone: {phone or 'N/A'}")
            
        except Exception as e:
            logger.error(f"Error extracting agent data: {e}")

    def extract_phone(self, text):
        """Extract phone number"""
        patterns = [
            r'\((\d{3})\)\s*(\d{3})-(\d{4})\s+mobile',
            r'(\d{3})-(\d{3})-(\d{4})\s+mobile',
            r'\((\d{3})\)\s*(\d{3})-(\d{4})\s+office',
            r'(\d{3})-(\d{3})-(\d{4})\s+office',
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return f"({groups[0]}) {groups[1]}-{groups[2]}"
        return ''

    def extract_address(self, text):
        """Extract office address"""
        patterns = [
            r'(\d+\s+[A-Za-z\s]+(?:Road|Street|Avenue|Drive|Boulevard|Lane|Way|Court|Circle|Parkway|Ave|St|Dr|Blvd|Ln|Rd|Ct|Cir|Pkwy)\s+[A-Za-z\s,]+[A-Z]{2}\s+\d{5})',
            r'(\d+\s+[A-Za-z\s]+\s+[A-Za-z\s,]+[A-Z]{2}\s+\d{5})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                addr = match.group(1).strip()
                addr = re.sub(r'\s+', ' ', addr)
                return addr
        return ''

    def extract_brokerage(self, text):
        """Extract brokerage name"""
        lines = text.split('\n')
        keywords = ['Realty', 'Real Estate', 'Broker', 'Group', 'Associates', 'Company', 'Properties']
        for line in lines:
            line = line.strip()
            if any(kw in line for kw in keywords):
                if 10 < len(line) < 100 and not line.startswith('©'):
                    excluded = ['find a', 'search for', 'contact', 'call', 'email', 'sign in', 
                                'register', 'save', 'filter', 'sort by', 'view', 'show']
                    if not any(phrase in line.lower() for phrase in excluded):
                        return line
        return ''

    def extract_license(self, text):
        """Extract agent license number"""
        patterns = [
            r'Agent license\s*#\s*(\d+)',
            r'License\s*#\s*(\d+)',
            r'#(\d{6,})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ''
    
    def save_progress(self, filename):
        """Save current progress to CSV"""
        try:
            df = pd.DataFrame(self.agents)
            df.to_csv(filename, index=False)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def save_final(self, city, state):
        """Final save with summary"""
        filename = f"agents_{city.replace(' ', '_')}_{state}_progress.csv"
        
        # Remove profile_url from final output
        df = pd.DataFrame(self.agents)
        final_df = df.drop('profile_url', axis=1) if 'profile_url' in df.columns else df
        final_filename = f"agents_{city.replace(' ', '_')}_{state}_FINAL.csv"
        final_df.to_csv(final_filename, index=False)
        
        # Print summary
        print("\n" + "="*70)
        print(f"RESULTS: {city}, {state}")
        print("="*70)
        print(f"Total agents: {len(self.agents)}")
        print(f"With phone: {sum(1 for a in self.agents if a.get('phone_number'))}")
        print(f"With address: {sum(1 for a in self.agents if a.get('address'))}")
        print(f"With brokerage: {sum(1 for a in self.agents if a.get('brokerage'))}")
        print(f"With license: {sum(1 for a in self.agents if a.get('agent_license'))}")
        print(f"\nProgress file: {filename}")
        print(f"Final file: {final_filename}")
        print("="*70 + "\n")
        
        return final_filename

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    print("\n" + "="*70)
    print("REALTOR.COM AGENT SCRAPER - STABLE VERSION")
    print("="*70)
    print("\nFEATURES:")
    print("  ✓ Auto-saves progress every 50 agents")
    print("  ✓ Resume from where it stopped")
    print("  ✓ Optimized for speed (images disabled)")
    print("  ✓ Browser visible (more stable)")
    print("="*70 + "\n")
    
    scraper = RealtorAgentScraperStable()
    
    try:
        city = input("Enter city name: ").strip()
        state = input("Enter state (e.g., WA for Seattle): ").strip().upper()
        
        if not city or not state:
            print("City and state required!")
            return
        
        start_time = time.time()
        
        # Search and extract
        scraper.search_city(city, state)
        
        elapsed_time = time.time() - start_time
        
        # Final save
        if scraper.agents:
            scraper.save_final(city, state)
            
            print(f"\n⚡ Total time: {elapsed_time/60:.1f} minutes")
            print(f"   Average: {elapsed_time/len(scraper.agents):.1f} seconds per agent")
            
            # Preview
            df = pd.DataFrame(scraper.agents)
            print("\nData Preview (first 5 agents):")
            print(df.head()[['name', 'phone_number', 'brokerage']].to_string(index=False))
    
    finally:
        scraper.close()
    
    print("\n" + "="*70)
    print("SCRAPING COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
