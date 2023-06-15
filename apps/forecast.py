import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table


def Forecast(pdb):
  
  pm = pdb.current_portfolio
  tickers = [ticker.ticker for ticker in pm.tickers]
  cg = pdb.current_content

  fig_portfolio_prediction = cg.forecast_portfolio
  portfolio_perfomance_df = cg.forecast_perfomance_df


  body = dbc.Container(
    [
      dbc.Row(
        [
          dbc.Col(
            [        
              dcc.Graph( id='graph-portfolio_forecast',figure=fig_portfolio_prediction ),
              html.P( "Montecarlo simulations predict the following scenario for the portfolio:"),
              html.Center([dash_table.DataTable(id='table-portfolio_perfomance', data=portfolio_perfomance_df.to_dict('records'),
                                  columns=[{"name": i, "id": i} for i in portfolio_perfomance_df.columns],
                                  fill_width=False
                          )])
            ], width=6, style={'marginLeft': 'auto', 'marginRight': 'auto'},
          ),
          dbc.Col(
            [
              dcc.Dropdown(
                id='dropdown-forecast_asset',
                options=[
                  {'label':i, 'value':i} for i in tickers
                ],
                value=tickers[0],
                placeholder="Select an asset"
              ),
              dcc.Graph( id='graph-asset_forecast' ),
              html.Center([html.Div(id='table-asset_perfomance')]),
            ], width=6,
          ),
        ], justify="center", style={'marginLeft': 'auto', 'marginRight': 'auto'}
      )
    ],
  className="mt-4",
  )

  layout = html.Div([
    body
  ])
  
  return layout
  

 
