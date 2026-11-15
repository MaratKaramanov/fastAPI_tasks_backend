from uuid import uuid4
from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"],)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

def get_db():
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()

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

#tasks: list[Task] = []

def convert_task_orm_to_task(task_orm: TaskORM) -> Task:
    return Task(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [convert_task_orm_to_task(task) for task in tasks_from_db]


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskSchema, db: Session = Depends(get_db)) -> Task:
    res = TaskORM(title=payload.title, completed=False)
    db.add(res)
    db.commit()
    db.refresh(res)
    return convert_task_orm_to_task(res)


@app.patch("/tasks/{id}")
def patch_task(id: str, payload: PatchTaskSchema, db: Session = Depends(get_db)) -> Task:
    task_for_update = db.get(TaskORM, id)
    if task_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
            task_for_update.completed = payload.completed
    db.commit()
    db.refresh(task_for_update)
    return convert_task_orm_to_task(task_for_update)

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: str, db: Session = Depends(get_db)):
    task_for_delete = db.get(TaskORM, id)
    if task_for_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task_for_delete)
    db.commit()
    return
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<TASKS



#CATEGORY>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


class CategoryORM(Base):
    __tablename__ = "categories"
    name: Mapped[str]

class Category(BaseModel):
    id: str
    name: str

class PPCategorySchema(BaseModel):
    name: str

#categories: list[Category] = []

def convert_categoryorm_to_category(category: CategoryORM) -> Category:
    return Category(id=category.id, name=category.name)


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)) -> list[Category]:
    categories_from_db = db.scalars(select(CategoryORM)).all()
    return [convert_categoryorm_to_category(category) for category in categories_from_db]
        

@app.post("/categories", status_code=status.HTTP_201_CREATED)
def post_categories(payload: PPCategorySchema, db: Session = Depends(get_db)) -> Category:
    res = CategoryORM(name=payload.name)
    db.add(res)
    db.commit()
    db.refresh(res)
    return convert_categoryorm_to_category(res)

@app.patch("/categories/{id}")
def patch_category(id: str, payload: PPCategorySchema, db: Session = Depends(get_db)) -> Category:
    category_for_update = db.get(CategoryORM, id)
    if category_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category_for_update.name = payload.name
    db.commit()
    db.refresh(category_for_update)
    return convert_categoryorm_to_category(category_for_update)
 

@app.delete("/categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str, db: Session = Depends(get_db)):
    category_for_delete = db.get(CategoryORM, id)
    if category_for_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category_for_delete)
    db.commit()
    return

