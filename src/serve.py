from fastapi import FastAPI
from get_medal_stats import get_spartan_medal_stats

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/spartan/{spartan_id}")
def spartan_stats(spartan_id: str):
    medals_list = get_spartan_medal_stats(spartan_id)
    response = {spartan_id: medals_list}
    return response
