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
            value=pdb.current_portfolio.name,
            placeholder="Select a portfolio",
          ),
          dbc.Button(
            "Select",
            id='portfolio_select_button',
          ),
          dbc.Button(
            "Modify",
            id='portfolio_modify_button',
          ),
          dbc.Button(
            "Delete",
            id='portfolio_delete_button',
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
  

 
