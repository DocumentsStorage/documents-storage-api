import uuid
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


class PydanticUUIDString(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            uuid.UUID(v)
        except Exception as e:
            raise TypeError('Invalid UUID')
        return v
