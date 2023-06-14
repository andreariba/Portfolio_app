import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

def Homepage(pdb, imageurl):

  body = dbc.Container(
    [html.Center(dbc.Row(
        [
          dbc.Col([html.Img(src=imageurl)]),
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
                "Edit",
                id='portfolio_edit_button',
              ),
              dbc.Button(
                "Delete",
                id='portfolio_delete_button',
              ),
              html.Div(id='select_portfolio'),
              html.Div(id='edit_portfolio'),
              html.Div(id='delete_portfolio'),
            ], style={'display': 'inline-block', 'width': '100%', 'height': '100%', 'verticalAlign': 'middle', 'textAlign': 'center'},
          ),
        ]
      ))
    ]
  )

  layout = html.Div([
    body
  ])
  
  return layout
  

 
