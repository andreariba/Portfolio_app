import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table


def New_Portfolio(pdb):

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
                value='nome-01',
                disabled=True,
              ),
              dbc.Button(
                "create new portfolio",
                id='new-portfolio-button',
                disabled=True,
              ),
              
              html.Center([html.Div(id='table_new_portfolio')]),
              dcc.Store(id='new-portfolio-storage'),
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
  

 
