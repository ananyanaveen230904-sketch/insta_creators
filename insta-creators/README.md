# Instagram Engagement Scraper

A Python + Selenium tool that automatically searches Instagram, extracts comments from posts, classifies them, and determines high text-based engagement.

## Project Overview

This tool automates the process of:
1. Searching Instagram for a keyword (default: "lifestyle")
2. Collecting post URLs from search/explore results
3. Extracting all comments from each post using browser automation
4. Classifying comments into:
   - **Text comments**: Contains letters/numbers but no emojis
   - **Emoji-only comments**: Contains only emojis
   - **Mixed comments**: Contains both emojis and text
5. Determining whether posts qualify as "high text-based engagement"
   - Must have ≥ minimum required comments (default: 50)
   - At least 50% comments must be text-based
6. Saving results to a CSV file with creator metadata and engagement metrics

## Quick Start

```bash
git clone <repo>
cd <repo-folder-name>
pip install -r requirements.txt
python scraper.py


## Project Structure

```
instagram-engagement/
│── scraper.py              # Main script
│── comment_classifier.py   # Comment classification logic
│── utils.py                # Utility functions
│── config.yaml             # Configuration file
│── requirements.txt        # Python dependencies
│── README.md               # This file
│── .env                    # Environment variables (create this)
│── output/
│    └── results.csv        # Output file (generated)
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ChromeDriver

The script requires ChromeDriver to be installed and accessible in your PATH.

**Windows:**
- Download ChromeDriver from https://chromedriver.chromium.org/
- Extract and add to PATH, or place in the same directory as the script
- Ensure Chrome browser is installed

**macOS:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
```

### 3. Create `.env` File

Create a `.env` file in the project root with your Instagram credentials:

```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

**⚠️ IMPORTANT:** Never commit the `.env` file to version control!

### 4. Configure Settings

Edit `config.yaml` to customize:
- `keyword`: Search keyword (default: "lifestyle")
- `num_posts`: Number of posts to process (default: 20)
- `min_comments`: Minimum comments required (default: 50)
- `output_csv`: Output file path
- `browser.headless`: Run browser in background (true/false)
- `browser.slow_mode`: Additional delay in seconds (helps avoid detection)

## How to Run

1. Ensure all dependencies are installed
2. Create `.env` file with Instagram credentials
3. Configure `config.yaml` if needed
4. Run the script:

```bash
python scraper.py
```

The script will:
- Log into Instagram
- Search for the configured keyword
- Collect post URLs
- Process each post (extract and classify comments)
- Save results to CSV
- Prompt you to open/download the CSV file (optional)

Progress will be displayed with a progress bar and detailed logging.

## Output CSV Format

The output CSV contains the following columns:

- `creator_handle`: Instagram handle of the post creator
- `post_url`: Full URL of the Instagram post
- `total_comments`: Total number of comments extracted
- `text_percentage`: Percentage of text-only comments
- `emoji_percentage`: Percentage of emoji-only comments
- `mixed_percentage`: Percentage of mixed comments
- `result`: "Pass" or "Fail" based on engagement criteria

## CSV Download Feature

After scraping completes, the script will prompt you with:

```
Do you want to open/download the CSV file? (y/n):
```

**If you choose 'y' or 'yes':**
- The CSV file will automatically open in your default application (Excel, CSV viewer, etc.)
- You'll be asked if you want to copy it to your Downloads folder:
  ```
  Copy to Downloads folder? (y/n):
  ```
- If you choose 'y', a copy will be saved to your Downloads folder

**If you choose 'n' or 'no':**
- The CSV file remains saved at the configured location (default: `output/results.csv`)
- You can manually open it later

**Note:** The CSV file is always saved to the location specified in `config.yaml` (default: `output/results.csv`), regardless of your download choice.

## Logging, Error Handling & Progress Tracking

This project includes comprehensive logging, robust error handling, and real-time progress tracking to help you monitor the scraping process and troubleshoot issues.

### Logging System

The scraper uses Python's built-in `logging` module with the following features:

- **Dual Output**: Logs are written to both:
  - **Console**: Real-time output while the script runs
  - **Log File**: `instagram_scraper.log` (persistent record of all operations)

- **Log Format**: Each log entry includes:
  - Timestamp
  - Log level (INFO, WARNING, ERROR)
  - Detailed message

- **Log Levels Used**:
  - `INFO`: General progress updates, successful operations
  - `WARNING`: Non-critical issues (e.g., element not found, using fallback method)
  - `ERROR`: Critical failures that may stop execution

- **Comprehensive Coverage**: Logs are generated for:
  - Configuration loading
  - Browser driver initialization
  - Login attempts and results
  - Post URL collection progress
  - Comment extraction progress
  - CSV saving operations
  - Error conditions and troubleshooting hints

