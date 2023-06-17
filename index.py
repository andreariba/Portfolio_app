import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc

from backend.Portfolio import PortfolioDB, Portfolio, Ticker
from backend.setupDB import initialize_MongoDB
from backend.configuration import MONGO_DB_USERNAME, MONGO_DB_PWD
import json

from apps.homepage import Homepage, get_dropdown_select_portfolio_options, DROPDOWN_ADD_NEW_PORTFOLIO_LABEL
from apps.overview import Overview
from apps.allocation import Allocation
from apps.forecast import Forecast
from apps.add_portfolio import New_Portfolio
from navbar import Navbar


initialize_MongoDB(username=MONGO_DB_USERNAME, password=MONGO_DB_PWD)


import pandas as pd
import numpy as np

print("\n**** Portfolio App ****\n")
print("[Dash version]:", dash.__version__)
print("[Pandas version]:", pd.__version__)
print("[Numpy version]:", np.__version__)

##########################
## Create the app
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
  dcc.Location(id='url', refresh=True),
  Navbar(),
  html.Div(id='page-content')
])
app.title = 'PortfolioApp'
homepage_img_url = app.get_asset_url('homepage_image.svg')


##########################
## Create the manager of the db (MongoDB)
pdb = PortfolioDB(mongo_user=MONGO_DB_USERNAME, mongo_pass=MONGO_DB_PWD)
pdb.get_portfolio('Example')
pm = pdb.current_portfolio
ps = pdb.current_simulation

print("Initialization done")


##########################
## Callback /new endpoint: to store a new portfolio inthe DB from the temporary portfolio
@app.callback(
  Output(component_id='portfolio-change', component_property='children'),
  Input(component_id='button-save_portfolio', component_property='n_clicks'),
  State(component_id='input-portfolio_name', component_property='value'),
  State(component_id='storage-temporary-portfolio', component_property='data'),
  prevent_initial_call=True
)
def create_new_portfolio(_, value, portfolio_storage):
  if value=='' or value==DROPDOWN_ADD_NEW_PORTFOLIO_LABEL:
    return html.Div("Invalid name")
  portfolio_storage = json.loads(portfolio_storage)
  print(portfolio_storage)
  portfolio = Portfolio(value)
  for ticker_dict in portfolio_storage:
    portfolio.add_Ticker(Ticker(ticker_dict))
  pdb.store_new_portfolio(portfolio)
  return html.Div(dcc.Location(pathname="/home", id="url"))


##########################
## Callback /new endpoint: to add a new ticker to the temporary new portfolio
@app.callback( 
  [
    Output(component_id='storage-temporary-portfolio', component_property='data'),
    Output(component_id='input-portfolio_name', component_property='disabled'),
    Output(component_id='button-save_portfolio', component_property='disabled'),
    Output(component_id='table-new_portfolio', component_property='children'),
  ],
  Input(component_id='button-add_remove', component_property='n_clicks'),
  State(component_id='input-ticker-name', component_property='value'),
  State(component_id='input-ticker-shares', component_property='value'),
  State(component_id='dropdown-ticker-currency', component_property='value'),
  State(component_id='dropdown-ticker-sector', component_property='value'),
  State(component_id='storage-temporary-portfolio', component_property='data'),
  prevent_initial_call=True
)
def add_ticker_to_new_portfolio(_, name, shares, currency, sector, portfolio_storage):
  
  ticker = Ticker({'ticker':name,'shares':float(shares),'currency':currency,'sector':sector})
  
  # detect if the portfolio_storage is empty or already initialized
  if portfolio_storage=='null':
      portfolio_storage =  [ticker.dict]
  else:
    portfolio_storage = json.loads(portfolio_storage)
    portfolio_storage.append(ticker.dict)
  print("[Temporary Portfolio]:", portfolio_storage)

  # merge if the tickers are already in the portfolio_storage
  to_remove = []
  for i in range(len(portfolio_storage)):
    ticker_1 = portfolio_storage[i]
    for j in range(i+1,len(portfolio_storage)):
      ticker_2 = portfolio_storage[j]
      if ticker_1 is ticker_2:
        continue
      else:
        if ticker_1['ticker'] == ticker_2['ticker']:
          ticker_1['shares'] = ticker_1['shares'] + ticker_2['shares']
          to_remove.append(ticker_2)
    if ticker_1['shares']<=0 and ticker_1 not in to_remove:
      to_remove.append(ticker_1)

  # remove the not needed anymore ticker entries
  print("removing:", to_remove)
  for t in to_remove:
    portfolio_storage.remove(t)

  # generate a Portfolio object to obtain the dataframe representation
  portfolio = Portfolio("tmp")
  for ticker_dict in portfolio_storage:
    portfolio.add_Ticker(Ticker(ticker_dict))
  portfolio_df = portfolio.dataframe_representation()

  return json.dumps(portfolio_storage), False, False, dash_table.DataTable(data=portfolio_df.to_dict('records'), columns=[{"name": i, "id": i} for i in portfolio_df.columns], fill_width=True)


