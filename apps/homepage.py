import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

import plotly.express as px
import plotly.graph_objects as go
#from plotly.subplots import make_subplots

import yaml
import pandas as pd
import numpy as np



portfolio_file = 'portfolio.yml'



def create_figures(input_file):
  with open('portfolio.yml','r') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    portfolio_data = yaml.load(file, Loader=yaml.FullLoader)

  stocks = portfolio_data['stocks']
  currency = portfolio_data['currency']
  sectors = portfolio_data['sectors']
  stock_sectors = portfolio_data['stock_sectors']
 
  asset_values = pd.read_csv('asset_values.csv',index_col=0)
  pct_values = pd.read_csv('pct_values.csv',index_col=0)
  
  melted_asset_values = asset_values.melt(ignore_index=False).reset_index()
  melted_asset_values['sector'] = melted_asset_values['variable'].map(stock_sectors).map(sectors)
  melted_asset_values = melted_asset_values.sort_values(by='sector')
  
  fig_capital_growth = px.line(melted_asset_values.groupby('Date').sum(),labels=dict(Date="Last year", _value="Capital (EUR)"))
  fig_capital_growth.update_layout(title="Growth in the last year", title_x=0.5,showlegend=False)
  
  asset_1y_perfomance = ((asset_values.iloc[-1]/asset_values.iloc[0]-1)*100)
  asset_1y_perfomance = round(asset_1y_perfomance,2)
  loser_gainer_df = pd.concat([asset_1y_perfomance.sort_values()[:5].reset_index(), asset_1y_perfomance.sort_values(ascending=False)[:5].reset_index()], axis=1)
  loser_gainer_df.columns = ['Losers', '% change (losers)','Gainers', '% change (gainers)']
  
  portfolio_value = asset_values.sum(axis=1)
  last_year_perfomance = round((portfolio_value.iloc[-1]/portfolio_value.iloc[0]-1)*100,2)
  portfolio_pct_change = portfolio_value.to_numpy()
  portfolio_pct_change = (portfolio_pct_change[1:]/portfolio_pct_change[:-1]-1)*100
  volatility = round(np.std(portfolio_pct_change),2)
  
  perfomance_df = pd.DataFrame.from_dict( {'Perfomance (%)':[last_year_perfomance], 'Volatility (%)':[volatility]})
  
  return fig_capital_growth, perfomance_df, loser_gainer_df


fig_capital_growth, perfomance_df, loser_gainer_df = create_figures(portfolio_file)

body = dbc.Container(
  [
    html.H2("Summary"),
    dbc.Row(
      [
        dbc.Col(
          [        
            dcc.Graph( id='total_capital',figure=fig_capital_growth )
          ], width=7,
        ),
        dbc.Col(
          [        
                        html.Center([dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False,
                                             style_cell={'textAlign': 'center'},
                                             style_data={'backgroundColor': 'green', 
                                                  'color':'white', 
                                                  'fontWeight': 'bold',
                                                  'font-size': '26px',
                                                  'border': '1px solid green'
                                             }, 
                                             style_header={
                                                  'backgroundColor': 'green',
                                                  'color': 'white',
                                                  'fontWeight': 'bold',
                                                  'border': '1px solid green'
                                             }
                        )]),
                        html.P('List of the top losers and gainers from the last year:'),
                        dash_table.DataTable(data=loser_gainer_df.to_dict('records'), columns=[{"name": i, "id": i} for i in loser_gainer_df.columns], fill_width=True),
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
  

 
