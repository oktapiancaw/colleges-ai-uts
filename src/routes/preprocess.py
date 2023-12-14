import re

# import requests
from typing import cast

from fastapi import APIRouter, Request
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from typica import MetadataResponse, BaseResponse

from src.common import envs
from src.core.db import MainSQL
from src.models.alert import AlertEntryModel
from src.models.preprocess import PreprocessDataModel, PreprocessSchemas
from src.helpers.static import STOPWORD


# * / - Routes --
app = APIRouter()


@app.post("/process")
def prepocess(request: Request, payload: PreprocessSchemas):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    query = f"""
    SELECT nonStandard, CONCAT(standard, " ") FROM slangword
    """
    slangs = {}
    cast(MainSQL, request.app.state.baseDb).cursor.execute(query)
    for raw in cast(MainSQL, request.app.state.baseDb).cursor.fetchall():
        slangs[raw[0]] = raw[1]

    query = f"""
    SELECT * FROM {envs.SQL_TABLE_ENTRY} WHERE feedId='{payload.link}'
    """

    cast(MainSQL, request.app.state.baseDb).cursor.execute(query)
    for raw in cast(MainSQL, request.app.state.baseDb).cursor.fetchall():
        data = AlertEntryModel(
            id=raw[0],
            title=raw[1],
            link=raw[2],
            publishedAt=raw[3],
            updatedAt=raw[4],
            content=raw[5],
            author=raw[6],
            feedId=raw[7],
        )

        symbol = re.sub(r"[^a-zA-Z\s]", "", data.content.lower())
        sword = ""
        for text in symbol.split(" "):
            if text in slangs.keys():
                sword = sword + slangs[text]
            else:
                sword = sword + " " + text
        sword = sword.replace("  ", " ").strip()

        stopword = ""
        for text in sword.split(" "):
            if text in STOPWORD:
                continue
            else:
                stopword = stopword + " " + text
        stopword = stopword.replace("  ", " ").strip()

        steming = stemmer.stem(stopword)

        tokenize = ", ".join(re.split(r"[\s.,:]+", steming))

        query_check = f"""
        SELECT id FROM preprocess WHERE id='{data.id}'
        """
        cast(MainSQL, request.app.state.baseDb).cursor.execute(query_check)
        if cast(MainSQL, request.app.state.baseDb).cursor.fetchone():
            query = f"""
            UPDATE preprocess SET cf='{data.content.lower()}', symbol='{symbol}', sword='{sword}', stopword='{stopword}', stemming='{steming}', tokenize='{tokenize}', cleanData='{steming}', feedId='{data.feedId}' WHERE id='{data.id}'
            """
        else:
            query = f"""
            INSERT INTO preprocess(id, cf, symbol, sword, stopword, stemming, tokenize, cleanData, feedId) VALUES ('{data.id}', '{data.content.lower()}', '{symbol}', '{sword}', '{stopword}', '{steming}', '{tokenize}', '{steming}', '{data.feedId}')
            """
        cast(MainSQL, request.app.state.baseDb).cursor.execute(query)
        cast(MainSQL, request.app.state.baseDb).client.commit()

    return MetadataResponse(status=True, code=200, message="OK")


@app.get("/get-feed")
def get_preprocess(request: Request, id: str):
    query = f"""
    SELECT * FROM preprocess WHERE feedId='{id}'
    """

    cast(MainSQL, request.app.state.baseDb).cursor.execute(query)
    list_data = cast(MainSQL, request.app.state.baseDb).cursor.fetchall()
    if not list_data:
        return MetadataResponse(status=False, code=404, message="Data not found")
    result = []
    for raw in list_data:
        data = PreprocessDataModel(
            id=raw[0],
            cf=raw[1],
            symbol=raw[2],
            sword=raw[3],
            stopword=raw[4],
            stemming=raw[5],
            tokenize=raw[6],
            cleanData=raw[7],
        )
        result.append(data.model_dump())

    return BaseResponse(
        metadata=MetadataResponse(status=True, code=200, message="OK"), data=result
    )
