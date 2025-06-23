import pytest
from fastapi import status
from sqlalchemy.future import select

from models import Recipe


@pytest.mark.asyncio
async def test_good_recipe_creation_ok(
    client, async_session_factory, test_recipe
):

    client.post("/recipes/", json=test_recipe)

    async with async_session_factory() as session:

        result = await session.execute(select(Recipe))
        recipes = result.scalars().all()
        assert recipes[0].name == "Test Recipe"


@pytest.mark.asyncio
async def test_bad_recipe_creation_nok(client):

    bad_recipe = {"name": "Bad Recipe"}
    response = client.post("/recipes/", json=bad_recipe)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_recipes_sorted_by_views_asc_and_cooking_time_asc(
    client, test_recipe, async_session_factory
):

    async with async_session_factory() as session:
        recipe = Recipe(**test_recipe)
        session.add(recipe)
        await session.commit()

    response = client.get("/recipes/")

    recipes = response.context["recipes"]

    if len(recipes) > 1:
        assert recipes[0].views >= recipes[1].views
        if recipes[0].views == recipes[1].views:
            assert recipes[0].cooking_time <= recipes[1].cooking_time


@pytest.mark.asyncio
async def test_get_recipe_after_creation(
    client, test_recipe, async_session_factory
):

    recipe = Recipe(**test_recipe)

    async with async_session_factory() as session:
        session.add(recipe)
        await session.commit()
        recipe_id = recipe.id

    response = client.get(f"/recipes/{recipe_id}")

    assert response.context["recipe"]["name"] == "Test Recipe"


@pytest.mark.asyncio
async def test_get_non_existent_recipe(client):
    response = client.get("/recipes/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
