

class PortfolioDB:

    def __init__(self) -> None:

        from pymongo import MongoClient
        
        self.portfolios = []

        client = MongoClient("mongodb://localhost:27017/",
                             username='admin',
                             password='password'
                            )
        
        db = client["portfolio"]

        for portfolio in db.list_collections():
            self.portfolios.append(portfolio['name'])

        return
