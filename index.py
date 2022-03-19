import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table
import dash_bootstrap_components as dbc

from apps.homepage import Homepage
from apps.allocation import Allocation
from apps.forecast import Forecast, forecast_asset_figure
from navbar import Navbar

#import pandas as pd
import pandas_datareader as pdr
import datetime
import yaml


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.config.suppress_callback_exceptions = True


app.layout = html.Div([
  dcc.Location(id='url',refresh=False),
  Navbar(),
  html.Div(id='page-content')
])


#download and generate the time series csv files
def download_data():
  with open('portfolio.yml','r') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    portfolio_data = yaml.load(file, Loader=yaml.FullLoader)

  stocks = portfolio_data['stocks']
  currency = portfolio_data['currency']
  sectors = portfolio_data['sectors']
  stock_sectors = portfolio_data['stock_sectors']
  
  today = datetime.date.today()
  delta_1y = datetime.timedelta(days=365)
  delta_1d = datetime.timedelta(days=1)
  a_year_ago = today-delta_1y

  symbols = list(set(stocks.keys()))
  print(symbols)
  raw_data_price = pdr.get_data_yahoo(symbols, start=a_year_ago, end=today)
  raw_close_price = raw_data_price.iloc[:, raw_data_price.columns.get_level_values(0) == 'Close']
  raw_close_price.columns = raw_close_price.columns.droplevel()
  
  raw_pct_change = raw_close_price[symbols].pct_change()*100
  
  close_price_df = raw_close_price.copy()
  pct_change_df = raw_pct_change.copy()
  symbols = list(stocks.keys())

  for ticker in close_price_df.columns:
    if stock_sectors[ticker]==5:
      continue
    ticker_curr = currency[ticker]
    if ticker_curr=='USD':
      close_price_df[ticker] = stocks[ticker]*close_price_df[ticker]*close_price_df['EUR=X']
    elif ticker_curr=='EUR':
      close_price_df[ticker] = stocks[ticker]*close_price_df[ticker]

  for ticker in close_price_df.columns:
    if stock_sectors[ticker]==5:
      close_price_df.drop(ticker, axis=1, inplace=True)
      pct_change_df.drop(ticker, axis=1, inplace=True)
      symbols.remove(ticker)
        
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
  
  asset_values.to_csv('asset_values.csv')
  pct_values.to_csv('pct_values.csv')
  

#download data
download_data()

#create app pages
home_page = Homepage()
forecast_page = Forecast()
allocation_page = Allocation()

@app.callback( Output('page-content','children'), [Input('url','pathname')] )
def display_page(pathname):
  print(pathname)
  if pathname=='/forecast':
    return forecast_page
  elif pathname=='/allocation':
    return allocation_page
  elif pathname=='/home':
    return home_page
  else:
    return home_page
    
@app.callback( [Output('asset_forecast', 'figure'), Output('table_asset_perfomance', 'children')], Input('asset_dropdown', 'value') )
def update_asset_forecast(value):
  figure, perfomance_df = forecast_asset_figure(value)
  return figure, dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False)

    
if __name__=='__main__':
  app.run_server(debug=True)
  
  
