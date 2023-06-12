from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/",
                     username='admin',
                     password='password'
                     )

# Access a database
db = client["portfolio"]

# access a collection with the sector mappings
collection = db["sectors"]
# insert one document into the collection
sectors = {
    "SECTOR_0": "Stocks",
    "SECTOR_1": "Bonds",
    "SECTOR_2": "Sectors",
    "SECTOR_3": "Commodity",
    "SECTOR_4": "Crypto",
    "SECTOR_5": "Currency"
}
collection.insert_one(sectors)

# Access a collection
collection = db["main"]

# Insert multiple documents
documents = [
    {"ticker": "CSSPX.MI", "shares": 25, "currency": "EUR", "sector": "SECTOR_0"},
    {"ticker": "ETH-USD", "shares": 29.40497366, "currency": "USD", "sector": "SECTOR_4"}
]
collection.insert_many(documents)

# Find all documents in a collection
result = collection.find()


# Update a single document
#collection.update_one({"name": "John Doe"}, {"$set": {"age": 31}})

# Update multiple documents
#collection.update_many({"age": {"$gt": 30}}, {"$inc": {"age": 1}})

# Delete a single document
#collection.delete_one({"name": "John Doe"})

# Delete multiple documentss
#collection.delete_many({"age": {"$gt": 30}})
