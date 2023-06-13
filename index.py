import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc

from utils.Portfolio import PortfolioDB, PortfolioManager, Ticker
import json

from apps.homepage import Homepage
from apps.overview import Overview
from apps.allocation import Allocation
from apps.forecast import Forecast
from apps.add_portfolio import New_Portfolio
from navbar import Navbar



app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
app.config.suppress_callback_exceptions = True


app.layout = html.Div([
  dcc.Location(id='url',refresh=False),
  Navbar(),
  html.Div(id='page-content')
])
app.title = 'PortfolioApp'

pdb = PortfolioDB()
pdb.get_portfolio('Example')
pm = pdb.current_portfolio
ps = pdb.current_simulation


@app.callback(
    [
      Output(component_id='portfolio-change', component_property='value'),
    ],
  Input(component_id='new-portfolio-button', component_property='n_clicks'),
  State('portfolio-name', 'value'),
  State(component_id='new-portfolio-storage', component_property='data'),
  prevent_initial_call=True
)
def create_new_portfolio(_, value, portfolio_storage):
  portfolio_storage = json.loads(portfolio_storage)
  print(portfolio_storage)
  portfolio = PortfolioManager(value)
  for ticker_dict in portfolio_storage:
    portfolio.add_Ticker(Ticker(ticker_dict))
  pdb.store_new_portfolio(portfolio)
  return html.Div(dcc.Location(pathname="/home", id="0"))


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
  
  ticker = Ticker({'ticker':name,'shares':shares,'currency':currency,'sector':sector})

  if portfolio_storage is None:
    portfolio_storage = [ticker.dict]
  else:
    portfolio_storage = json.loads(portfolio_storage)
    portfolio_storage.append(ticker.dict)
  print(portfolio_storage)

  portfolio = PortfolioManager("new")
  for ticker_dict in portfolio_storage:
    portfolio.add_Ticker(Ticker(ticker_dict))
  portfolio_df = portfolio.dataframe_representation()

  return json.dumps(portfolio_storage), False, False, dash_table.DataTable(data=portfolio_df.to_dict('records'), columns=[{"name": i, "id": i} for i in portfolio_df.columns], fill_width=True)


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


@app.callback(
  Output(component_id='selected_portfolio', component_property='children'),
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

@app.callback(
  Output(component_id='selected_portfolio', component_property='value'),
  Input(component_id='portfolio_delete_button', component_property='n_clicks'),
  State(component_id='portfolio_select_dropdown', component_property='value'),
  prevent_initial_call=True,
)
def deletePortfolio(_, value):
  if value=='Add new portfolio':
    return 'None'
  elif value!='':
    pdb.delete_portfolio(value)
    return html.Div(dcc.Location(pathname="/home", id="0"))
  return 'None'


@app.callback( Output('page-content','children'), [Input('url','pathname')] )
def display_page(pathname):
  print(pathname)
  if pathname=='/overview':
    return Overview(pdb)
  elif pathname=='/forecast':
    return Forecast(pdb)
  elif pathname=='/allocation':
    return Allocation(pdb)
  elif pathname=='/home':
    return Homepage(pdb)
  elif pathname=='/new':
    return New_Portfolio(pdb)
  else:
    return Homepage(pdb)

    
if __name__=='__main__':
  app.run_server(debug=True)
  
