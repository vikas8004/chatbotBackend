from bson import ObjectId


def convert_objectid_to_str(document,*fields):
    for field in fields:
        if field in document and isinstance(document[field], ObjectId):
            document[field] = str(document[field])  # Convert ObjectId to string
    return document