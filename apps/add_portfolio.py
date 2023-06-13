import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table


def New_Portfolio(pdb):
  
  body = dbc.Container(
    [
      dbc.Row(
        [
          
          dbc.Col(
            [
                html.P("Add ticker"),
                html.P("Ticker"),
                dbc.Input(id='ticker-name'),
                html.P("Shares"),
                dbc.Input(id='ticker-shares'),
                html.P("Currency"),
                dbc.Input(id='ticker-currency'),
                html.P("Sector"),
                dbc.Input(id='ticker-sector'),
                dbc.Button(
                    "add",
                    id='new_portfolio_add',
                )
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
  

 
