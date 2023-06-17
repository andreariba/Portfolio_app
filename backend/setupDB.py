from pymongo import MongoClient

from configuration import MONGO_DB_USERNAME, MONGO_DB_PWD

def initialize_MongoDB():
    # Connect to MongoDB
    client = MongoClient("mongodb",
                        username=MONGO_DB_USERNAME, #'admin',
                        password=MONGO_DB_PWD, #'password'
                        )
    
    # client = MongoClient("mongodb://localhost:27017/",
    #                      username='admin',
    #                      password='password'
    # 


    # Access a database
    db = client["utils"]
    
    if "sectors" not in db.list_collection_names():
        # access a collection with the sector mappings
        collection = db["sectors"]
        # insert one document into the collection
        sectors = {
            "SECTOR_0": "Stocks",
            "SECTOR_1": "Bonds",
            "SECTOR_2": "Sectors",
            "SECTOR_3": "Commodity",
            "SECTOR_4": "Crypto",
            "SECTOR_5": "Currency",
        }
        collection.insert_one(sectors)
    
    if "currencies" not in db.list_collection_names():
        collection = db["currencies"]
        currencies = {
            'CUR_01': 'EUR',
            'CUR_02': 'USD',
            'CUR_03': 'GBP',
            'CUR_04': 'CNY'
        }
        collection.insert_one(currencies)

    # Access a database
    db = client["portfolio"]

    if "Example" not in db.list_collection_names():
        # Access a collection
        collection = db["Example"]

        # Insert multiple documents
        documents = [
            {"ticker": "CSSPX.MI", "shares": 25, "currency": "EUR", "sector": "SECTOR_0"},
            {"ticker": "ETH-USD", "shares": 5, "currency": "USD", "sector": "SECTOR_4"}
        ]
        collection.insert_many(documents)

    return

if __name__=="__main__":
    initialize_MongoDB()

