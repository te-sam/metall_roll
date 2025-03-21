from fastapi import FastAPI

from app.rolls.router import router_rolls

app = FastAPI()

app.include_router(router_rolls)
