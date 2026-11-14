from uuid import uuid4
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"],)

#TASKS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Task(BaseModel):
    id: str
    title: str
    completed: bool

class CreateTaskSchema(BaseModel):
    title: str

class PatchTaskSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None

tasks: list[Task] = []

@app.get("/tasks")
def get_tasks():
    return tasks


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskSchema) -> Task:
    res = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(res)
    return res


@app.patch("/tasks/{id}")
def patch_task(id: str, payload: PatchTaskSchema):
    for tas in tasks:
        if tas.id == id:
            if payload.title is not None:
                tas.title = payload.title
            if payload.completed is not None:
                tas.completed = payload.completed

            return tas


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: str):
    for task in tasks:
        if id == task.id:
            tasks.remove(task)
            return
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<TASKS



#CATEGORY>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class Category(BaseModel):
    id: str
    name: str

class PPCategorySchema(BaseModel):
    name: str

categories: list[Category] = []

@app.get("/categories")
def get_categories() -> list[Category]:
    return categories

@app.post("/categories", status_code=status.HTTP_201_CREATED)
def post_categories(payload: PPCategorySchema) -> Category:
    res = Category(id=str(uuid4()), name=payload.name)
    categories.append(res)
    return res

@app.patch("/categories/{id}")
def patch_categories(id: str, payload: PPCategorySchema) -> Category:
    for category in categories:
        if category.id == id:
            category.name = payload.name
            return category
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

@app.delete("/categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str):
    for category in categories:
        if category.id == id:
            categories.remove(category)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

