import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc

from backend.Portfolio import PortfolioDB, Portfolio, Ticker
import json

from apps.homepage import Homepage
from apps.overview import Overview
from apps.allocation import Allocation
from apps.forecast import Forecast
from apps.add_portfolio import New_Portfolio
from navbar import Navbar

print(dash.__version__)

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
## Create the manager of MongoDB and an empty portfolio
pdb = PortfolioDB()
pdb.get_portfolio('Example')
pm = pdb.current_portfolio
ps = pdb.current_simulation


##########################
## Callback /new endpoint: to store a new portfolio inthe DB from the temporary portfolio
@app.callback(
  Output(component_id='portfolio-change', component_property='children'),
  Input(component_id='new-portfolio-button', component_property='n_clicks'),
  State('portfolio-name', 'value'),
  State(component_id='new-portfolio-storage', component_property='data'),
  prevent_initial_call=True
)
def create_new_portfolio(_, value, portfolio_storage):
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
    Output(component_id='new-portfolio-storage', component_property='data'),
    Output(component_id='portfolio-name', component_property='disabled'),
    Output(component_id='new-portfolio-button', component_property='disabled'),
    Output(component_id='table_new_portfolio', component_property='children'),
  ],
  Input(component_id='new_portfolio_add', component_property='n_clicks'),
  State(component_id='ticker-name', component_property='value'),
  State(component_id='ticker-shares', component_property='value'),
  State(component_id='ticker-currency', component_property='value'),
  State(component_id='ticker-sector', component_property='value'),
  State(component_id='new-portfolio-storage', component_property='data'),
  prevent_initial_call=True
)
def add_ticker_to_new_portfolio(_, name, shares, currency, sector, portfolio_storage):
  
  ticker = Ticker({'ticker':name,'shares':float(shares),'currency':currency,'sector':sector})
  print("[Temporary Portfolio]:", portfolio_storage)
  if portfolio_storage=='null':
      portfolio_storage =  [ticker.dict]
  else:
    portfolio_storage = json.loads(portfolio_storage)
    portfolio_storage.append(ticker.dict)
  print("[Temporary Portfolio]:", portfolio_storage)

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

  print("removing:", to_remove)
  for t in to_remove:
    portfolio_storage.remove(t)

  portfolio = Portfolio("tmp")
  for ticker_dict in portfolio_storage:
    portfolio.add_Ticker(Ticker(ticker_dict))
  portfolio_df = portfolio.dataframe_representation()

  return json.dumps(portfolio_storage), False, False, dash_table.DataTable(data=portfolio_df.to_dict('records'), columns=[{"name": i, "id": i} for i in portfolio_df.columns], fill_width=True)


##########################
## Callback /forecast endpoint: to update the ticker simulation plot
@app.callback( 
  [
    Output(component_id='asset_forecast', component_property='figure'), 
    Output(component_id='table_asset_perfomance', component_property='children'),
  ],
  Input('asset_dropdown', 'value') 
)
def update_asset_forecast(value):
  cg = pdb.current_content
  figure, perfomance_df = cg.forecast_asset_figure(value)
  return figure, dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False)


##########################
## Callback /home endpoint: to select a portfolio or go to /new endpoipnt
@app.callback(
  Output(component_id='select_portfolio', component_property='children'),
  Input(component_id='portfolio_select_button', component_property='n_clicks'),
  State(component_id='portfolio_select_dropdown', component_property='value'),
  prevent_initial_call=True,
)
def selectPortfolio(_, value):
  if value=='Add new portfolio':
    return html.Div(dcc.Location(pathname="/new", id="0"))
  elif value!='':
    pdb.get_portfolio(value)
    print("Current portfolio:", pdb.current_portfolio.name)
    return html.Div(dcc.Location(pathname="/overview", id="0"))
  return html.Div("Invalid")


##########################
## Callback /home endpoint: to edit a portfolio and go to /new endpoipnt
@app.callback(
  Output(component_id='edit_portfolio', component_property='children'),
  Input(component_id='portfolio_edit_button', component_property='n_clicks'),
  State(component_id='portfolio_select_dropdown', component_property='value'),
  prevent_initial_call=True,
)
def editPortfolio(_, value):
  print("edit", value)
  if value=='Add new portfolio':
    return html.Div(dcc.Location(pathname="/new", id="0"))
  elif value!='':
    print("here")
    return html.Div(dcc.Location(pathname="/edit", id="0", search=value))
  return html.Div(dcc.Location(pathname="/new", id="0"))


##########################
## Callback /home endpoint: to delete a portfolio from the DB
@app.callback(
  Output(component_id='delete_portfolio', component_property='children'),
  Input(component_id='portfolio_delete_button', component_property='n_clicks'),
  State(component_id='portfolio_select_dropdown', component_property='value'),
  prevent_initial_call=True,
)
def deletePortfolio(_, value):
  if value=='Add new portfolio':
    return html.Div(dcc.Location(pathname="/home", id="0"))
  elif value!='':
    pdb.delete_portfolio(value)
  return html.Div(dcc.Location(pathname="/home", id="0"))


##########################
## Callback to redirect path to the correct pages
@app.callback( Output('page-content','children'), [Input('url','pathname'),Input('url','search')] )
def display_page(pathname,search):
  print(pathname,search, search=='')
  if len(search)>0:
    value = search[1:]
  if pathname=='/overview':
    return Overview(pdb)
  elif pathname=='/forecast':
    return Forecast(pdb)
  elif pathname=='/allocation':
    return Allocation(pdb)
  elif pathname=='/home':
    return Homepage(pdb, homepage_img_url)
  elif pathname=='/new': 
    return New_Portfolio(pdb)
  elif pathname=='/edit': 
    return New_Portfolio(pdb,value)
  else:
    return Homepage(pdb, homepage_img_url)

# run the app
if __name__=='__main__':
  app.run_server(debug=True)
  
