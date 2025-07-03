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

class MoodRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def home(request: Request):
    """Serve the homepage HTML."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", tags=["API"])
def analyze(req: MoodRequest):
    """Analyze the mood of the given text and return the emotion and polarity."""
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
    logging.info(f"Text analyzed. Polarity: {polarity}, Mood: {mood}")
    return {"emotion": mood, "polarity": polarity}
