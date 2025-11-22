"""
Instagram Engagement Scraper

Main script that:
1. Searches Instagram for a keyword
2. Collects post URLs from search results
3. Extracts and classifies comments from each post
4. Determines high text-based engagement
5. Saves results to CSV
"""

import os
import time
import random
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
from dotenv import load_dotenv
from utils import (
    load_config,
    setup_driver,
    instagram_login,
    scroll_and_collect_comments,
    extract_creator_handle,
    save_to_csv,
    download_csv
)
from comment_classifier import classify_comment


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def search_instagram(driver, keyword, num_posts, slow_mode=0):
    """
    Search Instagram for a keyword and collect post URLs.
    
    Args:
        driver: Selenium WebDriver instance
        keyword (str): Search keyword
        num_posts (int): Number of posts to collect
        slow_mode (int): Additional delay in seconds
        
    Returns:
        list: List of post URLs
    """
    post_urls = []
    
    try:
        logger.info(f"Searching Instagram for keyword: '{keyword}'")
        
        # Direct navigation to hashtag page (most reliable method)
        hashtag_url = f"https://www.instagram.com/explore/tags/{keyword}/"
        logger.info(f"Navigating to: {hashtag_url}")
        driver.get(hashtag_url)
        time.sleep(4 + slow_mode)
        
        # Wait for posts to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            logger.info("Posts loaded successfully")
        except TimeoutException:
            logger.warning("Posts may not have loaded, continuing anyway...")
        
        # Collect post URLs by scrolling
        scroll_attempts = 0
        max_scrolls = 30
        seen_urls = set()
        no_new_posts_count = 0
        
        logger.info(f"Collecting {num_posts} post URLs...")
        
        while len(post_urls) < num_posts and scroll_attempts < max_scrolls:
            # Find all post links with multiple selectors
            post_selectors = [
                "//a[contains(@href, '/p/')]",
                "//a[contains(@href, '/reel/')]",
                "//article//a[contains(@href, '/p/')]",
                "//div[contains(@role, 'button')]//a[contains(@href, '/p/')]",
            ]
            
            post_links = []
            for selector in post_selectors:
                try:
                    links = driver.find_elements(By.XPATH, selector)
                    post_links.extend(links)
                except:
                    continue
            
            # Extract unique URLs
            previous_count = len(post_urls)
            for link in post_links:
                try:
                    href = link.get_attribute('href')
                    if href and ('/p/' in href or '/reel/' in href):
                        # Clean URL (remove query parameters)
                        clean_url = href.split('?')[0]
                        if clean_url not in seen_urls:
                            post_urls.append(clean_url)
                            seen_urls.add(clean_url)
                            if len(post_urls) >= num_posts:
                                break
                except:
                    continue
            
            # Check if we found new posts
            if len(post_urls) == previous_count:
                no_new_posts_count += 1
                if no_new_posts_count >= 3:
                    logger.warning("No new posts found after multiple scrolls, stopping...")
                    break
            else:
                no_new_posts_count = 0
            
            if len(post_urls) >= num_posts:
                break
            
            # Scroll down gradually
            scroll_amount = random.randint(500, 800)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(2, 3) + slow_mode)
            scroll_attempts += 1
            
            # Log progress
            if scroll_attempts % 5 == 0:
                logger.info(f"Progress: {len(post_urls)}/{num_posts} posts collected (scroll {scroll_attempts})")
        
        logger.info(f"Collected {len(post_urls)} unique post URLs")
        return post_urls[:num_posts]
        
    except Exception as e:
        logger.error(f"Error during Instagram search: {e}", exc_info=True)
        return post_urls


