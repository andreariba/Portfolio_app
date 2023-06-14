import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

import json


def New_Portfolio(pdb, search=None):

  sectors = pdb.sectors
  currencies = pdb.currencies

  sector_options = []
  for k,v in sectors.items():
    if k!='_id':
      sector_options.append( { 'label':f"{v} ({k})",'value':k }  )

  currency_options = []
  for k,v in currencies.items():
    if k!='_id':
      currency_options.append( { 'label':v,'value':v }  )

  initial_portfolio = None
  initial_name = 'portfolio-01'
  if search is not None:
    initial_name = pdb.current_portfolio.name
    initial_portfolio = []
    for ticker in pdb.current_portfolio.tickers:
      initial_portfolio.append(ticker.dict)

  print(initial_name, initial_portfolio)
  
  body = dbc.Container(
    [
      dbc.Row(
        [
          
          dbc.Col(
            [
                html.P("Add ticker"),
                html.P("Ticker (Yahoo Finance)"),
                dbc.Input(id='ticker-name'),
                html.P("Shares"),
                dbc.Input(id='ticker-shares'),
                html.P("Currency"),
                dcc.Dropdown(
                  id='ticker-currency',
                  options=currency_options,
                  value='',
                  placeholder="Select a currency"
                ),
                html.P("Sector"),
                dcc.Dropdown(
                  id='ticker-sector',
                  options=sector_options,
                  value='',
                  placeholder="Select an asset class"
                ),
                dbc.Button(
                    "add / remove",
                    id='new_portfolio_add',
                ),
            ]),
          dbc.Col(
            [
              html.P("Name"),
              dbc.Input(
                id='portfolio-name',
                value=initial_name,
                disabled=True,
              ),
              dbc.Button(
                "save portfolio",
                id='new-portfolio-button',
                disabled=True,
              ),
              
              html.Center([html.Div(id='table_new_portfolio')]),
              dcc.Store(
                id='new-portfolio-storage',
                data=json.dumps(initial_portfolio),
              ),
              html.Div(id="portfolio-change"),
            ]
          ),
        ]
      ),
    ]
  )

  layout = html.Div([
    body
  ])
  
  return layout
  

 
