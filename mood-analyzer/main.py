from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from textblob import TextBlob
import logging
import re
import string
import random
from typing import List, Optional

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

def get_music_suggestion(mood, n=2, randomize=False):
    music_map = {
        "ecstatic": [
            {"title": "Uptown Funk - Mark Ronson ft. Bruno Mars", "youtube": "https://www.youtube.com/watch?v=OPf0YbXqDm0", "spotify": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"},
            {"title": "Firework - Katy Perry", "youtube": "https://www.youtube.com/watch?v=QGJuMBdaqIw", "spotify": "https://open.spotify.com/track/1bDbXMyjaUIooNwFE9wn0N"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"},
            {"title": "Happy - Pharrell Williams", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs", "spotify": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"}
        ],
        "very happy": [
            {"title": "Happy - Pharrell Williams", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs", "spotify": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"},
            {"title": "Best Day of My Life - American Authors", "youtube": "https://www.youtube.com/watch?v=Y66j_BUCBMY", "spotify": "https://open.spotify.com/track/0HEmnAUT8PHznIAAmVXqFJ"},
            {"title": "On Top of the World - Imagine Dragons", "youtube": "https://www.youtube.com/watch?v=w5tWYmIOWGk", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "happy": [
            {"title": "Best Day of My Life - American Authors", "youtube": "https://www.youtube.com/watch?v=Y66j_BUCBMY", "spotify": "https://open.spotify.com/track/0HEmnAUT8PHznIAAmVXqFJ"},
            {"title": "On Top of the World - Imagine Dragons", "youtube": "https://www.youtube.com/watch?v=w5tWYmIOWGk", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Good Vibrations - The Beach Boys", "youtube": "https://www.youtube.com/watch?v=2s4slli8G6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Lovely Day - Bill Withers", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "content": [
            {"title": "Budapest - George Ezra", "youtube": "https://www.youtube.com/watch?v=VHrLPs3_1Fs", "spotify": "https://open.spotify.com/track/3oJ6m2tQyL3B1l2yQn6pYB"},
            {"title": "Banana Pancakes - Jack Johnson", "youtube": "https://www.youtube.com/watch?v=6Graa_Vm5eA", "spotify": "https://open.spotify.com/track/1yR65psqiazQpeM79CkH1A"},
            {"title": "Put It All On Me - Ed Sheeran", "youtube": "https://www.youtube.com/watch?v=2Vv-BfVoq4g", "spotify": "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"},
            {"title": "I'm Yours - Jason Mraz", "youtube": "https://www.youtube.com/watch?v=EkHTsc9PU2A", "spotify": "https://open.spotify.com/track/7o7Q8j6j6j6j6j6j6j6j6"}
        ],
        "neutral": [
            {"title": "Let It Be - The Beatles", "youtube": "https://www.youtube.com/watch?v=QDYfEBY9NM4", "spotify": "https://open.spotify.com/track/7iN1s7xHE4ifF5povM6A48"},
            {"title": "Viva La Vida - Coldplay", "youtube": "https://www.youtube.com/watch?v=dvgZkm1xWPE", "spotify": "https://open.spotify.com/track/1mea3bSkSGXuIRvnydlB5b"},
            {"title": "No Woman, No Cry - Bob Marley", "youtube": "https://www.youtube.com/watch?v=IT8z7X8g8g8", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Waiting on the World to Change - John Mayer", "youtube": "https://www.youtube.com/watch?v=oBIxScQ2z8I", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "anxious": [
            {"title": "Weightless - Marconi Union", "youtube": "https://www.youtube.com/watch?v=UfcAVejslrU", "spotify": "https://open.spotify.com/track/6U6zjSJIWbWq66m0hVGDgR"},
            {"title": "Breathe Me - Sia", "youtube": "https://www.youtube.com/watch?v=wbP0cQkQvvE", "spotify": "https://open.spotify.com/track/2gZUPNdnz5Y45eiGxpHGSc"},
            {"title": "The Sound of Silence - Disturbed", "youtube": "https://www.youtube.com/watch?v=4zLfCnGVeL4", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Fix You - Coldplay", "youtube": "https://www.youtube.com/watch?v=k4V3Mo61fJM", "spotify": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"}
        ],
        "sad": [
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"},
            {"title": "Fix You - Coldplay", "youtube": "https://www.youtube.com/watch?v=k4V3Mo61fJM", "spotify": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"},
            {"title": "Tears Dry on Their Own - Amy Winehouse", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Back to Black - Amy Winehouse", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "very sad": [
            {"title": "Hurt - Johnny Cash", "youtube": "https://www.youtube.com/watch?v=8AHCfZTRGiI", "spotify": "https://open.spotify.com/track/3U4isOIWM3VvDubwSI3y7a"},
            {"title": "Everybody Hurts - R.E.M.", "youtube": "https://www.youtube.com/watch?v=ijZRCIrTgQc", "spotify": "https://open.spotify.com/track/2RlgNHKcydI9sayD2Df2xp"},
            {"title": "The Night We Met - Lord Huron", "youtube": "https://www.youtube.com/watch?v=KtlgYxa6BMU", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Skinny Love - Bon Iver", "youtube": "https://www.youtube.com/watch?v=ssYG8j6j6j6", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "angry": [
            {"title": "Break Stuff - Limp Bizkit", "youtube": "https://www.youtube.com/watch?v=ZpUYjpKg9KY", "spotify": "https://open.spotify.com/track/2yJwXpWAQOOl5XFzbCxLSW"},
            {"title": "Given Up - Linkin Park", "youtube": "https://www.youtube.com/watch?v=0xyxtzD54rM", "spotify": "https://open.spotify.com/track/1VdZ0vKfR5jneCmWIUAMxK"},
            {"title": "Killing in the Name - Rage Against the Machine", "youtube": "https://www.youtube.com/watch?v=kszLwBaC4Sw", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Smells Like Teen Spirit - Nirvana", "youtube": "https://www.youtube.com/watch?v=hTWKbfoikeg", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "excited": [
            {"title": "Don't Stop Me Now - Queen", "youtube": "https://www.youtube.com/watch?v=HgzGwKwLmgM", "spotify": "https://open.spotify.com/track/5b2bA4VvQxQF2r2YkG3U6w"},
            {"title": "Can't Hold Us - Macklemore & Ryan Lewis", "youtube": "https://www.youtube.com/watch?v=2zNSgSzhBfM", "spotify": "https://open.spotify.com/track/3bidbhpOYeV4knp8AIu8Xn"},
            {"title": "Uptown Funk - Mark Ronson ft. Bruno Mars", "youtube": "https://www.youtube.com/watch?v=OPf0YbXqDm0", "spotify": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"},
            {"title": "Party in the USA - Miley Cyrus", "youtube": "https://www.youtube.com/watch?v=M11SvDtPBhA", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "relaxed": [
            {"title": "Better Together - Jack Johnson", "youtube": "https://www.youtube.com/watch?v=u57d4_b_YgI", "spotify": "https://open.spotify.com/track/3ebXMykcMXOcLeJ9xZ17XH"},
            {"title": "Holocene - Bon Iver", "youtube": "https://www.youtube.com/watch?v=TWcyIpul8OE", "spotify": "https://open.spotify.com/track/0rmkC6v0u1bBwZQW8ayvOe"},
            {"title": "Banana Pancakes - Jack Johnson", "youtube": "https://www.youtube.com/watch?v=6Graa_Vm5eA", "spotify": "https://open.spotify.com/track/1yR65psqiazQpeM79CkH1A"},
            {"title": "Come Away With Me - Norah Jones", "youtube": "https://www.youtube.com/watch?v=3B0X8tG8j6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "hopeful": [
            {"title": "Stronger - Kelly Clarkson", "youtube": "https://www.youtube.com/watch?v=Xn676-fLq7I", "spotify": "https://open.spotify.com/track/0wIhWL9p0pT5jH6T6y1nqP"},
            {"title": "Rise Up - Andra Day", "youtube": "https://www.youtube.com/watch?v=lwgr_IMeEgA", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"},
            {"title": "Fight Song - Rachel Platten", "youtube": "https://www.youtube.com/watch?v=xo1VInw-SKc", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "The Climb - Miley Cyrus", "youtube": "https://www.youtube.com/watch?v=NG2zI6j6j6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "grateful": [
            {"title": "Thank You - Dido", "youtube": "https://www.youtube.com/watch?v=1TO48Cnl66w", "spotify": "https://open.spotify.com/track/1kPpge9JDLpcj15qgrPbYX"},
            {"title": "Grateful - Rita Ora", "youtube": "https://www.youtube.com/watch?v=5oO5rFVp31M", "spotify": "https://open.spotify.com/track/2QeI2l3C8h1Hn3pQK1QK1Q"},
            {"title": "One - U2", "youtube": "https://www.youtube.com/watch?v=ftjEcrrf7r0", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Count on Me - Bruno Mars", "youtube": "https://www.youtube.com/watch?v=SMG9-8j6j6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "lonely": [
            {"title": "Dancing On My Own - Robyn", "youtube": "https://www.youtube.com/watch?v=CcNo07Xp8aQ", "spotify": "https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"},
            {"title": "All By Myself - Celine Dion", "youtube": "https://www.youtube.com/watch?v=by8oyJztzwo", "spotify": "https://open.spotify.com/track/0puf9yIluy9W0vpMEUoAnN"},
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"},
            {"title": "The Night We Met - Lord Huron", "youtube": "https://www.youtube.com/watch?v=KtlgYxa6BMU", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "nostalgic": [
            {"title": "Summer of '69 - Bryan Adams", "youtube": "https://www.youtube.com/watch?v=eFjjO_lhf9c", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"},
            {"title": "Yesterday - The Beatles", "youtube": "https://www.youtube.com/watch?v=NrgmdOz227I", "spotify": "https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI"},
            {"title": "Time After Time - Cyndi Lauper", "youtube": "https://www.youtube.com/watch?v=VdQYyMKW1lU", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Billie Jean - Michael Jackson", "youtube": "https://www.youtube.com/watch?v=Zi_XLOBDo_Y", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "motivated": [
            {"title": "Eye of the Tiger - Survivor", "youtube": "https://www.youtube.com/watch?v=btPJPFnesV4", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Lose Yourself - Eminem", "youtube": "https://www.youtube.com/watch?v=_Yhyp-_hX2s", "spotify": "https://open.spotify.com/track/1u8c2t2Cy7UBoG4ArRcF5g"},
            {"title": "Stronger - Kelly Clarkson", "youtube": "https://www.youtube.com/watch?v=Xn676-fLq7I", "spotify": "https://open.spotify.com/track/0wIhWL9p0pT5jH6T6y1nqP"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"}
        ],
        "inspired": [
            {"title": "Hall of Fame - The Script ft. will.i.am", "youtube": "https://www.youtube.com/watch?v=mk48xRzuNvA", "spotify": "https://open.spotify.com/track/2M9ULmQwTaTGmAdXaXpfz5"},
            {"title": "Unstoppable - Sia", "youtube": "https://www.youtube.com/watch?v=cxjvTXo9WWM", "spotify": "https://open.spotify.com/track/2P1q7vW6Gg3bQe3gGk3A9A"},
            {"title": "Fight Song - Rachel Platten", "youtube": "https://www.youtube.com/watch?v=xo1VInw-SKc", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "The Climb - Miley Cyrus", "youtube": "https://www.youtube.com/watch?v=NG2zI6j6j6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "bored": [
            {"title": "Shut Up and Dance - WALK THE MOON", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "Cheap Thrills - Sia", "youtube": "https://www.youtube.com/watch?v=nYh-n7EOtMA", "spotify": "https://open.spotify.com/track/1jYiIOC5d6soxkJP81fxq2"},
            {"title": "Counting Stars - OneRepublic", "youtube": "https://www.youtube.com/watch?v=hX8g2g6j6j6", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Radioactive - Imagine Dragons", "youtube": "https://www.youtube.com/watch?v=ktvTqknDobU", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "confident": [
            {"title": "Confident - Demi Lovato", "youtube": "https://www.youtube.com/watch?v=cwLRQn61oUY", "spotify": "https://open.spotify.com/track/1jYiIOC5d6soxkJP81fxq2"},
            {"title": "Stronger - Britney Spears", "youtube": "https://www.youtube.com/watch?v=AJWtLf4-WWs", "spotify": "https://open.spotify.com/track/6ktkj2qnJQhF7t2bA3QbQ9"},
            {"title": "Survivor - Destiny's Child", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Run the World (Girls) - Beyoncé", "youtube": "https://www.youtube.com/watch?v=VBmMU_iwe6U", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "romantic": [
            {"title": "Perfect - Ed Sheeran", "youtube": "https://www.youtube.com/watch?v=2Vv-BfVoq4g", "spotify": "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"},
            {"title": "All of Me - John Legend", "youtube": "https://www.youtube.com/watch?v=450p7goxZqg", "spotify": "https://open.spotify.com/track/3U4isOIWM3VvDubwSI3y7a"},
            {"title": "Thinking Out Loud - Ed Sheeran", "youtube": "https://www.youtube.com/watch?v=2Vv-BfVoq4g", "spotify": "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"},
            {"title": "A Thousand Years - Christina Perri", "youtube": "https://www.youtube.com/watch?v=rtOvBOTyX00", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "jealous": [
            {"title": "Jealous - Labrinth", "youtube": "https://www.youtube.com/watch?v=50VWOBi0VFs", "spotify": "https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"},
            {"title": "Cry Me a River - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=DksSPZTZES0", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"},
            {"title": "Back to Black - Amy Winehouse", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"}
        ],
        "fearful": [
            {"title": "Creep - Radiohead", "youtube": "https://www.youtube.com/watch?v=XFkzRNyygfk", "spotify": "https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI"},
            {"title": "Everybody's Got to Learn Sometime - Beck", "youtube": "https://www.youtube.com/watch?v=5C8Ck3eIpoE", "spotify": "https://open.spotify.com/track/1u8c2t2Cy7UBoG4ArRcF5g"},
            {"title": "Mad World - Gary Jules", "youtube": "https://www.youtube.com/watch?v=4N3N1MZ2I6A", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "The Sound of Silence - Disturbed", "youtube": "https://www.youtube.com/watch?v=4zLfCnGVeL4", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "surprised": [
            {"title": "Surprise Yourself - Jack Garratt", "youtube": "https://www.youtube.com/watch?v=8j741TUIET0", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Good Life - OneRepublic", "youtube": "https://www.youtube.com/watch?v=jZhQOvvV45w", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Happy - Pharrell Williams", "youtube": "https://www.youtube.com/watch?v=ZbZSe6N_BXs", "spotify": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
            {"title": "Can't Stop the Feeling - Justin Timberlake", "youtube": "https://www.youtube.com/watch?v=ru0K8uYEZWw", "spotify": "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"}
        ],
        "shy": [
            {"title": "Shy That Way - Tristan Prettyman & Jason Mraz", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "The Scientist - Coldplay", "youtube": "https://www.youtube.com/watch?v=RB-RcX5DS5A", "spotify": "https://open.spotify.com/track/75JFxkI2RXiU7L9VXzMkle"},
            {"title": "Skinny Love - Bon Iver", "youtube": "https://www.youtube.com/watch?v=ssYG8j6j6j6", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Wonderwall - Oasis", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ],
        "ashamed": [
            {"title": "Apologize - OneRepublic", "youtube": "https://www.youtube.com/watch?v=ZSM3w1v-A_Y", "spotify": "https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"},
            {"title": "Sorry - Justin Bieber", "youtube": "https://www.youtube.com/watch?v=fRh_vgS2dFE", "spotify": "https://open.spotify.com/track/09CtPGIpYB4BrO8qb1RGsF"},
            {"title": "Back to December - Taylor Swift", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Someone Like You - Adele", "youtube": "https://www.youtube.com/watch?v=hLQl3WQQoQ0", "spotify": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"}
        ],
        "guilty": [
            {"title": "Guilty - Barbra Streisand & Barry Gibb", "youtube": "https://www.youtube.com/watch?v=6JCLY0Rlx6Q", "spotify": "https://open.spotify.com/track/5J1RxkGkVQGk3A9A"},
            {"title": "Sorry Seems to Be the Hardest Word - Elton John", "youtube": "https://www.youtube.com/watch?v=J4cIxHn4Fpg", "spotify": "https://open.spotify.com/track/3DYVWvPh3kGwPasp7yjahc"},
            {"title": "Tears Dry on Their Own - Amy Winehouse", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"},
            {"title": "Back to Black - Amy Winehouse", "youtube": "https://www.youtube.com/watch?v=6JLwD7qwqH2c1UGhKjQp7G", "spotify": "https://open.spotify.com/track/6JLwD7qwqH2c1UGhKjQp7G"}
        ]
    }
    songs = music_map.get(mood, [
        {"title": "Let It Be - The Beatles", "youtube": "https://www.youtube.com/watch?v=QDYfEBY9NM4", "spotify": "https://open.spotify.com/track/7iN1s7xHE4ifF5povM6A48"}
    ])
    if randomize and len(songs) > n:
        return random.sample(songs, n)
    return songs[:n]

class MusicSuggestion(BaseModel):
    title: str
    youtube: Optional[str] = None
    spotify: Optional[str] = None

class MoodRequest(BaseModel):
    text: str

class MoodResponse(BaseModel):
    emotion: str
    polarity: float
    music: List[MusicSuggestion]

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def home(request: Request):
    """Serve the homepage HTML."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_model=MoodResponse, tags=["API"])
def analyze(req: MoodRequest, request: Request):
    """Analyze the mood of the given text and return the emotion, polarity, and music suggestion."""
    randomize = request.query_params.get("randomize", "false").lower() == "true"
    if not req.text or not req.text.strip():
        logging.warning("Empty text received for analysis.")
        return JSONResponse(status_code=400, content={"error": "Text input is required."})
    # Remove punctuation for keyword matching
    text = req.text.strip().lower()
    text_clean = re.sub(rf"[{re.escape(string.punctuation)}]", " ", text)
    blob = TextBlob(req.text)
    polarity = blob.sentiment.polarity
    mood_keywords = [
        "ecstatic", "very happy", "happy", "content", "neutral", "anxious", "sad", "very sad", "angry", "excited", "relaxed", "hopeful", "grateful", "lonely", "nostalgic", "motivated", "inspired", "bored", "confident", "romantic", "jealous", "fearful", "surprised", "ashamed", "guilty", "shy"
    ]
    found_mood = None
    for mood in mood_keywords:
        # Use word boundaries only for multi-word moods, not for single words like 'shy'
        if ' ' in mood:
            pattern = rf'\\b{re.escape(mood)}\\b'
        else:
            pattern = rf'(?<![a-zA-Z]){re.escape(mood)}(?![a-zA-Z])'
        if re.search(pattern, text_clean, re.IGNORECASE):
            found_mood = mood
            break
    if found_mood:
        music = get_music_suggestion(found_mood, n=2, randomize=randomize)
        logging.info(f"Keyword match. Mood: {found_mood}, Music: {music}, Polarity: {polarity}")
        return MoodResponse(emotion=found_mood, polarity=polarity, music=music)
    # Improved polarity mapping
    if polarity > 0.8:
        mood = "ecstatic"
    elif polarity > 0.6:
        mood = "very happy"
    elif polarity > 0.4:
        mood = "happy"
    elif polarity > 0.2:
        mood = "content"
    elif polarity > 0.05:
        mood = "hopeful"
    elif polarity > -0.05:
        mood = "neutral"
    elif polarity > -0.2:
        mood = "unsure"
    elif polarity > -0.4:
        mood = "sad"
    elif polarity > -0.6:
        mood = "very sad"
    elif polarity > -0.8:
        mood = "ashamed"
    elif polarity <= -0.8:
        mood = "guilty"
    else:
        mood = "neutral"
    music = get_music_suggestion(mood, n=2, randomize=randomize)
    logging.info(f"Text analyzed. Polarity: {polarity}, Mood: {mood}, Music: {music}")
    return MoodResponse(emotion=mood, polarity=polarity, music=music)
