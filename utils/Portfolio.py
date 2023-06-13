
import copy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Ticker:
    
    def __init__(self, db_entry_dict) -> None:
        self.ticker = db_entry_dict.get('ticker', 'no_ticker')
        self.shares = db_entry_dict.get('shares', 0)
        self.currency = db_entry_dict.get('currency', 'EUR')
        self.sector = db_entry_dict.get('sector', 'SECTOR_0')
        return
    
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
        
        currencies = []
        for ticker in tickers:
            if ticker.currency!="USD":
                new_currency = ticker.currency+"=X"
                if new_currency not in currencies:
                    currencies.append(ticker.currency+"=X")
        
        raw_data_price = yf.download(symbols+currencies, start=a_year_ago, end=today)

        raw_close_price = raw_data_price.iloc[:, raw_data_price.columns.get_level_values(0) == 'Close']
        raw_close_price.columns = raw_close_price.columns.droplevel()
        raw_pct_change = raw_close_price[symbols].pct_change()*100

        close_price_df = raw_close_price.copy()
        pct_change_df = raw_pct_change.copy()
        
        # convert all the values to euro
        for ticker in tickers:
            if ticker.sector=='SECTOR_5':
                continue
            if ticker.currency=='USD':
                close_price_df[ticker.ticker] = ticker.shares*close_price_df[ticker.ticker]*close_price_df['EUR=X']
            elif ticker.currency=='EUR':
                close_price_df[ticker.ticker] = ticker.shares*close_price_df[ticker.ticker]

        #remove weekend days
        current_date = a_year_ago
        while current_date<=today:
            wd = current_date.weekday()
            if wd>=5:
                close_price_df = close_price_df.drop(current_date)
                pct_change_df = pct_change_df.drop(current_date)
            current_date += delta_1d

        pct_values = pct_change_df[symbols]
        asset_values = round(close_price_df[symbols],2)
        asset_values = asset_values.fillna(method='ffill')

        return asset_values, pct_values


class PortfolioManager(metaclass=Singleton):
    
    def __init__(self) -> None:
        
        from pymongo import MongoClient
        
        self.tickers = []

        client = MongoClient("mongodb://localhost:27017/",
                             username='admin',
                             password='password'
                            )
        
        db = client["utils"]
        
        self.sectors = db["sectors"].find()[0]
        
        db = client["portfolio"]
        
        portfolio_colletion = db["main"]
        
        ticker_list = portfolio_colletion.find()
        
        for t in ticker_list:
            self.tickers.append(Ticker(t))
        
        self._asset_values, self._pct_values = YFBridge.download_data(self.tickers)
        return 
    
    @property
    def asset_values(self):
        return copy.deepcopy(self._asset_values)

    @property
    def pct_values(self):
        return copy.deepcopy(self._pct_values)
    

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

        #least_recent_date = data_price.index.min()
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


