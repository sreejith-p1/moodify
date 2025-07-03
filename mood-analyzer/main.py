from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from textblob import TextBlob

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class MoodRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
def analyze(req: MoodRequest):
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
    return {"emotion": mood, "polarity": polarity}
