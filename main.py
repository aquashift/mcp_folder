from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Node as DBNode, Base
from database import SessionLocal, engine

# Create tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(title="MCP Server", description="Corpus archive API", version="0.1.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic schemas
class NodeCreate(BaseModel):
    name: str
    org: str

class NodeOut(NodeCreate):
    id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with SQLAlchemy models


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the MCP Server. The archive is alive."}

# Create a node
@app.post("/nodes/", response_model=NodeOut)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    db_node = DBNode(name=node.name, org=node.org)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

# Get a single node by ID
@app.get("/nodes/{node_id}", response_model=NodeOut)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(DBNode).filter(DBNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

# Optional: Get all nodes
@app.get("/nodes/", response_model=list[NodeOut])
def get_all_nodes(db: Session = Depends(get_db)):
    nodes = db.query(DBNode).all()
    return nodes
