# import dependencies
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
import json
from starlette.config import Config

# Load environment variables from .env
config = Config(".env")


# https://stackoverflow.com/questions/71031816/how-do-you-properly-reuse-an-httpx-asyncclient-within-a-fastapi-application
# https://medium.com/@benshearlaw/how-to-use-httpx-request-client-with-fastapi-16255a9984a4

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()


# create app instance
app = FastAPI(lifespan=lifespan)

# set location for templates
templates = Jinja2Templates(directory="app/view_templates")

# handle http get requests for the site root /
# return the index.html page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    # get current date and time
    serverTime: datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")

    # note passing of parameters to the page
    return templates.TemplateResponse("index.html", {"request": request, "serverTime": serverTime })

@app.get("/advice", response_class=HTMLResponse)
async def advice(request: Request):
    
    # Define a request_client instance
    requests_client = request.app.requests_client

    # Connect to the API URL and await the response
    response = await requests_client.get(config("ADVICE_URL"))

    # Send the json data from the response in the TemplateResponse data parameter 
    return templates.TemplateResponse("advice.html", {"request": request, "data": response.json() })

@app.get("/apod", response_class=HTMLResponse)
async def apod(request: Request):
    requests_client = request.app.requests_client
    response = await requests_client.get(config("NASA_APOD_URL") + config("NASA_API_KEY"))
    return templates.TemplateResponse("apod.html", {"request": request, "data": response.json() })


# https://www.getorchestra.io/guides/mastering-query-parameters-in-fastapi-a-detailed-tutorial
@app.get("/params", response_class=HTMLResponse)
async def params(request: Request, name : str | None = ""):
    return templates.TemplateResponse("params.html", {"request": request, "name": name })

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)