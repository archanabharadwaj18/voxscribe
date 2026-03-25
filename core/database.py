import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["voxscribe"]
meetings_collection = db["meetings"]

def save_meeting(name, transcript, summary, key_points, action_items):
    meeting = {
        "name": name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "transcript": transcript,
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items
    }
    result = meetings_collection.insert_one(meeting)
    return str(result.inserted_id)

def get_all_meetings():
    meetings = meetings_collection.find({}, {"_id": 1, "name": 1, "date": 1, "summary": 1})
    return list(meetings)

def get_meeting_by_id(meeting_id):
    from bson import ObjectId
    return meetings_collection.find_one({"_id": ObjectId(meeting_id)})