class HomepageFigures:
    
    def __init__(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager
        self._fig_capital_growth = None
        self._perfomance_df = None
        self._loser_gainer_df = None
        self._generate()
        return
        
    @property
    def fig_capital_growth(self):
        return self._fig_capital_growth
    
    @property
    def perfomance_df(self):
        return self._perfomance_df
    
    @property
    def loser_gainer_df(self):
        return self._loser_gainer_df
    
    def _generate(self):
        
        import plotly.express as px

        asset_values = self.portfolio_manager.asset_values
        pct_values = self.portfolio_manager.pct_values

        melted_asset_values = asset_values.melt(ignore_index=False).reset_index()
        
        stock_sectors = { ticker.ticker:ticker.sector for ticker in self.portfolio_manager.tickers }
        
        melted_asset_values['sector'] = melted_asset_values['variable'].map(stock_sectors).map(self.portfolio_manager.sectors)
        melted_asset_values = melted_asset_values.sort_values(by='sector')

        fig_capital_growth = px.line(melted_asset_values.groupby('Date').sum(),labels=dict(Date="Last year", _value="Capital (EUR)"))
        fig_capital_growth.update_layout(title="Growth in the last year", title_x=0.5,showlegend=False)
        
        self._fig_capital_growth = fig_capital_growth

        import pandas as pd
        import numpy as np
        
        asset_1y_perfomance = ((asset_values.iloc[-1]/asset_values.iloc[0]-1)*100)
        asset_1y_perfomance = round(asset_1y_perfomance,2)
        loser_gainer_df = pd.concat([asset_1y_perfomance.sort_values()[:5].reset_index(), asset_1y_perfomance.sort_values(ascending=False)[:5].reset_index()], axis=1)
        loser_gainer_df.columns = ['Losers', '% change (losers)','Gainers', '% change (gainers)']
        
        self._loser_gainer_df = loser_gainer_df
        

        portfolio_value = asset_values.sum(axis=1)
        last_year_perfomance = round((portfolio_value.iloc[-1]/portfolio_value.iloc[0]-1)*100,2)
        portfolio_pct_change = portfolio_value.to_numpy()
        portfolio_pct_change = (portfolio_pct_change[1:]/portfolio_pct_change[:-1]-1)*100
        volatility = round(np.std(portfolio_pct_change),2)

        perfomance_df = pd.DataFrame.from_dict( {'Perfomance (%)':[last_year_perfomance], 'Volatility (%)':[volatility]})
        
        self._perfomance_df = perfomance_df

        return


def forecast_asset_figure(portfolio_simulation, ticker):
    
    import datetime
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    
    simulations = portfolio_simulation.simulations
    data_price = portfolio_simulation.data_price

    simulated_medians = np.median(simulations, axis=2)
    simulated_stds = np.std(simulations, axis=2)
    simulated_q95 = np.quantile(simulations, q=0.95, axis=2)
    simulated_q05 = np.quantile(simulations, q=0.05, axis=2)

    historical_prices = data_price.replace(0,np.nan)[ticker]
    business_days_to_add = portfolio_simulation.trading_days
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
    for j in range(portfolio_simulation.n_simulations):
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


def generate_portfolio_figure(portfolio_simulation):
    
    import datetime
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    
    simulations = portfolio_simulation.simulations
    data_price = portfolio_simulation.data_price
  
    portfolio_simulations = simulations.sum(axis=1)
    portfolio_median = np.median(portfolio_simulations, axis=1)
    portfolio_std = portfolio_simulations.std(axis=1)
    portfolio_q95 = np.quantile(portfolio_simulations, q=0.95, axis=1)
    portfolio_q05 = np.quantile(portfolio_simulations, q=0.05, axis=1)

    historical_portfolio = data_price.sum(axis=1)
    business_days_to_add = portfolio_simulation.trading_days
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
    for i in range(portfolio_simulation.n_simulations):
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

    return fig_portfolio_prediction, perfomance_df


def create_allocation_figures(portfolio_manager):

    import plotly.express as px
    import plotly.graph_objects as go
 
    asset_values = portfolio_manager.asset_values
    pct_values = portfolio_manager.pct_values

    melted_asset_values = asset_values.melt(ignore_index=False).reset_index()
    
    stock_sectors = { ticker.ticker:ticker.sector for ticker in portfolio_manager.tickers }
    
    melted_asset_values['sector'] = melted_asset_values['variable'].map(stock_sectors).map(portfolio_manager.sectors)
    melted_asset_values = melted_asset_values.sort_values(by='sector')

    most_recent_date = melted_asset_values['Date'].max()
    most_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==most_recent_date].groupby('sector').sum().reset_index().sort_values(by='sector')
    fig_piesector = go.Figure(data=[go.Pie(values=most_recent_allocation_df.value, labels=most_recent_allocation_df.sector, sort=False) ])
    fig_piesector.update_layout(title="on "+str(most_recent_date),title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))

    fig_sector_growth = px.area(
        melted_asset_values, x="Date", y="value",
        color="sector", line_group="variable" )
    fig_sector_growth.update_layout(title="Capital growth",title_x=0.5)
    fig_sector_growth.update_xaxes(title_text='Last year')
    fig_sector_growth.update_yaxes(title_text='Value (EUR)')

    least_recent_date = melted_asset_values['Date'].min()
    least_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==least_recent_date].groupby('sector').sum().reset_index().sort_values(by='sector')
    fig_piesector_initial = go.Figure(data=[go.Pie(values=least_recent_allocation_df.value, labels=most_recent_allocation_df.sector,sort=False) ])
    fig_piesector_initial.update_layout(title="on "+str(least_recent_date),title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))

    return fig_piesector, fig_sector_growth, fig_piesector_initial