**Example log output:**
```
2024-01-15 10:30:45 - INFO - Configuration loaded from config.yaml
2024-01-15 10:30:46 - INFO - Chrome driver initialized successfully
2024-01-15 10:30:47 - INFO - Attempting to log into Instagram...
2024-01-15 10:30:52 - INFO - Login successful! Detected Instagram home page elements.
2024-01-15 10:30:53 - INFO - Searching Instagram for keyword: 'lifestyle'
2024-01-15 10:31:10 - INFO - Collected 15 unique post URLs
2024-01-15 10:31:11 - INFO - Processing post: https://www.instagram.com/p/...
```

### Error Handling

The project implements robust error handling throughout:

- **Try-Except Blocks**: All critical operations are wrapped in try-except blocks
- **Specific Exception Handling**: Catches and handles:
  - `TimeoutException`: When elements don't load in time
  - `NoSuchElementException`: When expected elements aren't found
  - `ElementClickInterceptedException`: When clicks are blocked
  - `FileNotFoundError`: For missing configuration files
  - `KeyboardInterrupt`: Graceful handling of user cancellation

- **Graceful Degradation**: 
  - Multiple fallback selectors for finding elements
  - Alternative methods when primary approaches fail
  - Continues processing other posts even if one fails

- **Error Recovery**:
  - Automatic retries with different selectors
  - Detailed error messages with troubleshooting steps
  - Screenshots saved for debugging (e.g., `login_error_*.png`)
  - Page source saved for analysis (`login_page_source.html`)

- **User-Friendly Error Messages**: 
  - Clear explanations of what went wrong
  - Actionable troubleshooting steps
  - References to relevant documentation files

**Example error handling:**
```python
try:
    # Attempt operation
    element = driver.find_element(By.XPATH, selector)
except TimeoutException:
    logger.warning("Element not found, trying alternative selector...")
    # Try fallback method
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)  # Includes full traceback
```

### Progress Tracking

Real-time progress tracking helps you monitor the scraping process:

- **Progress Bar**: Uses `tqdm` library to display a visual progress bar:
  ```
  Processing posts: 45%|████████████        | 9/20 [02:15<02:45]
  ```

- **Progress Logging**: 
  - Post collection progress logged every 5 scroll attempts
  - Comment collection progress logged every 5 scroll attempts
  - Current status displayed in real-time

- **Summary Statistics**: At the end of scraping, displays:
  - Total posts processed
  - Number of posts that passed/failed
  - CSV file location
  - Processing time information

- **Detailed Progress Messages**:
  - Shows current step (e.g., "Processing post 5 of 20")
  - Displays comment collection progress
  - Reports successful operations

**Example progress output:**
```
2024-01-15 10:31:15 - INFO - Progress: 5/15 posts collected (scroll 10)
2024-01-15 10:31:20 - INFO - Comment collection progress: 45 comments (attempt 5)
2024-01-15 10:32:00 - INFO - Collected 67 unique comments after 12 scroll attempts
```

### Debugging Features

When errors occur, the scraper automatically:

1. **Saves Screenshots**: 
   - `login_error_*.png`: Screenshots of login failures
   - `login_error_detected.png`: When specific error messages are detected
   - Helps visualize what the browser sees

2. **Saves Page Source**: 
   - `login_page_source.html`: Full HTML of the page when errors occur
   - Useful for analyzing Instagram's response

3. **Detailed Error Traces**: 
   - Full stack traces with `exc_info=True`
   - Helps identify the exact line where errors occur

4. **Test Script**: 
   - `test_login.py`: Standalone script to test login without full scraping
   - Useful for debugging login issues in isolation

### Monitoring Your Scraping Session

To monitor your scraping session:

1. **Watch the Console**: Real-time updates show current progress
2. **Check the Log File**: `instagram_scraper.log` contains the complete history
3. **Review Progress Bar**: Visual indicator of completion percentage
4. **Check for Error Files**: Look for `login_error_*.png` if issues occur

**Tip**: Keep the log file open in a text editor to monitor progress, or use `tail -f instagram_scraper.log` on Linux/Mac to watch it in real-time.

## Instagram Login & Cookies

### Using Credentials (Current Method)

The script uses your Instagram username and password from the `.env` file. This is the simplest method but may trigger security checks.

### Alternative: Using Cookies (Advanced)

If you encounter login issues, you can use saved cookies:

1. **Manually log into Instagram** in Chrome
2. **Export cookies** using a browser extension (e.g., "Cookie-Editor")
3. **Save cookies** as JSON and load them in the script

To implement cookie-based login, modify `utils.py`:

```python
def load_cookies(driver, cookie_file):
    """Load cookies from JSON file."""
    import json
    driver.get("https://www.instagram.com/")
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
```

