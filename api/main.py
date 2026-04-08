import torchaudio
if not hasattr(torchaudio, 'list_audio_backends'):
    torchaudio.list_audio_backends = lambda: []

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.transcribe import transcribe_audio
from core.summarize import generate_summary
from core.database import save_meeting, get_all_meetings, get_meeting_by_id, db
from core.jira_sync import create_jira_tasks

from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
def serve_ui():
    return FileResponse("static/index.html")

@app.get("/")
def root():
    return {"message": "VoxScribe API is running"}

@app.post("/upload")
async def upload_meeting(
    meeting_name: str = Form(...),
    file: UploadFile = File(...)
):
    import traceback
    try:
        save_dir = os.path.join("data", "audio")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, file.filename)

        with open(save_path, "wb") as f:
            f.write(await file.read())

        full_text, segments, detected_language, confidence = transcribe_audio(save_path)

        summary, key_points, action_items = generate_summary(full_text)

        try:
            jira_tickets = create_jira_tasks(
                action_items=action_items,
                jira_url="https://archanabharadwajjs.atlassian.net",
                username="archanabharadwajjs@gmail.com",
                api_token=os.getenv("JIRA_API_TOKEN"),
                project_key="VOX"
            )
        except Exception:
            jira_tickets = []

        meeting_id = save_meeting(meeting_name, full_text, summary, key_points, action_items)

        return JSONResponse({
            "meeting_id": meeting_id,
            "summary": summary,
            "key_points": key_points,
            "action_items": action_items,
            "transcript": full_text,
            "segments": segments,
            "language": detected_language,
            "language_confidence": confidence,
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/record")
async def record_meeting(
    meeting_name: str = Form(...),
    file: UploadFile = File(...)
):
    import traceback
    try:
        save_dir = os.path.join("data", "audio")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "recording_" + file.filename)

        with open(save_path, "wb") as f:
            f.write(await file.read())

        full_text, segments, detected_language, confidence = transcribe_audio(save_path)

        summary, key_points, action_items = generate_summary(full_text)

        meeting_id = save_meeting(meeting_name, full_text, summary, key_points, action_items)

        return JSONResponse({
            "meeting_id": meeting_id,
            "summary": summary,
            "key_points": key_points,
            "action_items": action_items,
            "transcript": full_text,
            "segments": segments,
            "language": detected_language,
            "language_confidence": confidence,
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/meetings")
def list_meetings():
    meetings = get_all_meetings()
    for m in meetings:
        m["_id"] = str(m["_id"])
    return meetings

@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        return JSONResponse(status_code=404, content={"error": "Meeting not found"})
    meeting["_id"] = str(meeting["_id"])
    return meeting

@app.put("/meetings/{meeting_id}")
async def update_meeting_name(meeting_id: str, new_name: str):
    try:
        result = db.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": {"name": new_name}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return {"message": "Name updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {e}")

@app.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    try:
        result = db.meetings.delete_one({"_id": ObjectId(meeting_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return {"message": "Meeting deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {e}")