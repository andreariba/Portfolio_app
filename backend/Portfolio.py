
import copy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Ticker:
    
    def __init__(self, db_entry_dict=dict()) -> None:
        self.ticker = db_entry_dict.get('ticker', 'no_ticker')
        self.shares = db_entry_dict.get('shares', 0)
        self.currency = db_entry_dict.get('currency', 'EUR')
        self.sector = db_entry_dict.get('sector', 'SECTOR_0')
        return
    
    @property
    def dict(self):
        return {'ticker':self.ticker,'shares':self.shares,'currency':self.currency,'sector':self.sector}
    
    def __str__(self) -> str:
        return f"{self.ticker} | {self.shares} | {self.currency} | {self.sector}"



class YFBridge:
    @staticmethod
    def download_data(tickers):
        
        import datetime
        import yfinance as yf
        
        today = datetime.date.today()
        delta_1y = datetime.timedelta(days=365)
        delta_1d = datetime.timedelta(days=1)
        a_year_ago = today-delta_1y

        symbols = [ticker.ticker for ticker in tickers]
        
        currencies = ["EUR=X"]
        for ticker in tickers:
            if ticker.currency!="USD":
                new_currency = ticker.currency+"=X"
                if new_currency not in currencies:
                    currencies.append(ticker.currency+"=X")
        
        raw_data_price = yf.download(symbols+currencies, start=a_year_ago, end=today)
        
        if len(symbols+currencies)==1:
            raw_close_price = raw_data_price.iloc[:, raw_data_price.columns == 'Close']
            raw_close_price.columns = [ticker.ticker]
        else:
            raw_close_price = raw_data_price.iloc[:, raw_data_price.columns.get_level_values(0) == 'Close']
            raw_close_price.columns = raw_close_price.columns.droplevel()
        raw_pct_change = raw_close_price[symbols].pct_change()*100

        close_price_df = raw_close_price.copy()
        pct_change_df = raw_pct_change.copy()
        
        # convert all the values to euro
        for ticker in tickers:
            if ticker.sector=='SECTOR_5':
                continue
            if ticker.currency=='EUR':
                close_price_df[ticker.ticker] = ticker.shares*close_price_df[ticker.ticker]
            elif ticker.currency=='USD':
                close_price_df[ticker.ticker] = ticker.shares*close_price_df[ticker.ticker]*close_price_df['EUR=X']
            else:
                close_price_df[ticker.ticker] = ticker.shares*close_price_df[ticker.ticker]*close_price_df['EUR=X']/close_price_df[ticker.currency+'=X']

        #remove weekend days
        current_date = a_year_ago
        while current_date<=today:
            wd = current_date.weekday()
            if wd>=5:
                if current_date in close_price_df.index:
                    close_price_df = close_price_df.drop(current_date)
                if current_date in pct_change_df.index:
                    pct_change_df = pct_change_df.drop(current_date)
            current_date += delta_1d

        pct_values = pct_change_df[symbols]
        asset_values = round(close_price_df[symbols],2)
        asset_values = asset_values.fillna(method='ffill')

        return asset_values, pct_values



class Portfolio:
    
    def __init__(self, name) -> None:
        
        self._name = name
        self.tickers = []
        self._asset_values = None
        self._pct_values = None
        
        return 
    
    @property
    def name(self):
        return self._name
    @property
    def asset_values(self):
        return copy.deepcopy(self._asset_values)

    @property
    def pct_values(self):
        return copy.deepcopy(self._pct_values)
    
    def dataframe_representation(self):
        import pandas as pd
        df = pd.DataFrame(columns=list(Ticker().dict.keys()))
        for ticker in self.tickers:
            df = pd.concat([df, pd.DataFrame([ticker.dict])], ignore_index=True)
        return df
    
    def add_Ticker(self, ticker):
        if isinstance(ticker, Ticker):
            self.tickers.append(ticker)
        else:
            raise TypeError("ticker must be of Type Ticker")
            
    def generate(self):
        if len(self.tickers)>0:
            self._asset_values, self._pct_values = YFBridge.download_data(self.tickers)
    

    
    

