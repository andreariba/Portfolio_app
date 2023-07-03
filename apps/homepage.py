import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


DROPDOWN_ADD_NEW_PORTFOLIO_LABEL = 'Add new portfolio'

def get_dropdown_select_portfolio_options(pdb):
  return [{'label': i, 'value':i} for i in pdb.portfolios+[DROPDOWN_ADD_NEW_PORTFOLIO_LABEL]]

def Homepage(pdb, sb, imageurl):

  figure_news_sentiment = sb.fig

  body = dbc.Container(
    [html.Center(dbc.Row(
        [
          dbc.Col([dcc.Graph( id='graph-news_sentiment',figure=figure_news_sentiment )]),
          dbc.Col([html.Img(src=imageurl)]),
          dbc.Col(
            [
              dcc.Dropdown(
                id='dropdown-select_portfolio',
                options=get_dropdown_select_portfolio_options(pdb),
                value=pdb.current_portfolio.name,
                placeholder="Select a portfolio",
                style={'margin-top':'80px'},
              ),
              dbc.Button(
                "Select",
                id='button-select_portfolio',
              ),
              dbc.Button(
                "Edit",
                id='button-edit_portfolio',
              ),
              dbc.Button(
                "Delete",
                id='button-delete_portfolio',
              ),
              html.Div(id='div-select_portfolio'),
              html.Div(id='div-edit_portfolio'),
              html.Div(id='div-delete_portfolio'),
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
  

 
