# LinkedIn Job Scraping API

This API provides endpoints to automatically scrape job listings from LinkedIn using keywords and various filters.

## Features

- 🔍 **Keyword-based job search** - Search jobs using any keywords
- 📍 **Location filtering** - Filter jobs by location or remote work
- 🎯 **Experience level filtering** - Filter by career level (internship, entry, mid, senior, etc.)
- 💼 **Job type filtering** - Filter by employment type (full-time, part-time, contract, etc.)
- 📄 **Detailed job information** - Get complete job descriptions from LinkedIn URLs
- 🚀 **Fast and reliable** - Built with Selenium WebDriver for accurate scraping

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Chrome Browser

The scraper uses Chrome WebDriver, so you need Chrome installed:

**Ubuntu/Debian:**
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download and install from https://www.google.com/chrome/

### 3. Start the API Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### 1. Search LinkedIn Jobs

**Endpoint:** `POST /api/v1/jobs/linkedin/search`

**Description:** Search for jobs on LinkedIn using keywords and optional filters.

**Request Body:**
```json
{
  "keywords": "python developer",
  "location": "New York",
  "max_results": 25,
  "experience_level": "mid",
  "job_type": "full-time"
}
```

**Parameters:**
- `keywords` (required): Job search keywords (e.g., "python developer", "data scientist")
- `location` (optional): Location filter (e.g., "New York", "Remote")
- `max_results` (optional): Maximum number of results (1-100, default: 25)
- `experience_level` (optional): Experience level filter
  - Options: `internship`, `entry`, `associate`, `mid`, `senior`, `director`, `executive`
- `job_type` (optional): Job type filter
  - Options: `full-time`, `part-time`, `contract`, `temporary`, `internship`

**Response:**
```json
{
  "total_results": 15,
  "search_parameters": {
    "keywords": "python developer",
    "location": "New York",
    "max_results": 25,
    "experience_level": "mid",
    "job_type": "full-time"
  },
  "jobs": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "New York, NY",
      "posted_date": "2024-01-15",
      "job_url": "https://www.linkedin.com/jobs/view/1234567890",
      "description_preview": "We are looking for a skilled Python developer..."
    }
  ],
  "success": true,
  "message": "Successfully found 15 jobs matching your criteria"
}
```

### 2. Get LinkedIn Job Details

**Endpoint:** `POST /api/v1/jobs/linkedin/details`

**Description:** Get detailed information for a specific LinkedIn job posting.

**Request Body:**
```json
{
  "job_url": "https://www.linkedin.com/jobs/view/1234567890"
}
```

**Parameters:**
- `job_url` (required): LinkedIn job posting URL

**Response:**
```json
{
  "job_details": {
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "New York, NY",
    "description": "Full job description with all details...",
    "job_url": "https://www.linkedin.com/jobs/view/1234567890"
  },
  "success": true,
  "message": "Successfully retrieved job details"
}
```

## Usage Examples

### Using cURL

**Search for Python jobs:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/linkedin/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "python developer",
    "location": "San Francisco",
    "max_results": 10,
    "experience_level": "mid"
  }'
```

**Get job details:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/linkedin/details" \
  -H "Content-Type: application/json" \
  -d '{
    "job_url": "https://www.linkedin.com/jobs/view/1234567890"
  }'
```

### Using Python

```python
import requests

# Search for jobs
response = requests.post("http://localhost:8000/api/v1/jobs/linkedin/search", json={
    "keywords": "data scientist",
    "location": "Remote",
    "max_results": 20,
    "experience_level": "senior"
})

jobs_data = response.json()
print(f"Found {jobs_data['total_results']} jobs")

# Get details for first job
if jobs_data['jobs']:
    first_job_url = jobs_data['jobs'][0]['job_url']
    
    details_response = requests.post("http://localhost:8000/api/v1/jobs/linkedin/details", json={
        "job_url": first_job_url
    })
    
    job_details = details_response.json()
    print(f"Job Title: {job_details['job_details']['title']}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

async function searchLinkedInJobs() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/jobs/linkedin/search', {
      keywords: 'software engineer',
      location: 'Seattle',
      max_results: 15,
      job_type: 'full-time'
    });
    
    console.log(`Found ${response.data.total_results} jobs`);
    return response.data.jobs;
  } catch (error) {
    console.error('Error searching jobs:', error.message);
  }
}

searchLinkedInJobs();
```

## Testing

Run the test script to verify the API is working:

```bash
cd backend
python test_linkedin_api.py
```

This will test both endpoints and provide detailed output.

## Rate Limiting & Best Practices

1. **Respect LinkedIn's robots.txt** - The scraper includes delays to avoid overwhelming LinkedIn's servers
2. **Use reasonable limits** - Don't request more than 100 jobs at once
3. **Cache results** - Consider caching job search results to reduce API calls
4. **Handle errors gracefully** - The API returns error messages in the response
5. **Monitor usage** - Be mindful of your scraping frequency

## Error Handling

The API handles errors gracefully and returns structured error responses:

```json
{
  "total_results": 0,
  "search_parameters": {"keywords": "python developer"},
  "jobs": [],
  "success": false,
  "message": "Error searching LinkedIn jobs: Network timeout"
}
```

Common error scenarios:
- Network timeouts
- LinkedIn page structure changes
- Invalid search parameters
- Chrome/WebDriver issues

## Troubleshooting

### Chrome/WebDriver Issues

If you encounter WebDriver errors:

```bash
# Update Chrome
sudo apt update && sudo apt upgrade google-chrome-stable

# Or reinstall webdriver-manager
pip uninstall webdriver-manager
pip install webdriver-manager
```

### Memory Issues

For high-volume scraping, consider:
- Reducing `max_results`
- Running in headless mode (already enabled)
- Implementing request queuing

## Integration with Existing Job Tracker

The LinkedIn API integrates seamlessly with the existing job tracker system. You can:

1. Search for jobs using LinkedIn API
2. Use the existing `/api/v1/jobs/scrape` endpoint to analyze and save interesting jobs
3. Manage applications using existing job tracker endpoints

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation and testing interfaces.