class PortfolioSimulation:
    
    def __init__(self, portfolio_manager, n_simulations=200, trading_days=253):
        self.portfolio_manager = portfolio_manager
        self.n_simulations = n_simulations
        self.trading_days = trading_days
        self._data_price = None
        self._data_pct = None
        self._simulations = None
        self._simulate()
        
    @property
    def data_price(self):
        return copy.deepcopy(self._data_price)
    
    @property
    def data_pct(self):
        return copy.deepcopy(self._data_pct)
    
    @property
    def simulations(self):
        return copy.deepcopy(self._simulations)

    def _simulate(self):
        
        import warnings
        warnings.filterwarnings("ignore")
        
        import numpy as np
        from copulas.univariate import ParametricType, Univariate
        from copulas.multivariate import GaussianMultivariate
        
        asset_values = self.portfolio_manager.asset_values
        pct_values = self.portfolio_manager.pct_values
        
        n_simulations = self.n_simulations
        trading_days = self.trading_days

        pct_values = pct_values.dropna(axis=1, how='all')
        pct_values = pct_values.dropna(axis=0, how='any')
        asset_values = asset_values.fillna(0)

        data_pct = round(pct_values,2)
        data_price = round(asset_values,2)

        most_recent_date = data_price.index.max()

        univariate = Univariate(parametric=ParametricType.PARAMETRIC)
        dist = GaussianMultivariate(distribution=univariate)
        dist.fit(data_pct)

        sampled = dist.sample(trading_days*n_simulations)

        x0 = data_price.loc[most_recent_date].loc[sampled.columns].to_numpy()

        simulations = np.array([], dtype=float)

        # run the simulations
        for i in range(n_simulations):

            # x stores the changing values of the variables across the simulation.
            # x starts by copying the initial values stored in x0.
            x = np.copy(x0).astype(float) 

            # function to sample 'size'(=lenght=4) times from  
            # a multivariate normal distribution with specified mean and covariance
            pct_changes = sampled.iloc[i*trading_days:(i+1)*trading_days]

            # array storing a single simulation initialized 
            # with the initial value x that is equal to x0
            simulation = np.array(x)

            # for each of the 4 sampled returns I update iteratively
            # the values in the vector x
            for idx, row in pct_changes.iterrows():

                for a in range(len(row)):
                    x[a] = x[a]*(1+row[a]/100)
                    if x[a]<0:
                        x[a]=0.0

                simulation = np.append(simulation, x)

            #reshape the simulation array
            simulation = simulation.reshape(trading_days+1,-1)

            # appending the single simulation to the simulations array
            if i==0:
                simulations = simulation[...,np.newaxis]
            else:
                simulations = np.append(simulations,simulation[...,np.newaxis], axis=2)
        
        self._data_price = data_price
        self._data_pct = data_pct
        self._simulations = simulations
        return
    



