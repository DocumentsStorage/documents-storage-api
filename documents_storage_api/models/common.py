from pydantic import BaseModel
from bson.objectid import ObjectId as BsonObjectId


class PydanticObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            BsonObjectId(v)
        except Exception as e:
            raise TypeError('Invalid ObjectID')
        return BsonObjectId(v)
