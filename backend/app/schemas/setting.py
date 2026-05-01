from pydantic import BaseModel


class SettingRead(BaseModel):
    key: str
    value: str | None

    model_config = {"from_attributes": True}


class SettingWrite(BaseModel):
    value: str | None = None