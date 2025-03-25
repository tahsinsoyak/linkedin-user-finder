import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

class LinkedInScraper:
    def __init__(self, email, password):
            self.email = email
            self.password = password
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-notifications')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
        
    def login(self):
        """Login to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.random_sleep(0, 1)  # Added delay after page load
            
            self.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.email)
            self.random_sleep(0, 1)  # Added delay after username
            
            self.wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(self.password)
            self.random_sleep(0, 1)  # Added delay after password
            
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))).click()
            self.random_sleep(0, 1)  # Added delay after click
            
            # Verify login success
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module")))
                print("Successfully logged in to LinkedIn")
            except TimeoutException:
                print("Login might have failed - please check if you're logged in")
                
            self.random_sleep(3, 5)  # Existing delay
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.quit()

    # Add this helper method to the LinkedInScraper class
    def save_screenshot(self, name="debug"):
        """Save a screenshot for debugging"""
        try:
            self.driver.save_screenshot(f"screenshot_{name}.png")
            print(f"Saved screenshot as screenshot_{name}.png")
        except Exception as e:
            print(f"Failed to save screenshot: {str(e)}")
    def search_profiles(self, keywords):
        """Search for profiles based on keywords"""
        try:
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            self.driver.get(search_url)
            self.random_sleep(2, 4)  # Wait for page load
            
            # Wait for search results to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container")))
            
            # Find all profile links with the specific class and href pattern
            profile_links = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "a.pitWIDpwSQjnTZEObWBMaQTiXHUJwNBg[href*='/in/']"
            )
            
            profile_urls = []
            for link in profile_links:
                try:
                    url = link.get_attribute('href')
                    # Clean up the URL by removing tracking parameters
                    if url:
                        base_url = url.split('?')[0]
                        if base_url not in profile_urls:  # Avoid duplicates
                            name = link.text.strip()
                            if name and "LinkedIn Member" not in name:
                                profile_urls.append(base_url)
                                print(f"Found profile: {name} - {base_url}")
                except Exception as e:
                    print(f"Error processing link: {str(e)}")
                    continue
            
            if not profile_urls:
                print("No profiles found - saving screenshot for debugging")
                self.save_screenshot("search_results")
            
            return profile_urls[:10]  # Limit to first 10 profiles
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            self.save_screenshot("search_error")
            return []
            
    def extract_profile_data(self, profile_url):
        """Extract data from a profile"""
        try:
            self.driver.get(profile_url)
            self.random_sleep(0, 1)
            self.random_sleep(2, 4)
            
            name = self._get_element_text("h1.inline.t-24.v-align-middle.break-words")
            company = self._get_element_text("div.inline-show-more-text--is-collapsed.inline-show-more-text--is-collapsed-with-line-clamp")
            
            data = {
                'name': name,
                'headline': self._get_element_text("div.text-body-medium.break-words"),
                'location': self._get_element_text("span.text-body-small.inline.t-black--light.break-words"),
                'company': company,
                'email': self._find_email()
            }
            
            # If no email found, generate potential variations
            if not data['email']:
                potential_emails = self._generate_email(company, name)
                if potential_emails:
                    data['potential_emails'] = ', '.join(potential_emails)
                    print(f"Generated potential emails for {name}:")
                    for email in potential_emails:
                        print(f"  - {email}")
                
            return data
            
        except Exception as e:
            print(f"Data extraction failed: {str(e)}")
            return None
            
    def random_sleep(self,min_seconds=2, max_seconds=5):
        """Helper function for random delays"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    def _get_element_text(self, selector):
        """Helper method to get element text"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return ""
            
    def _find_email(self):
        """Try to find email on profile"""
        try:
            contact_info = self.driver.find_element(By.CSS_SELECTOR, "a[data-control-name='contact_see_more']")
            contact_info.click()
            self.random_sleep(0, 1)  # Added delay after click
            
            email_element = self.driver.find_element(By.CSS_SELECTOR, "a[href^='mailto:']")
            self.random_sleep(0, 1)  # Added delay after finding email
            email = email_element.text.strip()
            if email:
                return email
            else:
                print("No email found")
        except:
            return  None
            
    def _generate_email(self, company, name=None):
        """Generate potential email variations"""
        if not company:
            return []
            
        try:
            # Search for company website
            search_url = f"https://www.google.com/search?q={company}+website"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            website = soup.find('cite')
            
            if not website:
                return []
                
            domain = website.text.split('//')[1].split('/')[0]
            email_variations = []
            
            # Add standard contact emails
            standard_emails = [
                f"info@{domain}",
                f"contact@{domain}",
                f"hello@{domain}",
                f"sales@{domain}",
                f"export@{domain}"
            ]
            email_variations.extend(standard_emails)
            
            # If we have a name, generate personalized variations
            if name:
                name_parts = name.lower().strip().split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    
                    # Common email patterns
                    personal_emails = [
                        f"{first_name}@{domain}",
                        f"{first_name}.{last_name}@{domain}",
                        f"{first_name[0]}{last_name}@{domain}",
                        f"{first_name}_{last_name}@{domain}",
                        f"{last_name}.{first_name}@{domain}",
                        f"{first_name[0]}.{last_name}@{domain}",
                        f"{first_name}-{last_name}@{domain}",
                        f"{last_name}{first_name[0]}@{domain}",
                        f"{first_name}{last_name[0]}@{domain}"
                    ]
                    email_variations.extend(personal_emails)
            
            return email_variations
            
        except Exception as e:
            print(f"Error generating emails: {str(e)}")
            return []
        
    def save_to_csv(self, data, filename):
        """Save scraped data to CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            print(f"Failed to save CSV: {str(e)}")
            
    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize scraper with your LinkedIn credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        return
        
    scraper = LinkedInScraper(email, password)
    
    try:
        # Login
        scraper.login()
        scraper.random_sleep(5, 8)  # Wait after login
        
        # Get company and position keywords
        company = input("Enter company name: ")
        positions = [
            "Export Manager",
        ]
        
        all_data = []
        
        # Search for each position with delays
        for position in positions:
            keywords = f"{company} {position}"
            print(f"\nSearching for: {keywords}")
            
            # Get profiles from first page
            profile_urls = scraper.search_profiles(keywords)
            print(f"Found {len(profile_urls)} profiles")
            
            # Extract data from each profile
            for url in profile_urls:
                print(f"Processing profile: {url}")
                profile_data = scraper.extract_profile_data(url)
                if profile_data:
                    all_data.append(profile_data)
                    print("Successfully extracted profile data")
                scraper.random_sleep(4, 7)  # Longer delay between profile visits
            
            scraper.random_sleep(5, 8)  # Delay between searches
            
        # Save results
        if all_data:
            scraper.save_to_csv(all_data, f"linkedin_profiles_{company}.csv")
            print(f"Saved {len(all_data)} profiles to CSV")
        else:
            print("No profiles were found or extracted")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()

