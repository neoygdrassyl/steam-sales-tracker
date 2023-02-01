from fastapi import Body, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from models.games import Game

from unidecode import unidecode

from main import app, templates

# DETA INIT
import os
from dotenv import load_dotenv
load_dotenv()
# ---------------
from deta import Deta
deta = Deta(os.getenv('DETA_PROJECT_KEY'))
db = deta.Base("tracker") # creates or connects to NoSQL DB
# ---------------

@app.get("/")
async def root():
    return {"message": "APP WORKING OK!"}

@app.get("/tracker/", response_class=HTMLResponse)
async def read_item(request: Request, result: int = 0, search: str = "", limit: int = 10, offset: int = 0):
    
    res = []

    

    res = db.fetch()
    
    all_items = res.items

    def filterFn(array, value):
        _value = unidecode(value.lower())
        final = []
        for item in array:
            con_1 = _value in unidecode(str(item["name"]).lower() )
            con_2 = _value in unidecode(str(item["genres"]).lower() )
            #con_3 = _value in unidecode(str(item["price"]).lower() )
            #con_4 = _value in unidecode(str(item["lowest"]).lower() )
            if con_1 or con_2:
                final.append(item)
        return final
        

    def sortFn(e):
        return e['name']

    count = len(db.fetch().items)
    if search:
        all_items = filterFn(all_items, search)
        count = len(all_items)

    all_items.sort(key=sortFn)


    return templates.TemplateResponse("tracker.html", {"request": request, "items": all_items, "result": result, "search": search, "limit": limit, "offset": offset, "count": count})

#  --- VIEWS ---
@app.get("/new", response_class=HTMLResponse)
async def new(request: Request):
    return templates.TemplateResponse("new.html", {"request": request})

@app.get("/item/{item_id}", response_class=HTMLResponse)
async def load_game(request: Request, item_id: str):
    item  = db.get(item_id)
    return templates.TemplateResponse("update.html", {"request": request, "item": item})


@app.get("/password/{password}")
async def check_pass(request: Request, password: str):
    if(password == os.getenv('API_PASS')):
        return {"message": "New entry created successfuly!", "status": 200 }
    else:
         raise HTTPException(status_code=404, detail="Wrong password")

#  --- METHODS ---
@app.post("/create")
async def create_game(game: Game, request: Request):
    print(request.headers['password'])
    if(request.headers['password'] == os.getenv('API_PASS')):
        json_encoded_data = jsonable_encoder(game)
        db.insert(json_encoded_data)
        return {"message": "New entry created successfuly!", "status": 201 }
    else:
         raise HTTPException(status_code=404, detail="Wrong password")

@app.put("/edit/{item_key}")
async def create_game(game: Game, item_key: str, request: Request):
    if(request.headers['password'] == os.getenv('API_PASS')):
        json_encoded_data = jsonable_encoder(game)
        db.update(json_encoded_data, item_key)
        return {"message": "Entry updated successfuly!", "status": 210 }
    else:
         raise HTTPException(status_code=404, detail="Wrong password")

@app.delete("/delete/{item_id}")
async def delete_game(item_id: str):
    db.delete(item_id)
    return {"message": "entry delete succesfully!", "status": 211 }