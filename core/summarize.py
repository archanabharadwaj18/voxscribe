import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(transcript_text):
    prompt = f"""You are a meeting assistant. Given the following meeting transcript (which includes [Speaker X] tags), provide:
1. A concise summary (3-5 sentences)
2. Key points discussed (bullet list)
3. Action items if any (bullet list)

Transcript:
{transcript_text}

Respond in this exact format:
SUMMARY:
<summary here>

KEY POINTS:
- point 1
- point 2

ACTION ITEMS:
- item 1
- item 2
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content

    summary = ""
    key_points = []
    action_items = []

    section = None
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("SUMMARY:"):
            section = "summary"
        elif line.startswith("KEY POINTS:"):
            section = "key_points"
        elif line.startswith("ACTION ITEMS:"):
            section = "action_items"
        elif line.startswith("-") and section == "key_points":
            key_points.append(line[1:].strip())
        elif line.startswith("-") and section == "action_items":
            action_items.append(line[1:].strip())
        elif section == "summary" and line:
            summary += line + " "

    return summary.strip(), key_points, action_items