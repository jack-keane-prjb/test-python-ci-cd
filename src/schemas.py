from pydantic import BaseModel


class BaseRecipe(BaseModel):
    name: str
    views: int
    cooking_time: str
    ingredients: str
    description: str


class RecipeIn(BaseRecipe): ...  # noqa: E701


class RecipeOut(BaseRecipe):
    id: int

    class Config:
        orm_mode = True