##########################
## Callback /forecast endpoint: to update the ticker simulation plot
@app.callback(
  [
    Output(component_id='graph-asset_forecast', component_property='figure'), 
    Output(component_id='table-asset_perfomance', component_property='children'),
  ],
  Input('dropdown-forecast_asset', 'value') 
)
def update_asset_forecast(value):
  cg = pdb.current_content
  figure, perfomance_df = cg.forecast_asset_figure(value)
  return figure, dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False)


##########################
## Callback /home endpoint: to select a portfolio or go to /new endpoipnt
@app.callback(
  Output(component_id='div-select_portfolio', component_property='children'),
  Input(component_id='button-select_portfolio', component_property='n_clicks'),
  State(component_id='dropdown-select_portfolio', component_property='value'),
  prevent_initial_call=True,
)
def selectPortfolio(_, value):
  if value==DROPDOWN_ADD_NEW_PORTFOLIO_LABEL:
    return html.Div(dcc.Location(pathname="/new", id="0"))
  elif value!='':
    pdb.get_portfolio(value)
    print("Current portfolio:", pdb.current_portfolio.name)
    return html.Div(dcc.Location(pathname="/overview", id="0"))
  return html.Div("Invalid")


##########################
## Callback /home endpoint: to edit a portfolio and go to /new endpoipnt
@app.callback(
  Output(component_id='div-edit_portfolio', component_property='children'),
  Input(component_id='button-edit_portfolio', component_property='n_clicks'),
  State(component_id='dropdown-select_portfolio', component_property='value'),
  prevent_initial_call=True,
)
def editPortfolio(_, value):
  print("edit", value)
  if value=='Add new portfolio':
    return html.Div(dcc.Location(pathname="/new", id="0"))
  elif value!='':
    pdb.get_portfolio(value)
    print("Edit portfolio:", pdb.current_portfolio.name)
    return html.Div(dcc.Location(pathname="/edit", id="0"))
  return html.Div(dcc.Location(pathname="/new", id="0"))


##########################
## Callback /home endpoint: to delete a portfolio from the DB
@app.callback(
  [
    Output(component_id='div-delete_portfolio', component_property='children'),
    Output(component_id='dropdown-select_portfolio', component_property='value'),
    Output(component_id='dropdown-select_portfolio', component_property='options'),
  ],
  Input(component_id='button-delete_portfolio', component_property='n_clicks'),
  State(component_id='dropdown-select_portfolio', component_property='value'),
  prevent_initial_call=True,
)
def deletePortfolio(_, value):
  if value=='Add new portfolio':
    return html.Div(dcc.Location(pathname="/home", id="0"))
  elif value!='':
    pdb.delete_portfolio(value)
    print("Deleted:", value)
    options = get_dropdown_select_portfolio_options(pdb)
  return html.Div(dcc.Location(pathname="/home", id="0")), options[0]['value'], options


##########################
## Callback to redirect path to the correct pages
@app.callback( Output('page-content','children'), [Input('url','pathname')] )
def display_page(pathname):
  if pathname=='/overview':
    return Overview(pdb)
  elif pathname=='/forecast':
    return Forecast(pdb)
  elif pathname=='/allocation':
    return Allocation(pdb)
  elif pathname=='/home':
    return Homepage(pdb, homepage_img_url)
  elif pathname=='/new': 
    return New_Portfolio(pdb,initial=False)
  elif pathname=='/edit':
    return New_Portfolio(pdb,initial=True)
  else:
    return Homepage(pdb, homepage_img_url)

# run the app
if __name__=='__main__':
  print("Starting the server ...")
  app.run_server(host='0.0.0.0', port=8050, debug=False)
  