class ContentGenerator:
    
    def __init__(self, portfolio, portfolio_simulation, sectors):
        
        self.portfolio = portfolio
        self.portfolio_simulation = portfolio_simulation
        
        self.sectors = sectors
        self.stock_sectors = { ticker.ticker:ticker.sector for ticker in self.portfolio.tickers }
        
        self._homepage_capital_growth = None
        self._homepage_loser_gainer_df = None
        self._homepage_perfomance_df = None
        
        self._allocation_piesector = None
        self._allocation_sector_growth = None
        self._allocation_piesector_initial = None
        
        self._forecast_portfolio = None
        self._forecast_perfomance_df = None
        
        self._generate()

        return
        
    @property
    def homepage_capital_growth(self):
        return self._homepage_capital_growth
    
    @property
    def homepage_perfomance_df(self):
        return self._homepage_perfomance_df
    
    @property
    def homepage_loser_gainer_df(self):
        return self._homepage_loser_gainer_df
    
    @property
    def allocation_piesector(self):
        return self._allocation_piesector
    
    @property
    def allocation_sector_growth(self):
        return self._allocation_sector_growth
    
    @property
    def allocation_piesector_initial(self):
        return self._allocation_piesector_initial
    
    @property
    def forecast_portfolio(self):
        return self._forecast_portfolio
    
    @property
    def forecast_perfomance_df(self):
        return self._forecast_perfomance_df
    
    
    
    def _generate(self):

        self._melt_asset_values_by_sector()
        
        self._generate_homepage_capital_growth()
        self._generate_homepage_loser_gainer_df()
        self._generate_homepage_perfomance_df()
        
        self._generate_current_allocation_pie()
        self._generate_allocation_change_figures()
        self._generate_past_allocation_pie()
        
        self._generate_forecast_portfolio_figure()
        
        return
    
    
    def _melt_asset_values_by_sector(self):

        asset_values = self.portfolio.asset_values

        melted_asset_values = asset_values.melt(ignore_index=False).reset_index()
        melted_asset_values['sector'] = melted_asset_values['variable'].map(self.stock_sectors).map(self.sectors)
        self._melted_asset_values = melted_asset_values.sort_values(by='sector')

        return


    def _generate_homepage_capital_growth(self):
        
        import plotly.express as px

        melted_asset_values = self._melted_asset_values

        fig_capital_growth = px.line(melted_asset_values.groupby('Date').sum()['value'],labels=dict(Date="Last year", value="Capital (EUR)"))
        fig_capital_growth.update_layout(title="Growth in the last year", title_x=0.5,showlegend=False)
        
        self._homepage_capital_growth = fig_capital_growth
        return


    def _generate_homepage_loser_gainer_df(self):
        
        import pandas as pd
        
        asset_values = self.portfolio.asset_values
        
        asset_1y_perfomance = ((asset_values.iloc[-1]/asset_values.iloc[0]-1)*100)
        asset_1y_perfomance = round(asset_1y_perfomance,2)
        loser_gainer_df = pd.concat([asset_1y_perfomance.sort_values()[:5].reset_index(), asset_1y_perfomance.sort_values(ascending=False)[:5].reset_index()], axis=1)
        loser_gainer_df.columns = ['Losers', '% change (losers)','Gainers', '% change (gainers)']
        
        self._homepage_loser_gainer_df = loser_gainer_df

        return
    
    
    def _generate_homepage_perfomance_df(self):
        
        import pandas as pd
        import numpy as np
        
        asset_values = self.portfolio.asset_values

        portfolio_value = asset_values.sum(axis=1)
        last_year_perfomance = round((portfolio_value.iloc[-1]/portfolio_value.iloc[0]-1)*100,2)
        portfolio_pct_change = portfolio_value.to_numpy()
        portfolio_pct_change = (portfolio_pct_change[1:]/portfolio_pct_change[:-1]-1)*100
        volatility = round(np.std(portfolio_pct_change),2)

        perfomance_df = pd.DataFrame.from_dict( {'Perfomance (%)':[last_year_perfomance], 'Volatility (%)':[volatility]})
        
        self._homepage_perfomance_df = perfomance_df

        return
    

    def _generate_current_allocation_pie(self):

        import plotly.graph_objects as go

        melted_asset_values = self._melted_asset_values

        # most recent pie
        most_recent_date = melted_asset_values['Date'].max()
        
        most_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==most_recent_date].drop('Date', axis=1).groupby('sector').sum().reset_index().sort_values(by='sector')
        
        fig_piesector = go.Figure(data=[go.Pie(values=most_recent_allocation_df.value, labels=most_recent_allocation_df.sector, sort=False) ])
        fig_piesector.update_layout(title="on "+str(most_recent_date),title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))
        
        self._allocation_piesector = fig_piesector

        return
    

    def _generate_allocation_change_figures(self):

        import plotly.express as px

        melted_asset_values = self._melted_asset_values

        # sector growth
        fig_sector_growth = px.area(
            melted_asset_values, x="Date", y="value",
            color="sector", line_group="variable" )
        fig_sector_growth.update_layout(title="Capital growth",title_x=0.5)
        fig_sector_growth.update_xaxes(title_text='Last year')
        fig_sector_growth.update_yaxes(title_text='Value (EUR)')

        self._allocation_sector_growth = fig_sector_growth


    def _generate_past_allocation_pie(self):

        import plotly.graph_objects as go

        melted_asset_values = self._melted_asset_values

        # least recent pie
        least_recent_date = melted_asset_values['Date'].min()
        least_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==least_recent_date].drop('Date', axis=1).groupby('sector').sum().reset_index().sort_values(by='sector')
        
        fig_piesector_initial = go.Figure(data=[go.Pie(values=least_recent_allocation_df.value, labels=least_recent_allocation_df.sector,sort=False) ])
        fig_piesector_initial.update_layout(title="on "+str(least_recent_date),title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))
        
        self._allocation_piesector_initial = fig_piesector_initial

        return

    
    def _generate_forecast_portfolio_figure(self):
    
        import datetime
        import numpy as np
        import pandas as pd
        import plotly.graph_objects as go

        simulations = self.portfolio_simulation.simulations
        data_price = self.portfolio_simulation.data_price

        portfolio_simulations = simulations.sum(axis=1)
        portfolio_median = np.median(portfolio_simulations, axis=1)
        portfolio_q95 = np.quantile(portfolio_simulations, q=0.95, axis=1)
        portfolio_q05 = np.quantile(portfolio_simulations, q=0.05, axis=1)

        historical_portfolio = data_price.sum(axis=1)
        business_days_to_add = self.portfolio_simulation.trading_days
        current_date = historical_portfolio.index.max()#datetime.datetime.strptime(historical_portfolio.index.max(),'%Y-%m-%d')
        forecasted_dates = [current_date]
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5: # sunday = 6
                continue
            business_days_to_add -= 1
            forecasted_dates.append(current_date)

        lines = []
        for i in range(self.portfolio_simulation.n_simulations):
            line = go.Scatter(x=forecasted_dates, y=portfolio_simulations[:,i], mode="lines", opacity=.1, line_color='gray')
            lines.append(line) 

        fig_portfolio_prediction = go.Figure(
            data=lines,
            layout=go.Layout(showlegend=False)
        )

        fig_portfolio_prediction.add_trace(go.Scatter(x=historical_portfolio.index, 
                                           y=historical_portfolio, line_color='blue',
                                           fill=None, showlegend=False))

        fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                                           y=portfolio_q05, line_color='orange',
                                           fill=None, showlegend=False))
        fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                                           y=portfolio_q95, line_color='orange', 
                                           fill='tonexty', showlegend=False))
        fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                                           y=portfolio_median, line_color='red',
                                           showlegend=False))

        fig_portfolio_prediction.update_yaxes(type="log")
        fig_portfolio_prediction.update_layout(title_text="Portfolio Forecast", xaxis_title="Trading days",yaxis_title="Value (€)",title_x=0.5)

        forecast_pct_q95 = (portfolio_q95[-1]/historical_portfolio[-1]-1)*100
        forecast_pct_median = (portfolio_median[-1]/historical_portfolio[-1]-1)*100
        forecast_pct_q05 = (portfolio_q05[-1]/historical_portfolio[-1]-1)*100
        perfomance_array = np.array([[portfolio_median[-1],portfolio_q05[-1],portfolio_q95[-1]],
                                   [forecast_pct_median,forecast_pct_q05,forecast_pct_q95]])

        perfomance_df = pd.DataFrame(perfomance_array.astype(int), 
                                     columns=['Median','Value at Risk 5%', 'q95'],
                                     index=['Value (€)', 'Relative change (%)' ]
                                    ).reset_index()

        perfomance_df.columns.values[0] = ''
        
        self._forecast_portfolio = fig_portfolio_prediction
        self._forecast_perfomance_df = perfomance_df

        return 
    
    
    def forecast_asset_figure(self,ticker):
    
        import datetime
        import numpy as np
        import pandas as pd
        import plotly.graph_objects as go

        simulations = self.portfolio_simulation.simulations
        data_price = self.portfolio_simulation.data_price

        simulated_medians = np.median(simulations, axis=2)
        simulated_q95 = np.quantile(simulations, q=0.95, axis=2)
        simulated_q05 = np.quantile(simulations, q=0.05, axis=2)

        historical_prices = data_price.replace(0,np.nan)[ticker]
        business_days_to_add = self.portfolio_simulation.trading_days
        current_date = historical_prices.index.max()#datetime.datetime.strptime(historical_prices.index.max(),'%Y-%m-%d')
        forecasted_dates = [current_date]
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5: # sunday = 6
                continue
            business_days_to_add -= 1
            forecasted_dates.append(current_date)

        i = data_price.columns.get_loc(ticker)

        lines = []
        for j in range(self.portfolio_simulation.n_simulations):
            line = go.Scatter(x=forecasted_dates, y=simulations[:,i,j], mode="lines", opacity=.1, line_color='gray', showlegend=False)
            lines.append(line)       

        fig = go.Figure(
            data=lines,
            layout=go.Layout(showlegend=False)
        )

        fig.add_trace(go.Scatter(x=data_price.index, 
                                 y=historical_prices, line_color='blue',
                                 fill=None, showlegend=False))    
        fig.add_trace(go.Scatter(x=forecasted_dates, 
                                 y=simulated_q05[:,i], line_color='orange',
                                 fill=None, showlegend=False))
        fig.add_trace(go.Scatter(x=forecasted_dates, 
                                 y=simulated_q95[:,i], line_color='orange', 
                                 fill='tonexty', showlegend=False))
        fig.add_trace(go.Scatter(x=forecasted_dates, 
                                 y=simulated_medians[:,i], line_color='red',
                                 showlegend=False))

        fig.update_layout(title_text=ticker,xaxis_title="Trading days",yaxis_title="Value (€)",title_x=0.5)

        historical_prices = historical_prices.to_numpy()

        forecast_pct_q95 = (simulated_q95[-1,i]/historical_prices[-1]-1)*100
        forecast_pct_median = (simulated_medians[-1,i]/historical_prices[-1]-1)*100
        forecast_pct_q05 = (simulated_q05[-1,i]/historical_prices[-1]-1)*100
        perfomance_array = np.array([[simulated_medians[-1,i],simulated_q05[-1,i],simulated_q95[-1,i]],
                                   [forecast_pct_median,forecast_pct_q05,forecast_pct_q95]])

        perfomance_df = pd.DataFrame(perfomance_array.astype(int), 
                                   columns=['Median','Value at Risk 5%', 'q95'],
                                   index=['Value (€)', 'Relative change (%)' ]
                                  ).reset_index()

        perfomance_df.columns.values[0] = ''

        return fig, perfomance_df
    