## Troubleshooting

### Rate Limits & Blocked Requests

**Symptoms:**
- "Try Again Later" messages
- Login failures
- Posts not loading

**Solutions:**
1. **Increase `slow_mode`** in `config.yaml` (e.g., set to 5-10 seconds)
2. **Reduce `num_posts`** to process fewer posts per session
3. **Add delays** between actions (already implemented with random delays)
4. **Use a VPN** or different IP address
5. **Wait 24 hours** if temporarily blocked
6. **Use Instagram's official API** for production use (requires approval)

### Login Issues

**Symptoms:**
- "Sorry, your password was incorrect"
- "Please wait a few minutes before you try again"
- Two-factor authentication prompts
- "Login failed" error

**Quick Debug:**
1. **Run the test script first:**
   ```bash
   python test_login.py
   ```
   This will help identify the exact issue and save debugging screenshots.

**Solutions:**
1. **Verify credentials** in `.env` file:
   - Check for typos
   - Ensure no extra spaces
   - Try logging in manually on Instagram website first
2. **Check generated files:**
   - Look at `login_error_*.png` screenshots
   - Check `login_page_source.html` for error messages
3. **Disable 2FA temporarily** for testing (not recommended for security)
4. **Use cookie-based authentication** (see above)
5. **Wait before retrying** if rate-limited (1-2 hours)
6. **Check for Instagram security emails** and verify account
7. **See detailed guide:** `LOGIN_TROUBLESHOOTING.md`

### Slow Loading / Timeout Errors

**Symptoms:**
- Elements not found
- Timeout exceptions
- Comments not loading

**Solutions:**
1. **Check internet connection**
2. **Increase timeout values** in the code (currently 10-15 seconds)
3. **Reduce `num_posts`** to process fewer posts
4. **Run in non-headless mode** to see what's happening
5. **Update ChromeDriver** to match your Chrome version

### Infinite Scrolling Failures

**Symptoms:**
- Not all comments are collected
- Script stops scrolling prematurely

**Solutions:**
1. **Increase `max_scroll_attempts`** in `scroll_and_collect_comments()`
2. **Check Instagram's comment loading behavior** (may have changed)
3. **Verify XPath selectors** are still valid (Instagram updates UI frequently)
4. **Add more wait conditions** for comment elements

### ChromeDriver Issues

**Symptoms:**
- "chromedriver executable needs to be in PATH"
- Version mismatch errors

**Solutions:**
1. **Download matching ChromeDriver version** from https://chromedriver.chromium.org/
2. **Check Chrome version**: `chrome://version/` in browser
3. **Use Selenium Manager** (auto-downloads driver in Selenium 4.6+)
4. **Add ChromeDriver to PATH** or place in project directory

### No Comments Found

**Symptoms:**
- `total_comments: 0` in results
- Comments section not opening

**Solutions:**
1. **Posts may have comments disabled**
2. **XPath selectors may need updating** (Instagram UI changes)
3. **Check if comments require login** (should be logged in)
4. **Verify post URL is accessible**

## Best Practices

1. **Respect Rate Limits**: Don't scrape too aggressively
2. **Use Delays**: The script includes random delays to appear more human-like
3. **Monitor Logs**: 
   - Check `instagram_scraper.log` for detailed operation history
   - Watch console output for real-time progress
   - Review error screenshots (`login_error_*.png`) if issues occur
4. **Test Small First**: Start with `num_posts: 5` to test before larger runs
5. **Use Test Script**: Run `python test_login.py` to debug login issues separately
6. **Keep Updated**: Instagram changes frequently; update selectors as needed
7. **Check Progress Bar**: Monitor the tqdm progress bar to track completion
8. **Review Error Messages**: The script provides detailed error messages with troubleshooting steps
9. **Legal Compliance**: Ensure you comply with Instagram's Terms of Service

## Code Architecture

- **`scraper.py`**: Main orchestration script
- **`comment_classifier.py`**: Comment classification using regex
- **`utils.py`**: Reusable utility functions (config, driver, login, CSV)
- **`config.yaml`**: Centralized configuration
- **Modular design**: Easy to extend and maintain

## Dependencies

- **selenium**: Browser automation
- **python-dotenv**: Environment variable management
- **pyyaml**: YAML configuration parsing
- **pandas**: CSV data handling
- **tqdm**: Progress bars

## Notes

- Instagram's UI changes frequently; XPath selectors may need updates
- The script includes anti-detection measures but may still trigger rate limits
- For production use, consider Instagram's official API
- Always respect Instagram's Terms of Service and robots.txt

## License

This project is for educational purposes. Use responsibly and in compliance with Instagram's Terms of Service.

