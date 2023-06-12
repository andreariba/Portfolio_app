import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from utils.Portfolio import PortfolioManager, PortfolioSimulation, generate_portfolio_figure

pm = PortfolioManager()
tickers = [ticker.ticker for ticker in pm.tickers]
ps = PortfolioSimulation(pm)


fig_portfolio_prediction, portfolio_perfomance_df = generate_portfolio_figure(ps)


body = dbc.Container(
  [
    dbc.Row(
      [
        dbc.Col(
          [        
            dcc.Graph( id='portfolio_forecast',figure=fig_portfolio_prediction ),
            html.P( "Montecarlo simulations predict the following scenario for the portfolio:"),
            html.Center([dash_table.DataTable(id='table_portfolio_perfomance', data=portfolio_perfomance_df.to_dict('records'),
                                 columns=[{"name": i, "id": i} for i in portfolio_perfomance_df.columns],
                                 fill_width=False
                        )])
          ], width=6, style={'marginLeft': 'auto', 'marginRight': 'auto'},
        ),
        dbc.Col(
          [
            dcc.Dropdown(
              id='asset_dropdown',
              options=[
                {'label':i, 'value':i} for i in tickers
              ],
              value=tickers,
              placeholder="Select an asset"
            ),
            dcc.Graph( id='asset_forecast' ),
            html.Center([html.Div(id='table_asset_perfomance')]),
          ], width=6,
        ),
      ], justify="center", style={'marginLeft': 'auto', 'marginRight': 'auto'}
    )
  ],
className="mt-4",
)

def Forecast():
  layout = html.Div([
    body
  ])
  
  return layout
  

 