class PortfolioDB(metaclass=Singleton):

    def __init__(self, mongo_user='admin', mongo_pass='password') -> None:
        
        self._mongo_user = mongo_user
        self._mongo_pass = mongo_pass

        self.portfolios = []
        self.sectors = self._get_sectors()
        self.currencies = self._get_currencies()
        self.get_current_portfolio_list()

        self._current_Portfolio = None
        self._current_PortfolioSimulation = None
        self._current_ContentGenerator = None

        return
    
    @property
    def current_portfolio(self):
        return self._current_Portfolio
    
    @property
    def current_simulation(self):
        return self._current_PortfolioSimulation
    
    @property
    def current_content(self):
        return self._current_ContentGenerator
    
    def _connect(self):
        from pymongo import MongoClient
        
        client = MongoClient("mongodb",
                             username=self._mongo_user, #'admin',
                             password=self._mongo_pass, #'password'
                            )
        
        # client = MongoClient("mongodb://localhost:27017/",
        #                      username='admin',
        #                      password='password'
        #                     )

        return client
    
    
    def _get_sectors(self):
        
        client = self._connect()
        
        db = client["utils"] 
        
        return db["sectors"].find()[0]

    
    def _get_currencies(self):
        
        client = self._connect()
        
        db = client["utils"] 
        
        return db["currencies"].find()[0]
    
    
    def get_current_portfolio_list(self):
        
        client = self._connect()
        
        db = client["portfolio"]

        self.portfolios = []
        for portfolio in db.list_collections():
            self.portfolios.append(portfolio['name'])
        
        return self.portfolios
    
    
    def set_portfolio(self, portfolio):
        
        portfolio.generate()
        self._current_Portfolio = portfolio
        
        portfolio_simulation = PortfolioSimulation(portfolio)
        self._current_PortfolioSimulation = portfolio_simulation
        
        content_generator = ContentGenerator(portfolio, portfolio_simulation, self.sectors)
        self._current_ContentGenerator = content_generator
        
        return
    
    
    def get_portfolio(self, name):
        
        self.get_current_portfolio_list()
        if name not in self.portfolios:
            raise ValueError(f"'{name}' portfolio not in the db")
                
        portfolio = Portfolio(name)
        
        client = self._connect()
        
        db = client["portfolio"]
        portfolio_colletion = db[portfolio.name]
        
        ticker_list = portfolio_colletion.find()
        for t in ticker_list:
            portfolio.add_Ticker(Ticker(t))
        
        self.set_portfolio(portfolio)
        
        return portfolio
    
    
    def delete_portfolio(self, name):
        
        client = self._connect()
        
        db = client["portfolio"]
        
        db[name].drop()
        
        self.get_current_portfolio_list()
        
        return
    
    
    def store_new_portfolio(self, portfolio):
        
        client = self._connect()
        
        db = client["portfolio"]
        
        if portfolio.name in db.list_collection_names():
            self.delete_portfolio(portfolio.name)

        collection = db[portfolio.name]
        
        for ticker in portfolio.tickers:
            collection.insert_one(ticker.dict)
            
        self.get_current_portfolio_list()
        
        return