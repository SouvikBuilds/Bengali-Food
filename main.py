from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from typing import List
import os

# 🔹 Load .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# 🔹 FastAPI app init
app = FastAPI()

# 🔹 Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # agar sirf specific domain chahiye ho to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# 🔹 Model
class BengaliFood(BaseModel):
    name: str
    category: str
    picture: str
    ingredients: List[str]

# 🔹 Serializer
def bengali_food_serializer(food) -> dict:
    return {
        "id": str(food["_id"]),
        "name": food["name"],
        "category": food["category"],
        "picture": food["picture"],
        "ingredients": food["ingredients"]
    }

@app.get("/")
def hello():
    return {"message": "Welcome In Bengali Food World"}

@app.get("/foods")
def get_all_foods():
    foods = []
    food_collection = collection.find({})
    for food in food_collection:   # normal for loop
        foods.append(bengali_food_serializer(food))
    return foods

@app.post("/foods")
def add_food(food: BengaliFood):
    food_dict = food.dict()
    result = collection.insert_one(food_dict)
    created = collection.find_one({"_id": result.inserted_id})
    return bengali_food_serializer(created)

@app.put("/foods/{id}")
def update_food(id: str, food: BengaliFood):
    update_result = collection.update_one({"_id": ObjectId(id)}, {"$set": food.dict()})
    if update_result.modified_count == 1:
        updated_food = collection.find_one({"_id": ObjectId(id)})
        return bengali_food_serializer(updated_food)
    raise HTTPException(status_code=404, detail="Food not found")

@app.delete("/foods/{id}")
def delete_food(id: str):
    delete_result = collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Food Deleted Successfully"}
    else:
        return {"message": "Food Not Found"}

@app.get("/foods/search")
def search_food(query: str):
    foods = []
    food_collection = collection.find({"name": {"$regex": query, "$options": "i"}})
    for food in food_collection:
        foods.append(bengali_food_serializer(food))
    return foods
