import re
import xmltodict

from dateutil import parser
from typing import cast

from requests import request as requrl
from fastapi import APIRouter, Request, Response, Form
from typica import MetadataResponse, BaseResponse

from src.common import envs
from src.core.db import MainSQL
from src.models.alert import AlertSchemas, AlertDataModel, AlertEntryModel


# * / - Routes --
app = APIRouter()


@app.post("/scrap-data")
def scrap_alert_data(request: Request, response: Response, link: str = Form(...)):
    res = requrl("GET", link)
    raw = xmltodict.parse(res.content)["feed"]

    data = AlertDataModel(
        id=raw.get("id"),
        title=raw.get("title"),
        link=raw["link"]["@href"],
        updatedAt=parser.parse(raw.get("updated")).timestamp().__floor__(),
    )

    query_check = f"SELECT id FROM {envs.SQL_TABLE_DATA} WHERE id='{raw.get('id')}'"
    cast(MainSQL, request.app.state.baseDb).cursor.execute(query_check)
    if cast(MainSQL, request.app.state.baseDb).cursor.fetchone():
        response.status_code = 400
        return MetadataResponse(status=False, code=400, message="Data already exists")

    queries = [
        f"INSERT INTO data(id, title, link, updatedAt) VALUES('{data.id}', '{data.title}', '{data.link}', {data.updatedAt})"
    ]
    for entry in raw.get("entry", []):
        CLEANR = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
        payload = AlertEntryModel(
            id=entry.get("id"),
            feedId=raw.get("id"),
            title=entry["title"]["#text"],
            link=entry["link"]["@href"],
            updatedAt=parser.parse(entry.get("updated")).timestamp().__floor__(),
            publishedAt=parser.parse(entry.get("published")).timestamp().__floor__(),
            content=CLEANR.sub("", entry["content"]["#text"]),
            author=entry["author"]["name"],
        )
        queries.append(
            f"INSERT INTO entry(id, title, link, publishedAt, updatedAt, content, author, feedId) VALUES('{payload.id}', '{payload.title}', '{payload.link}', {payload.publishedAt}, {payload.updatedAt}, '{payload.content}', '{payload.author}', '{payload.feedId}')"
        )

    for query in queries:
        cast(MainSQL, request.app.state.baseDb).cursor.execute(query)

    cast(MainSQL, request.app.state.baseDb).client.commit()

    response.status_code = 200
    return BaseResponse(
        data=data,
        metadata=MetadataResponse(status=True, code=200, message="OK"),
    )
