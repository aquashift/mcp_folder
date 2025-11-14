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


# Pydantic schema
class NodeCreate(BaseModel):
    name: str
    org: str

class NodeOut(NodeCreate):
    id: int

# Define a Node schema
class Node(BaseModel):
    id: str
    title: str
    body: str

# Temporary in-memory store
nodes = {}
# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the MCP Server. The archive is alive."}

# Example ritual endpoint: retrieve a node by ID
@app.get("/nodes/{node_id}")
def get_node(node_id: str):
    # For now, return a placeholder
    return {"node_id": node_id, "status": "retrieved (placeholder)"}

@app.post("/nodes/")
def create_node(node: Node):
    nodes[node.id] = node
    return {"status": "created", "node": node}

@app.post("/nodes/", response_model=NodeOut)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    db_node = DBNode(name=node.name, org=node.org)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@app.get("/nodes/{node_id}")
def get_node(node_id: str):
    node = nodes.get(node_id)
    if node:
        return {"status": "retrieved", "node": node}
    return {"error": "Node not found"}

@app.get("/nodes/{node_id}", response_model=NodeOut)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(DBNode).filter(DBNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node







