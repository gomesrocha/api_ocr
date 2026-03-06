from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.get('/')
def read_root():
    return {'message': 'Welcome to the FastAPI app!'}

@app.post('/items/')
def create_item(item: Item):
    return item

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)