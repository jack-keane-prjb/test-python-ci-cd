import json
from typing import List

from fastapi import FastAPI, HTTPException, Request

from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates

from sqlalchemy import asc, desc
from sqlalchemy.future import select

import models as models
import schemas as schemas
from database import engine, session

import isodate

app = FastAPI()


def format_duration(iso_duration):
    try:
        duration = isodate.parse_duration(iso_duration)

        if duration.total_seconds() < 3600:
            return f"{int(duration.total_seconds() / 60)} minutes"
        else:
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
    except:
        return iso_duration


templates = Jinja2Templates(directory="templates")
templates.env.filters["format_duration"] = format_duration


@app.on_event("startup")
async def shutdown():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.get("/recipes/", response_model=List[schemas.RecipeOut])
async def all_recipes(request: Request) -> List[models.Recipe]:

    res = await session.execute(
        select(models.Recipe)
        .order_by(desc(models.Recipe.views))
        .order_by(asc(models.Recipe.cooking_time))
    )
    recipes = res.scalars().all()

    return templates.TemplateResponse(
        "index.html", {"request": request, "recipes": recipes}
    )


@app.get("/recipes/{id}", response_model=schemas.RecipeOut)
async def get_recipe(request: Request, id: int) -> models.Recipe:
    result = await session.execute(select(models.Recipe).where(models.Recipe.id == id))

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


@app.post("/recipes/", response_model=schemas.RecipeOut)
async def add_recipe(recipe: schemas.RecipeIn) -> models.Recipe:
    new_recipe = models.Recipe(**recipe.dict())
    async with session.begin():
        session.add(new_recipe)

    return new_recipe


# # For testing:

# curl -X POST http://127.0.0.1:8000/recipes/ \
#   -H "Content-Type: application/json" \
#   -d '{
#     "name": "Summer Salad",
#     "views": 265,
#     "cooking_time": "PT15M",
#     "ingredients": "{\"Pear\": 3, \"Banana\": 2, \"Mango\": 2, \"Spinach\": 1, \"Walnuts\": 0.5}",
#     "description": "A refreshing fruit salad with seasonal produce, tossed with baby spinach and toasted walnuts. Light honey-lime dressing enhances the natural sweetness."
#   }'
