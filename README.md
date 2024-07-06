# LinkedInToSheets
---
 ## LinkedIn Job Scraper and Google Sheets Updater

This Python script automates the process of scraping job details from LinkedIn job postings and updating a Google Sheet with the collected information. It's designed to help job seekers efficiently track and organize job applications.

## Features

- Scrapes job details from LinkedIn job postings
- Updates a Google Sheet with the scraped information
- Implements measures to bypass basic scraping protections
- Uses Google Sheets API for seamless integration

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher installed
- A Google Cloud Platform account with Google Sheets API enabled
- A service account key file (JSON) for Google Sheets API authentication

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/linkedin-job-scraper.git
   cd linkedin-job-scraper
   ```

2. Install the required Python packages:
   ```
   pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. Place your Google Sheets API service account key file (named `job-sheet.json`) in the same directory as the script.

## Configuration

1. Open `app.py` and replace the `sheet_id` variable with your Google Sheet ID:
   ```python
   sheet_id = 'your-google-sheet-id-here'
   ```

2. Ensure your Google Sheet has the following columns in order:
   - Company
   - Position
   - Location
   - Date Applied
   - Status
   - Notes
   - Website
   - Skills/Description

## Usage

1. Run the script:
   ```
   python3 app.py
   ```

2. When prompted, enter the full LinkedIn job posting URL.

3. The script will scrape the job details and update your Google Sheet with the information.

## How It Works

1. The script uses `requests` and `BeautifulSoup` to scrape job details from the LinkedIn job posting.
2. It implements measures to bypass basic scraping protections, such as random user agents and request delays.
3. The scraped data is then formatted and sent to the specified Google Sheet using the Google Sheets API.

## Limitations

- Web scraping may violate LinkedIn's terms of service. Use this script responsibly and at your own risk.
- The script may break if LinkedIn changes its HTML structure.
- There's a possibility of being blocked by LinkedIn if used excessively.

## Contributing

Contributions to improve the script are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the original branch: `git push origin feature-branch-name`.
5. Create the pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Disclaimer

This script is for educational purposes only. The user is responsible for complying with LinkedIn's terms of service and any applicable laws or regulations.