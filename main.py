import os, logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

key = os.getenv("API_KEY")

origins = [
    "https://quiet-taiga-97989.herokuapp.com",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
)

@app.get("/places/{place_id}")
async def places(place_id):
    print('reached root')
    url = f'https://maps.googleapis.com/maps/api/place/details/json?'
    payload = {'fields': 'photos', 'key': key, 'place_id': place_id}
    r = requests.get(url, params=payload)
    print(r.status_code)
    print(r.text)
    print(r.url)
    try:
        r.raise_for_status()
        photos = r.json()['result']['photos']
        return {"photos": photos}
    except KeyError as error:
        #Google returns invalid request as 200 OK... Why, google?
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={'status': e.response.status_code})


@app.get("/photos/{photo_ref}")
async def photos(photo_ref):
    #print('reached root')
    payload = {'photoreference': photo_ref, 'key': key, 'maxwidth': '600'}
    url = f'https://maps.googleapis.com/maps/api/place/photo?'
    r = requests.get(url, params=payload, allow_redirects = False)
    try:
        r.raise_for_status()
        location = r.headers['Location']
        return {"location": location}  
    except requests.exceptions.HTTPError as e:
        #print(e)
        raise HTTPException(status_code=400, detail={'status': e.response.status_code})
    except Exception as e:
        raise HTTPException(status_code=400, detail={'status': 'invalid request'})