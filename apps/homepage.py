import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

def Homepage(pdb):

  body = dbc.Container(
    [
      dbc.Col(
        [
          dcc.Dropdown(
            id='portfolio_select_dropdown',
            options=[
              {'label': i, 'value':i} for i in pdb.portfolios+['Add new portfolio']
            ],
            value='Example',
            placeholder="Select a portfolio",
          ),
          dbc.Button(
            "Select",
            id='portfolio_select_button', #disabled=True, False
          ),
          dbc.Button(
            "Delete",
            id='portfolio_delete_button', #disabled=True, False
          ),
          html.Div(id='selected_portfolio'),
        ], style={'display': 'inline-block', 'width': '100%', 'height': '100%', 'verticalAlign': 'middle', 'textAlign': 'center'},
      ),
    ]
  )

  layout = html.Div([
    body
  ])
  
  return layout
  

 
