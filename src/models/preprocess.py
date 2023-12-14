from typica import BaseModel


class PreprocessSchemas(BaseModel):
    link: str


class PreprocessDataModel(BaseModel):
    id: str
    cf: str
    symbol: str
    sword: str
    stopword: str
    stemming: str
    tokenize: str
    cleanData: str
