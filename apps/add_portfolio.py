import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from backend.Portfolio import Ticker
import json
import pandas as pd


def New_Portfolio(pdb, initial=False):

  sectors = pdb.sectors
  currencies = pdb.currencies

  # options for the sector Dropdown
  sector_options = []
  for k,v in sectors.items():
    if k!='_id':
      sector_options.append( { 'label':f"{v} ({k})",'value':k }  )
  
  # options for the currency Dropdown
  currency_options = []
  for k,v in currencies.items():
    if k!='_id':
      currency_options.append( { 'label':v,'value':v }  )

  # initialize the variable in case of a new portfolio
  initial_portfolio = None
  initial_name = 'portfolio-01'
  initial_df = pd.DataFrame(columns=list(Ticker().dict.keys()))

  # in case of editing an existing portfolio load the current data of the portfolio
  if initial:
    initial_name = pdb.current_portfolio.name
    initial_df = pdb.current_portfolio.dataframe_representation()
    initial_portfolio = []
    for ticker in pdb.current_portfolio.tickers:
      initial_portfolio.append(ticker.dict)
  
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
              
              html.Center(
                [
                  html.Div(id='table_new_portfolio',
                           children=dash_table.DataTable(data=initial_df .to_dict('records'), columns=[{"name": i, "id": i} for i in initial_df .columns], fill_width=True)
                          )
                ]),
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
  

 
