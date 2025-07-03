from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from textblob import TextBlob
import logging

app = FastAPI(
    title="Mood Analyzer API",
    description="Analyze mood from text and suggest music.",
    version="1.0.0"
)
templates = Jinja2Templates(directory="templates")

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

def get_music_suggestion(mood):
    music_map = {
        "very happy": [
            {"title": "Happy - Pharrell Williams", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs", "spotify": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"}
        ],
        "happy": [
            {"title": "Best Day of My Life - American Authors", "youtube": "https://www.youtube.com/watch?v=Y66j_BUCBMY", "spotify": "https://open.spotify.com/track/0HEmnAUT8PHznIAAmVXqFJ"},
            {"title": "On Top of the World - Imagine Dragons", "youtube": "https://www.youtube.com/watch?v=w5tWYmIOWGk", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "neutral": [
            {"title": "Let It Be - The Beatles", "youtube": "https://www.youtube.com/watch?v=QDYfEBY9NM4", "spotify": "https://open.spotify.com/track/7iN1s7xHE4ifF5povM6A48"},
            {"title": "Viva La Vida - Coldplay", "youtube": "https://www.youtube.com/watch?v=dvgZkm1xWPE", "spotify": "https://open.spotify.com/track/1mea3bSkSGXuIRvnydlB5b"}
        ],
        "sad": [
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"},
            {"title": "Fix You - Coldplay", "youtube": "https://www.youtube.com/watch?v=k4V3Mo61fJM", "spotify": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"}
        ],
        "very sad": [
            {"title": "Hurt - Johnny Cash", "youtube": "https://www.youtube.com/watch?v=8AHCfZTRGiI", "spotify": "https://open.spotify.com/track/3U4isOIWM3VvDubwSI3y7a"},
            {"title": "Everybody Hurts - R.E.M.", "youtube": "https://www.youtube.com/watch?v=ijZRCIrTgQc", "spotify": "https://open.spotify.com/track/2RlgNHKcydI9sayD2Df2xp"}
        ]
    }
    return music_map.get(mood, [
        {"title": "Let It Be - The Beatles", "youtube": "https://www.youtube.com/watch?v=QDYfEBY9NM4", "spotify": "https://open.spotify.com/track/7iN1s7xHE4ifF5povM6A48"}
    ])

class MoodRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def home(request: Request):
    """Serve the homepage HTML."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", tags=["API"])
def analyze(req: MoodRequest):
    """Analyze the mood of the given text and return the emotion, polarity, and music suggestion."""
    if not req.text or not req.text.strip():
        logging.warning("Empty text received for analysis.")
        return JSONResponse(status_code=400, content={"error": "Text input is required."})
    blob = TextBlob(req.text)
    polarity = blob.sentiment.polarity
    if polarity > 0.5:
        mood = "very happy"
    elif polarity > 0:
        mood = "happy"
    elif polarity == 0:
        mood = "neutral"
    elif polarity > -0.5:
        mood = "sad"
    else:
        mood = "very sad"
    music = get_music_suggestion(mood)
    logging.info(f"Text analyzed. Polarity: {polarity}, Mood: {mood}, Music: {music}")
    return {"emotion": mood, "polarity": polarity, "music": music}
