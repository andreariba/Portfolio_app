import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from utils.DBmanager import PortfolioDB

pdb = PortfolioDB()

body = dbc.Container(
  [
    html.Div(
      [      
        dcc.Dropdown(
          id='portfolio_select',
          options=[
            {'label': i, 'value':i} for i in pdb.portfolios+['Add new portfolio']
          ],
          value='',
          placeholder="Select a portfolio"
        ),
      ], style={'display': 'inline-block', 'width': '100%', 'height': '100%', 'verticalAlign': 'middle'}
    ),
  ]
)


def Homepage():
  layout = html.Div([
    body
  ])
  
  return layout
  

 
