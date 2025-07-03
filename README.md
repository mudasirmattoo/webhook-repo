# webhook-repo

![Dashboard Screenshot](webhook_project/github_webhook/static/images/dashboard.png)

This is a Django-based web application that receives GitHub webhook events (push, pull request, and merge), stores them in MongoDB Atlas, and displays them on a responsive dashboard with charts and event cards.

## Features

- GitHub webhook integration for:
  - Push events
  - Pull request events
  - Merge events
- Stores event data in MongoDB
- Displays:
  - List of recent events with repository name, branches, author, and timestamp
  - Bar chart of event type counts
  - Line chart of daily activity
- Responsive design with Tailwind CSS
- Auto-refresh dashboard (polling every 5 seconds)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mudasirmattoo/webhook-repo.git
cd webhook-repo
```
### 2. Create and activate a virtual environment
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Setup environment variables
Create a .env file in the project root:
```bash
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_CLUSTER=your_mongodb_cluster_url
MONGODB_DB_NAME=your_db_name
```

### 5. Run database migrations
```
python manage.py migrate
```
### 6. Start the development server
```
python manage.py runserver
```
### 7. Expose your local server to the internet using ngrok
```
ngrok http 8000
```
### GitHub Webhook Setup
Go to your GitHub repository → Settings → Webhooks.

Click Add webhook.

Set the Payload URL as:
```
https://<your-ngrok-url>/webhook/github/
```
Content type: application/json

Events to trigger: Choose “Let me select individual events” and select:

push

pull_request

Click Add webhook.

Access the Dashboard
Open: http://localhost:8000/

### Create a requirements.txt containing:
```
Django==4.2.5
pymongo==4.7.2
dnspython==2.4.2
python-dotenv==1.0.1
```

To regenerate after adding new packages:
```
pip freeze > requirements.txt
```
