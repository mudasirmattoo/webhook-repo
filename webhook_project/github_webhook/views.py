from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()
username = os.getenv("MONGODB_USERNAME")
password = urllib.parse.quote_plus(os.getenv("MONGODB_PASSWORD"))
cluster = os.getenv("MONGODB_CLUSTER")
db_name = os.getenv("MONGODB_DB_NAME")

# Create your views here.

uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName={db_name}"
client = MongoClient(uri)
db = client[db_name]
collection = db["events"]

@csrf_exempt
def github_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        payload = json.loads(request.body)
        event = request.headers.get("X-GitHub-Event")

        action_type = None
        from_branch = None
        to_branch = None
        author = None

        if event == "push":
            action_type = "PUSH"
            author = payload["pusher"]["name"]
            to_branch = payload["ref"].split("/")[-1]
            timestamp = payload["head_commit"]["timestamp"]

        elif event == "pull_request":
            pr = payload["pull_request"]
            author = pr["user"]["login"]
            from_branch = pr["head"]["ref"]
            to_branch = pr["base"]["ref"]
            timestamp = pr["created_at"]

            if payload["action"] == "opened":
                action_type = "PULL_REQUEST"
            elif payload["action"] == "closed" and pr["merged"]:
                action_type = "MERGE"

        else:
            return JsonResponse({"message": f"Unhandled event type: {event}"}, status=200)

        record = {
            "request_id": str(uuid.uuid4()),
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        collection.insert_one(record)
        return JsonResponse({"message": "Event received and stored"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
