# Realtor-Agent-Scraper
  A robust Python-based web scraper for extracting real estate agent information from realtor.com.
# Realtor Agent Scraper

A robust Python-based web scraper for extracting real estate agent information from realtor.com. Built with Selenium and BeautifulSoup, this tool automatically collects agent details across multiple pages with progress tracking and resume capabilities.

## Features

✨ **Core Capabilities**
- 🔍 Search for real estate agents by city and state
- 📄 Auto-pagination through all search results
- 💾 Automatic progress saving every 50 agents
- ⏯️ Resume from where it stopped
- ⚡ Optimized for speed (images disabled)
- 🌐 Browser-visible mode for stability

**Data Extraction**
- Agent name
- Phone number (mobile & office)
- Office address
- Brokerage/Company name
- License number
- Profile URL (for tracking)

## Requirements

- Python 3.8+
- Chrome/Chromium browser installed
- Dependencies listed in `requirements.txt`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/realtor-agent-scraper.git
cd realtor-agent-scraper
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Main Dependencies:**
- `undetected-chromedriver==3.5.4` - Undetected Chrome automation
- `selenium==4.15.2` - Web driver control
- `beautifulsoup4==4.12.2` - HTML parsing
- `pandas==2.0.3` - Data handling

## Usage

### Basic Usage
```bash
python agent_scraper_stable.py
```

The script will prompt you for:
1. **City name**: Enter the city (e.g., "London", "Seattle")
2. **State code**: Enter the state abbreviation (e.g., "KY", "WA", "NY")

### Example
```
Enter city name: Seattle
Enter state (e.g., WA for Seattle): WA
```

### What Happens
1. Opens Chrome browser (visible for stability)
2. Navigates to realtor.com agent search
3. Automatically clicks through all pagination pages
4. Collects agent profile URLs
5. Scrapes detailed information from each profile
6. Saves progress every 50 agents
7. Generates final CSV with all results

## Output Files

Two CSV files are generated:

### Progress File
`agents_[City]_[State]_progress.csv`
- Contains internal tracking data
- Includes profile URLs for resume capability
- Used for resuming interrupted scraping

### Final Output
`agents_[City]_[State]_FINAL.csv`
- Clean data without tracking columns
- Ready for analysis/reporting
- Contains all extracted agent information

**Example Output Structure:**
```csv
name,phone_number,address,brokerage,agent_license
John Smith,"(206) 555-1234","123 Main St, Seattle, WA 98101",Smith Realty Group,123456
Jane Doe,"(206) 555-5678","456 Oak Ave, Seattle, WA 98102",Pacific Real Estate,654321
```

## Performance

- **Average Speed**: ~1-2 seconds per agent
- **Pagination**: Handles 40+ pages automatically
- **Large Cities**: Can collect 500+ agents in one session
- **Resume**: Instantly skip already-scraped agents

## Project Structure

```
realtor-agent-scraper/
├── agent_scraper_stable.py       # Main scraper (production-ready)
├── agent_scraper_final.py        # Alternative implementation
├── agent_scraper_optimized.py    # Performance-optimized version
├── README.md                      # This file
├── requirements.txt               # Python dependencies
└── agents_*.csv                   # Generated output files
```

## Advanced Features

### Resume Capability
If scraping is interrupted:
1. Run the script again with the same city/state
2. Script detects existing progress file
3. Automatically skips already-scraped agents
4. Continues from where it stopped

### Batch Processing
Modify `main()` function to process multiple cities:
```python
cities = [
    ("Seattle", "WA"),
    ("London", "KY"),
    ("New York", "NY")
]

for city, state in cities:
    scraper = RealtorAgentScraperStable()
    scraper.search_city(city, state)
    scraper.close()
```

## Configuration

Edit these values in `RealtorAgentScraperStable` class:

```python
self.save_frequency = 50  # Save every 50 agents
# Adjust based on your needs and system resources
```

### Chrome Options
Modify in `setup_driver()`:
- `version_main=134` - Chrome version (update if needed)
- Disable/enable image loading
- Adjust headless mode (currently disabled for stability)

## Troubleshooting

### Chrome Version Mismatch
```
Error: Chrome version mismatch
Solution: Update Chrome browser or adjust version_main parameter
```

### Timeout Errors
```
Solution: Increase sleep times in code:
- search_input.send_keys(Keys.RETURN) - wait after
- time.sleep() values - increase by 0.5-1 seconds
```

### No Results Found
- Verify city/state spelling
- Check internet connection
- Try with a different city
- realtor.com may have changed page structure

### SSL/Certificate Errors
```bash
pip install --upgrade certifi
```

## Data Quality Notes

⚠️ **Important**
- Phone numbers: May include both mobile and office numbers
- Address: Extracted from page text (may vary in format)
- Brokerage: Best-guess extraction from available text
- License: Not always visible on every profile page
- Some fields may be empty (N/A) for certain agents

## Limitations

- ⚠️ Respects website terms of service - Use responsibly
- Rate-limited to human-like speeds
- Requires visible browser (performance trade-off for stability)
- Images disabled to improve speed
- Limited to realtor.com data only

## Legal & Ethical

- **Use responsibly**: Check realtor.com's Terms of Service
- **Rate limiting**: Script includes delays to avoid server overload
- **Personal use**: Intended for research and analysis
- **Commercial use**: Verify compliance with realtor.com policies

## Contributing

Contributions welcome! Areas for improvement:
- Mobile detection bypass improvements
- Additional data fields extraction
- Proxy support
- Async scraping
- Error recovery mechanisms

## Roadmap

- [ ] Support for other real estate platforms
- [ ] Proxy rotation for large-scale scraping
- [ ] Database integration
- [ ] Email notification on completion
- [ ] Web interface for easier use
- [ ] Async/concurrent scraping

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is provided for educational purposes. Users are responsible for ensuring compliance with:
- realtor.com Terms of Service
- Local and applicable laws
- Ethical web scraping practices
- Data privacy regulations

## Support

### Common Issues
1. **Script runs but no data collected**: Website structure may have changed
2. **Slow performance**: Disable your VPN, check internet speed
3. **Progress file corruption**: Delete and restart scraping

### Debug Mode
Enable logging to see detailed operation:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Credits

Built with:
- [Undetected ChromeDriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [Selenium](https://www.selenium.dev/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Pandas](https://pandas.pydata.org/)

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: Production Ready ✅

For issues, questions, or suggestions, please open an issue on GitHub.
