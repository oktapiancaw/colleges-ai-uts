import re
import xmltodict

from dateutil import parser
from typing import cast

from requests import request as requrl
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.common import envs
from src.core.db import MainSQL
from src.models.alert import AlertSchemas, AlertDataModel, AlertEntryModel


# * / - Routes --
app = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
def views(request: Request):
    query = f"""
    SELECT * FROM {envs.SQL_TABLE_DATA}
    """
    result = []
    cast(MainSQL, request.app.state.baseDb).cursor.execute(query)
    for raw in cast(MainSQL, request.app.state.baseDb).cursor.fetchall():
        data = AlertDataModel(
            id=raw[0],
            title=raw[1],
            link=raw[2],
            updatedAt=raw[3],
        )
        result.append(data)

    return templates.TemplateResponse(
        "index.html", {"request": request, "data_alerts": result}
    )
