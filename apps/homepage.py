import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from utils.Portfolio import PortfolioManager, HomepageFigures

body = dbc.Container(
  [
    dbc.Row(
      [
        dbc.Col(
          [        
            dcc.Dropdown(
              id='portfolio_select',
              options=[
                {'label': f"my_{i}", 'value':i} for i in range(3)
              ],
              value='',
              placeholder="Select a portfolio"
            ),
          ], width=7,
        ),
        dbc.Col(
          [        
                        html.P('Add new portfolio')
          ], width=5, align='center', style={'marginLeft': 'auto', 'marginRight': 'auto'},
        ),
      ], justify='center',
    )
  ]
)


def Homepage():
  layout = html.Div([
    body
  ])
  
  return layout
  

 
