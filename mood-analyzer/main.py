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
        "ecstatic": [
            {"title": "Uptown Funk - Mark Ronson ft. Bruno Mars", "youtube": "https://www.youtube.com/watch?v=OPf0YbXqDm0", "spotify": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"},
            {"title": "Firework - Katy Perry", "youtube": "https://www.youtube.com/watch?v=QGJuMBdaqIw", "spotify": "https://open.spotify.com/track/1bDbXMyjaUIooNwFE9wn0N"}
        ],
        "very happy": [
            {"title": "Happy - Pharrell Williams", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs", "spotify": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"}
        ],
        "happy": [
            {"title": "Best Day of My Life - American Authors", "youtube": "https://www.youtube.com/watch?v=Y66j_BUCBMY", "spotify": "https://open.spotify.com/track/0HEmnAUT8PHznIAAmVXqFJ"},
            {"title": "On Top of the World - Imagine Dragons", "youtube": "https://www.youtube.com/watch?v=w5tWYmIOWGk", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "content": [
            {"title": "Budapest - George Ezra", "youtube": "https://www.youtube.com/watch?v=VHrLPs3_1Fs", "spotify": "https://open.spotify.com/track/3oJ6m2tQyL3B1l2yQn6pYB"},
            {"title": "Banana Pancakes - Jack Johnson", "youtube": "https://www.youtube.com/watch?v=6Graa_Vm5eA", "spotify": "https://open.spotify.com/track/1yR65psqiazQpeM79CkH1A"}
        ],
        "neutral": [
            {"title": "Let It Be - The Beatles", "youtube": "https://www.youtube.com/watch?v=QDYfEBY9NM4", "spotify": "https://open.spotify.com/track/7iN1s7xHE4ifF5povM6A48"},
            {"title": "Viva La Vida - Coldplay", "youtube": "https://www.youtube.com/watch?v=dvgZkm1xWPE", "spotify": "https://open.spotify.com/track/1mea3bSkSGXuIRvnydlB5b"}
        ],
        "anxious": [
            {"title": "Weightless - Marconi Union", "youtube": "https://www.youtube.com/watch?v=UfcAVejslrU", "spotify": "https://open.spotify.com/track/6U6zjSJIWbWq66m0hVGDgR"},
            {"title": "Breathe Me - Sia", "youtube": "https://www.youtube.com/watch?v=wbP0cQkQvvE", "spotify": "https://open.spotify.com/track/2gZUPNdnz5Y45eiGxpHGSc"}
        ],
        "sad": [
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"},
            {"title": "Fix You - Coldplay", "youtube": "https://www.youtube.com/watch?v=k4V3Mo61fJM", "spotify": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"}
        ],
        "very sad": [
            {"title": "Hurt - Johnny Cash", "youtube": "https://www.youtube.com/watch?v=8AHCfZTRGiI", "spotify": "https://open.spotify.com/track/3U4isOIWM3VvDubwSI3y7a"},
            {"title": "Everybody Hurts - R.E.M.", "youtube": "https://www.youtube.com/watch?v=ijZRCIrTgQc", "spotify": "https://open.spotify.com/track/2RlgNHKcydI9sayD2Df2xp"}
        ],
        "angry": [
            {"title": "Break Stuff - Limp Bizkit", "youtube": "https://www.youtube.com/watch?v=ZpUYjpKg9KY", "spotify": "https://open.spotify.com/track/2yJwXpWAQOOl5XFzbCxLSW"},
            {"title": "Given Up - Linkin Park", "youtube": "https://www.youtube.com/watch?v=0xyxtzD54rM", "spotify": "https://open.spotify.com/track/1VdZ0vKfR5jneCmWIUAMxK"}
        ],
        "excited": [
            {"title": "Don't Stop Me Now - Queen", "youtube": "https://www.youtube.com/watch?v=HgzGwKwLmgM", "spotify": "https://open.spotify.com/track/5b2bA4VvQxQF2r2YkG3U6w"},
            {"title": "Can't Hold Us - Macklemore & Ryan Lewis", "youtube": "https://www.youtube.com/watch?v=2zNSgSzhBfM", "spotify": "https://open.spotify.com/track/3bidbhpOYeV4knp8AIu8Xn"}
        ],
        "relaxed": [
            {"title": "Better Together - Jack Johnson", "youtube": "https://www.youtube.com/watch?v=u57d4_b_YgI", "spotify": "https://open.spotify.com/track/3ebXMykcMXOcLeJ9xZ17XH"},
            {"title": "Holocene - Bon Iver", "youtube": "https://www.youtube.com/watch?v=TWcyIpul8OE", "spotify": "https://open.spotify.com/track/0rmkC6v0u1bBwZQW8ayvOe"}
        ],
        "hopeful": [
            {"title": "Stronger - Kelly Clarkson", "youtube": "https://www.youtube.com/watch?v=Xn676-fLq7I", "spotify": "https://open.spotify.com/track/0wIhWL9p0pT5jH6T6y1nqP"},
            {"title": "Rise Up - Andra Day", "youtube": "https://www.youtube.com/watch?v=lwgr_IMeEgA", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"}
        ],
        "grateful": [
            {"title": "Thank You - Dido", "youtube": "https://www.youtube.com/watch?v=1TO48Cnl66w", "spotify": "https://open.spotify.com/track/1kPpge9JDLpcj15qgrPbYX"},
            {"title": "Grateful - Rita Ora", "youtube": "https://www.youtube.com/watch?v=5oO5rFVp31M", "spotify": "https://open.spotify.com/track/2QeI2l3C8h1Hn3pQK1QK1Q"}
        ],
        "lonely": [
            {"title": "Dancing On My Own - Robyn", "youtube": "https://www.youtube.com/watch?v=CcNo07Xp8aQ", "spotify": "https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"},
            {"title": "All By Myself - Celine Dion", "youtube": "https://www.youtube.com/watch?v=by8oyJztzwo", "spotify": "https://open.spotify.com/track/0puf9yIluy9W0vpMEUoAnN"}
        ],
        "nostalgic": [
            {"title": "Summer of '69 - Bryan Adams", "youtube": "https://www.youtube.com/watch?v=eFjjO_lhf9c", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"},
            {"title": "Yesterday - The Beatles", "youtube": "https://www.youtube.com/watch?v=NrgmdOz227I", "spotify": "https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI"}
        ],
        "motivated": [
            {"title": "Eye of the Tiger - Survivor", "youtube": "https://www.youtube.com/watch?v=btPJPFnesV4", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Lose Yourself - Eminem", "youtube": "https://www.youtube.com/watch?v=_Yhyp-_hX2s", "spotify": "https://open.spotify.com/track/1u8c2t2Cy7UBoG4ArRcF5g"}
        ],
        "inspired": [
            {"title": "Hall of Fame - The Script ft. will.i.am", "youtube": "https://www.youtube.com/watch?v=mk48xRzuNvA", "spotify": "https://open.spotify.com/track/2M9ULmQwTaTGmAdXaXpfz5"},
            {"title": "Unstoppable - Sia", "youtube": "https://www.youtube.com/watch?v=cxjvTXo9WWM", "spotify": "https://open.spotify.com/track/2P1q7vW6Gg3bQe3gGk3A9A"}
        ],
        "bored": [
            {"title": "Shut Up and Dance - WALK THE MOON", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "Cheap Thrills - Sia", "youtube": "https://www.youtube.com/watch?v=nYh-n7EOtMA", "spotify": "https://open.spotify.com/track/1jYiIOC5d6soxkJP81fxq2"}
        ],
        "confident": [
            {"title": "Confident - Demi Lovato", "youtube": "https://www.youtube.com/watch?v=cwLRQn61oUY", "spotify": "https://open.spotify.com/track/1jYiIOC5d6soxkJP81fxq2"},
            {"title": "Stronger - Britney Spears", "youtube": "https://www.youtube.com/watch?v=AJWtLf4-WWs", "spotify": "https://open.spotify.com/track/6ktkj2qnJQhF7t2bA3QbQ9"}
        ],
        "romantic": [
            {"title": "Perfect - Ed Sheeran", "youtube": "https://www.youtube.com/watch?v=2Vv-BfVoq4g", "spotify": "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"},
            {"title": "All of Me - John Legend", "youtube": "https://www.youtube.com/watch?v=450p7goxZqg", "spotify": "https://open.spotify.com/track/3U4isOIWM3VvDubwSI3y7a"}
        ],
        "jealous": [
            {"title": "Jealous - Labrinth", "youtube": "https://www.youtube.com/watch?v=50VWOBi0VFs", "spotify": "https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"},
            {"title": "Cry Me a River - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=DksSPZTZES0", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"}
        ],
        "fearful": [
            {"title": "Creep - Radiohead", "youtube": "https://www.youtube.com/watch?v=XFkzRNyygfk", "spotify": "https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI"},
            {"title": "Everybody's Got to Learn Sometime - Beck", "youtube": "https://www.youtube.com/watch?v=5C8Ck3eIpoE", "spotify": "https://open.spotify.com/track/1u8c2t2Cy7UBoG4ArRcF5g"}
        ],
        "surprised": [
            {"title": "Surprise Yourself - Jack Garratt", "youtube": "https://www.youtube.com/watch?v=8j741TUIET0", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Good Life - OneRepublic", "youtube": "https://www.youtube.com/watch?v=jZhQOvvV45w", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"}
        ],
        "shy": [
            {"title": "Shy That Way - Tristan Prettyman & Jason Mraz", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "The Scientist - Coldplay", "youtube": "https://www.youtube.com/watch?v=RB-RcX5DS5A", "spotify": "https://open.spotify.com/track/75JFxkI2RXiU7L9VXzMkle"}
        ],
        "ashamed": [
            {"title": "Apologize - OneRepublic", "youtube": "https://www.youtube.com/watch?v=ZSM3w1v-A_Y", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Sorry - Justin Bieber", "youtube": "https://www.youtube.com/watch?v=fRh_vgS2dFE", "spotify": "https://open.spotify.com/track/09CtPGIpYB4BrO8qb1RGsF"}
        ],
        "guilty": [
            {"title": "Guilty - Barbra Streisand & Barry Gibb", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "Sorry Seems to Be the Hardest Word - Elton John", "youtube": "https://www.youtube.com/watch?v=J4cIxHn4Fpg", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"}
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
    if polarity > 0.7:
        mood = "ecstatic"
    elif polarity > 0.5:
        mood = "very happy"
    elif polarity > 0.2:
        mood = "happy"
    elif polarity > 0:
        mood = "content"
    elif polarity == 0:
        mood = "neutral"
    elif polarity > -0.2:
        mood = "anxious"
    elif polarity > -0.5:
        mood = "sad"
    elif polarity > -0.7:
        mood = "very sad"
    elif polarity <= -0.7:
        mood = "angry"
    else:
        mood = "neutral"
    music = get_music_suggestion(mood)
    logging.info(f"Text analyzed. Polarity: {polarity}, Mood: {mood}, Music: {music}")
    return {"emotion": mood, "polarity": polarity, "music": music}
