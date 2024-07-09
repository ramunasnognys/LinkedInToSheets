import requests
from bs4 import BeautifulSoup
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from urllib.parse import urlparse
import time
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# List of common tech skills (expand this list as needed)
COMMON_SKILLS = set([
    "javascript", "python", "java", "c++", "c#", "ruby", "php", "swift", "kotlin", "go",
    "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "asp.net",
    "html", "css", "sass", "less", "bootstrap", "tailwind",
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
    "machine learning", "deep learning", "artificial intelligence", "data science",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "agile", "scrum", "kanban", "jira", "confluence",
    "restful api", "graphql", "soap", "microservices", "serverless",
    "linux", "unix", "windows", "macos",
    "cybersecurity", "networking", "cloud computing",
    "react native", "flutter", "xamarin", "unity", "unreal engine",
    "blockchain", "ethereum", "solidity", "smart contracts",
    "ar/vr", "iot", "big data", "hadoop", "spark",
    "devops", "ci/cd", "test-driven development", "continuous integration",
    "webpack", "babel", "eslint", "prettier",
    "restful apis", "graphql", "websockets",
    "responsive design", "progressive web apps",
    "typescript", "rust", "scala", "haskell", "erlang",
    "agile methodologies", "scrum", "kanban",
    "version control", "git", "svn", "mercurial",
    "data visualization", "d3.js", "tableau", "power bi",
    "natural language processing", "computer vision",
    "robotics", "quantum computing",
    "elasticsearch", "logstash", "kibana", "elk stack",
    "redux", "mobx", "vuex", "ngrx",
    "webpack", "rollup", "parcel",
    "jest", "mocha", "jasmine", "selenium",
    "webgl", "three.js",
    "progressive web apps", "service workers",
    "webassembly", "emscripten",
    "apache kafka", "rabbitmq", "redis",
    "memcached", "varnish", "nginx",
    "opencv", "keras",
    "ansible", "puppet", "chef", "terraform",
    "prometheus", "grafana",
    "oauth", "jwt", "openid connect",
    "grpc", "protocol buffers",
    "webrtc", "socket.io",
    "jenkins", "travis ci", "circleci", "gitlab ci",
    "docker swarm", "mesos",
    "istio", "envoy", "linkerd",
    "openshift", "rancher", "helm",
    "datadog",
    "splunk", "sumo logic",
    "apache airflow", "luigi", "prefect",
    "apache flink", "apache beam",
    "databricks", "snowflake", "bigquery",
    "tensorflow extended (tfx)", "kubeflow",
    "mlflow", "dvc", "weights & biases",
    "pytorch lightning", "fastai", "hugging face transformers",
    "openai gym", "ray", "rllib",
    "apache cassandra", "scylladb", "cockroachdb",
    "neo4j", "arangodb", "orientdb",
    "influxdb", "timescaledb", "questdb",
    "ipfs", "filecoin", "storj",
    "assemblyscript",
    "kotlin multiplatform",
    "ionic",
    "godot",
    "arkit", "arcore", "vuforia",
    "openxr", "webxr", "a-frame",
    "stable diffusion", "dall-e", "midjourney",
    "gpt-3", "bert", "t5",
    "openai", "deepmind", "anthropic"
])

def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False
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

def extract_skills(description):
    # Tokenize the description
    tokens = word_tokenize(description.lower())
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Extract skills
    extracted_skills = []
    for skill in COMMON_SKILLS:
        if skill.lower() in ' '.join(tokens):
            extracted_skills.append(skill)
    
    return list(set(extracted_skills))  # Remove duplicates

def scrape_linkedin_job(url):
    if not is_valid_url(url):
        print(f"Invalid URL in scrape_linkedin_job: {url}")
        return None

    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/'
    }

    session = requests.Session()

    try:
        time.sleep(random.uniform(1, 3))
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
        skills = extract_skills(description_text)
    else:
        description_text = "Job description not found"
        skills = []

    return {
        "company": company_name.text.strip() if company_name else "Not found",
        "position": job_title.text.strip() if job_title else "Not found",
        "location": location.text.strip() if location else "Not found",
        "description": description_text,
        "skills": ", ".join(skills)
    }

def get_job_urls_and_row_data(sheet_id):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SERVICE_ACCOUNT_FILE = 'job-sheet.json'
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Read all data from A2:J
    result = sheet.values().get(spreadsheetId=sheet_id, range='A2:J').execute()
    values = result.get('values', [])
    
    return values

def update_google_sheet(job_data, sheet_id, row_number):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'job-sheet.json'
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # First, read the existing content of the row
    result = sheet.values().get(spreadsheetId=sheet_id, range=f'A{row_number}:J{row_number}').execute()
    existing_row_data = result.get('values', [['' for _ in range(10)]])[0]
    
    # Prepare the data to be inserted
    row_data = [
        job_data['company'],
        job_data['position'],
        job_data['location'],
        existing_row_data[3],  # DATE
        existing_row_data[4],  # DATE (APPLIED)
        existing_row_data[5],  # STATUS
        existing_row_data[6],  # NOTES
        existing_row_data[7],  # WEBSITE - keep existing data
        job_data['description'],  # Description
        job_data['skills']  # Skills
    ]
    
    # Update the sheet
    body = {
        'values': [row_data]
    }
    result = sheet.values().update(
        spreadsheetId=sheet_id, range=f'A{row_number}:J{row_number}',
        valueInputOption='USER_ENTERED', body=body).execute()
    
    print(f"Row {row_number}: {result.get('updatedCells')} cells updated.")

if __name__ == "__main__":
    sheet_id = '1sEbe0fCYEQ45FLCCoT3BqWrpa2ZNdVTLgyJk5rBQOnc'
    
    row_data = get_job_urls_and_row_data(sheet_id)
    
    if not row_data:
        print("No data found in the sheet.")
    else:
        print(f"Total rows found: {len(row_data)}")
        for index, row in enumerate(row_data, start=2):
            print(f"\nProcessing row {index}:")
            print(f"Row data: {row}")
            
            # Check if the row has any content in columns A-G (excluding WEBSITE, Description, and Skills)
            if any(row[:7]):
                print(f"Row {index} already has content. Skipping.")
                continue
            
            # Get the URL from column H (index 7)
            job_url = row[7] if len(row) > 7 else ''
            
            print(f"URL found: {job_url}")
            if is_valid_url(job_url):
                print("URL is valid. Scraping...")
                job_data = scrape_linkedin_job(job_url)
                if job_data:
                    update_google_sheet(job_data, sheet_id, index)
                else:
                    print(f"Failed to scrape data for URL: {job_url}")
            else:
                print(f"Invalid URL found in row {index}: {job_url}")
            
            time.sleep(random.uniform(3, 7))
    
    print("Job scraping and sheet updating completed.")