def process_post(driver, post_url, min_comments, slow_mode=0):
    """
    Process a single Instagram post: extract comments and compute metrics.
    
    Args:
        driver: Selenium WebDriver instance
        post_url (str): URL of the post to process
        min_comments (int): Minimum required comments for qualification
        slow_mode (int): Additional delay in seconds
        
    Returns:
        dict: Result dictionary with post metrics
    """
    result = {
        'creator_handle': '',
        'post_url': post_url,
        'total_comments': 0,
        'text_percentage': 0.0,
        'emoji_percentage': 0.0,
        'mixed_percentage': 0.0,
        'result': 'Fail'
    }
    
    try:
        logger.info(f"Processing post: {post_url}")
        
        # Navigate to post
        driver.get(post_url)
        time.sleep(3 + slow_mode)
        
        # Extract creator handle
        result['creator_handle'] = extract_creator_handle(driver)
        
        # Click on comments to open comments section (if needed)
        try:
            # Try to find and click comment count or comment button
            comment_selectors = [
                "//span[contains(text(), 'comment') and not(contains(text(), 'comments'))]/ancestor::button",
                "//a[contains(@href, '/p/')]//span[contains(text(), 'comment')]",
                "//button[contains(@aria-label, 'comment')]",
                "//span[contains(text(), 'comment')]/ancestor::a",
                "//article//span[contains(text(), 'comment')]",
            ]
            
            comment_opened = False
            for selector in comment_selectors:
                try:
                    comment_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if comment_element.is_displayed():
                        driver.execute_script("arguments[0].click();", comment_element)
                        time.sleep(2 + slow_mode)
                        comment_opened = True
                        logger.info("Opened comments section")
                        break
                except:
                    continue
            
            if not comment_opened:
                logger.info("Comments section may already be visible or will be extracted from page")
        except Exception as e:
            logger.warning(f"Could not open comments section explicitly: {e}. Will try to extract from page.")
        
        # Collect comments
        comments = scroll_and_collect_comments(driver, max_scroll_attempts=15, slow_mode=slow_mode)
        result['total_comments'] = len(comments)
        
        if result['total_comments'] == 0:
            logger.warning(f"No comments found for post: {post_url}")
            return result
        
        # Classify comments
        text_count = 0
        emoji_count = 0
        mixed_count = 0
        
        for comment in comments:
            classification = classify_comment(comment)
            if classification == "text":
                text_count += 1
            elif classification == "emoji":
                emoji_count += 1
            elif classification == "mixed":
                mixed_count += 1
        
        # Calculate percentages
        total = len(comments)
        result['text_percentage'] = round((text_count / total) * 100, 2)
        result['emoji_percentage'] = round((emoji_count / total) * 100, 2)
        result['mixed_percentage'] = round((mixed_count / total) * 100, 2)
        
        # Determine Pass/Fail
        text_based_count = text_count + mixed_count  # Mixed comments contain text
        text_based_percentage = (text_based_count / total) * 100
        
        if result['total_comments'] >= min_comments and text_based_percentage >= 50:
            result['result'] = 'Pass'
        else:
            result['result'] = 'Fail'
        
        logger.info(
            f"Post processed: {result['total_comments']} comments, "
            f"{result['text_percentage']}% text, Result: {result['result']}"
        )
        
        return result
        
    except TimeoutException:
        logger.error(f"Timeout while processing post: {post_url}")
        return result
    except Exception as e:
        logger.error(f"Error processing post {post_url}: {e}")
        return result


def main():
    """Main execution function."""
    try:
        # Load configuration
        config = load_config('config.yaml')
        
        keyword = config.get('keyword', 'lifestyle')
        num_posts = config.get('num_posts', 20)
        min_comments = config.get('min_comments', 50)
        output_csv = config.get('output_csv', 'output/results.csv')
        browser_config = config.get('browser', {})
        headless = browser_config.get('headless', False)
        slow_mode = browser_config.get('slow_mode', 2)
        
        # Get credentials from environment
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            logger.error("INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set in .env file")
            return
        
        # Setup driver
        driver = setup_driver(headless=headless, slow_mode=slow_mode)
        
        try:
            # Login to Instagram
            logger.info("Attempting to log into Instagram...")
            if not instagram_login(driver, username, password, slow_mode=slow_mode):
                logger.error("=" * 60)
                logger.error("LOGIN FAILED - Please check the following:")
                logger.error("=" * 60)
                logger.error("1. Verify your credentials in .env file")
                logger.error("2. Check for screenshots: login_error_*.png")
                logger.error("3. Check page source: login_page_source.html")
                logger.error("4. Run 'python test_login.py' for detailed debugging")
                logger.error("5. See LOGIN_TROUBLESHOOTING.md for solutions")
                logger.error("=" * 60)
                if not headless:
                    logger.info("Browser will stay open for 30 seconds for inspection...")
                    time.sleep(30)
                return
            
            # Search and collect post URLs
            post_urls = search_instagram(driver, keyword, num_posts, slow_mode=slow_mode)
            
            if not post_urls:
                logger.error("No posts found. Exiting.")
                return
            
            # Process each post
            results = []
            
            with tqdm(total=len(post_urls), desc="Processing posts") as pbar:
                for post_url in post_urls:
                    result = process_post(driver, post_url, min_comments, slow_mode=slow_mode)
                    results.append(result)
                    pbar.update(1)
                    
                    # Random delay between posts to avoid rate limiting
                    time.sleep(random.uniform(3, 5) + slow_mode)
            
            # Save results to CSV
            save_to_csv(results, output_csv)
            
            # Print summary
            pass_count = sum(1 for r in results if r['result'] == 'Pass')
            logger.info(f"\n{'='*50}")
            logger.info(f"Scraping completed!")
            logger.info(f"Total posts processed: {len(results)}")
            logger.info(f"Posts that passed: {pass_count}")
            logger.info(f"Posts that failed: {len(results) - pass_count}")
            logger.info(f"Results saved to: {output_csv}")
            logger.info(f"{'='*50}")
            
            # Prompt user to download/open CSV
            try:
                print("\n" + "="*50)
                user_input = input("Do you want to open/download the CSV file? (y/n): ").strip().lower()
                
                if user_input in ['y', 'yes']:
                    # Ask for additional options
                    copy_input = input("Copy to Downloads folder? (y/n): ").strip().lower()
                    copy_to_downloads = copy_input in ['y', 'yes']
                    
                    download_csv(output_csv, open_file=True, copy_to_downloads=copy_to_downloads)
                else:
                    logger.info(f"CSV file saved at: {output_csv}")
            except (KeyboardInterrupt, EOFError):
                logger.info("Skipping download prompt")
            
        finally:
            # Close driver
            driver.quit()
            logger.info("Browser closed")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

