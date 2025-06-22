from sqlalchemy import Column, String, Integer

from database import Base

class Recipe(Base):
    __tablename__ = 'Recipe'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    views = Column(String, index=True)
    cooking_time = Column(String, index=True)
    ingredients = Column(String, index=True)
    description = Column(String, index=True)
