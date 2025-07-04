from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient  
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import urllib.parse
import json

load_dotenv()
username = os.getenv("MONGODB_USERNAME")
password = urllib.parse.quote_plus(os.getenv("MONGODB_PASSWORD"))
cluster = os.getenv("MONGODB_CLUSTER")
db_name = os.getenv("MONGODB_DB_NAME")

uri = f"mongodb+srv://{username}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client[db_name]
collection = db["events"]


# Create your views here.
@csrf_exempt
def github_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        payload = json.loads(request.body.decode("utf-8"))
        event = request.headers.get("X-GitHub-Event")


        action_type = None
        from_branch = None
        to_branch = None
        author = None
        timestamp = None

        if event == "push":
            action_type = "PUSH"
            repo_name = payload.get("repository", {}).get("name")
            author = payload.get("pusher", {}).get("name")
            to_branch = payload.get("ref", "").split("/")[-1]
            timestamp = payload.get("head_commit", {}).get("timestamp")

        elif event == "pull_request":
            repo_name = payload.get("repository", {}).get("name")
            pr = payload.get("pull_request", {})
            author = pr.get("user", {}).get("login")
            from_branch = pr.get("head", {}).get("ref")
            to_branch = pr.get("base", {}).get("ref")
            timestamp = pr.get("created_at")

            if payload.get("action") == "opened":
                action_type = "PULL_REQUEST"
            elif payload.get("action") == "closed" and pr.get("merged"):
                action_type = "MERGE"

        else:
            return JsonResponse({"message": f"Unhandled event type: {event}"}, status=200)

        record = {
            "request_id": str(uuid.uuid4()),
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "repo_name": repo_name
        }

        collection.insert_one(record)
        return JsonResponse({"message": "Event received and stored"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_events(request):
    try:
        events = list(collection.find().sort("timestamp", -1).limit(10))
        for event in events:
            event["_id"] = str(event["_id"])
        return JsonResponse(events, safe=False)
    except Exception as e:
        print(f"[ERROR] Failed to fetch events: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def event_dashboard(request):
    return render(request, "github_webhook/index.html")