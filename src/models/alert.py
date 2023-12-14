from typica import BaseModel, MetaUpdate, Optional


class AlertSchemas(BaseModel):
    link: str


class AlertDataModel(BaseModel):
    id: str
    title: str
    link: str
    updatedAt: Optional[int] = 0


class AlertEntryModel(BaseModel):
    id: str
    feedId: str
    title: str
    link: str
    updatedAt: Optional[int] = 0
    publishedAt: Optional[int] = 0
    content: str
    author: Optional[str] = ""


class CategoriesModel(BaseModel):
    id: str
    name: str
