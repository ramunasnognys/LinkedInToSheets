import requests
from bs4 import BeautifulSoup
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from urllib.parse import urlparse
import time
import random

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def scrape_linkedin_job(url):
    if not is_valid_url(url):
        print(f"Invalid URL: {url}")
        return None

    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/'
    }

    session = requests.Session()

    try:
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        response = session.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    job_title = soup.find('h1', class_='top-card-layout__title')
    company_name = soup.find('a', class_='topcard__org-name-link')
    location = soup.find('span', class_='topcard__flavor--bullet')
    job_description = soup.find('div', class_='show-more-less-html__markup')
    
    if job_description:
        description_text = re.sub(r'\s+', ' ', job_description.text).strip()
    else:
        description_text = "Job description not found"

    return {
        "company": company_name.text.strip() if company_name else "Not found",
        "position": job_title.text.strip() if job_title else "Not found",
        "location": location.text.strip() if location else "Not found",
        "description": description_text
    }

def get_job_urls_and_row_data(sheet_id):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SERVICE_ACCOUNT_FILE = 'job-sheet.json'
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Read all data from A2:H
    result = sheet.values().get(spreadsheetId=sheet_id, range='A2:H').execute()
    values = result.get('values', [])
    
    return values

def update_google_sheet(job_data, sheet_id, row_number):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'job-sheet.json'
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Prepare the data to be inserted
    row_data = [
        job_data['company'],
        job_data['position'],
        job_data['location'],
        '',  # DATE (APPLIED) - left blank
        '',  # STATUS - left blank
        '',  # NOTES - left blank
        '',  # WEBSITE - we don't update this
        job_data['description']  # SKILLS - contains job description
    ]
    
    # Update the sheet
    body = {
        'values': [row_data]
    }
    result = sheet.values().update(
        spreadsheetId=sheet_id, range=f'A{row_number}:H{row_number}',
        valueInputOption='USER_ENTERED', body=body).execute()
    
    print(f"Row {row_number}: {result.get('updatedCells')} cells updated.")

if __name__ == "__main__":
    sheet_id = '1sEbe0fCYEQ45FLCCoT3BqWrpa2ZNdVTLgyJk5rBQOnc'
    
    row_data = get_job_urls_and_row_data(sheet_id)
    
    if not row_data:
        print("No data found in the sheet.")
    else:
        for index, row in enumerate(row_data, start=2):  # start=2 because row 1 is headers
            # Check if the row has any content in columns A-F (excluding WEBSITE and SKILLS)
            if any(row[:6]):
                print(f"Row {index} already has content. Skipping.")
                continue
            
            # Get the URL from column G (index 6)
            job_url = row[6] if len(row) > 6 else ''
            
            print(f"Processing URL {index-1} of {len(row_data)}: {job_url}")
            if is_valid_url(job_url):
                job_data = scrape_linkedin_job(job_url)
                if job_data:
                    update_google_sheet(job_data, sheet_id, index)
                else:
                    print(f"Failed to scrape data for URL: {job_url}")
            else:
                print(f"Invalid URL found in row {index}: {job_url}")
            
            # Add a delay between requests to avoid overwhelming the server
            time.sleep(random.uniform(3, 7))
    
    print("Job scraping and sheet updating completed.")