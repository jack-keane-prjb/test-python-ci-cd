import json
from typing import List

import isodate  # type: ignore
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from sqlalchemy import asc, desc
from sqlalchemy.future import select

from database import Base, engine, session
from models import Recipe
from schemas import RecipeIn, RecipeOut

app = FastAPI()


def format_duration(iso_duration):
    duration = isodate.parse_duration(iso_duration)

    if duration.total_seconds() < 3600:
        return f"{int(duration.total_seconds() / 60)} minutes"
    else:
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"


templates = Jinja2Templates(directory="templates")
templates.env.filters["format_duration"] = format_duration


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.get("/recipes/", response_model=List[RecipeOut])
# async def all_recipes(request: Request) -> List[Recipe]:
async def all_recipes(request: Request):

    res = await session.execute(
        select(Recipe)
        .order_by(desc(Recipe.views))
        .order_by(asc(Recipe.cooking_time))
    )
    recipes = res.scalars().all()

    return templates.TemplateResponse(
        "index.html", {"request": request, "recipes": recipes}
    )


@app.get("/recipes/{id}", response_model=RecipeOut)
async def get_recipe(request: Request, id: int):
    result = await session.execute(select(Recipe).where(Recipe.id == id))

    recipe = result.scalars().first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    serialized = jsonable_encoder(recipe)

    if isinstance(serialized["ingredients"], str):
        try:
            serialized["ingredients"] = json.loads(serialized["ingredients"])
        except json.JSONDecodeError:
            serialized["ingredients"] = None

    return templates.TemplateResponse(
        "recipe.html", {"request": request, "recipe": serialized}
    )


@app.post("/recipes/", response_model=RecipeOut)
async def add_recipe(recipe: RecipeIn) -> Recipe:
    new_recipe = Recipe(**recipe.dict())
    async with session.begin():
        session.add(new_recipe)

    return new_recipe
