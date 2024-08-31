import pymongo

from app.conf import HOST


client: pymongo.MongoClient = pymongo.MongoClient(host=f"mongodb://{HOST}")
mongodb = client.EirbConnect


def create_collections(collection_list):
    """
    Create collections in database if they don't exist
    """
    for collection in collection_list:
        if collection not in mongodb.list_collection_names():
            mongodb.create_collection(collection)
