import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

import plotly.express as px
import plotly.graph_objects as go
#from plotly.subplots import make_subplots

import yaml
import pandas as pd
#import numpy as np



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
  
  most_recent_date = melted_asset_values['Date'].max()
  most_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==most_recent_date].groupby('sector').sum().reset_index().sort_values(by='sector')
  fig_piesector = go.Figure(data=[go.Pie(values=most_recent_allocation_df.value, labels=most_recent_allocation_df.sector, sort=False) ])
  fig_piesector.update_layout(title="on "+most_recent_date,title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))

  fig_sector_growth = px.area(
        melted_asset_values, x="Date", y="value",
        color="sector", line_group="variable" )
  fig_sector_growth.update_layout(title="Capital growth",title_x=0.5)
  fig_sector_growth.update_xaxes(title_text='Last year')
  fig_sector_growth.update_yaxes(title_text='Value (EUR)')
  
  least_recent_date = melted_asset_values['Date'].min()
  least_recent_allocation_df = melted_asset_values[melted_asset_values['Date']==least_recent_date].groupby('sector').sum().reset_index().sort_values(by='sector')
  fig_piesector_initial = go.Figure(data=[go.Pie(values=least_recent_allocation_df.value, labels=most_recent_allocation_df.sector,sort=False) ])
  fig_piesector_initial.update_layout(title="on "+least_recent_date,title_x=0.5, margin=dict(t=0, b=0, l=0, r=0))

  return fig_piesector, fig_sector_growth, fig_piesector_initial


fig_piesector, fig_sector_growth, fig_piesector_initial = create_figures(portfolio_file)

body = dbc.Container(
  [
    html.H2("Allocation"),
    dbc.Row(
      [
        dbc.Col(
          [        
            dcc.Graph( id='total_capital',figure=fig_piesector_initial )
          ], width=3,
        ),
        dbc.Col(
          [        
            dcc.Graph( id='capital_by_sector',figure=fig_sector_growth )
          ], width=6,
        ),
        dbc.Col(
          [
            dcc.Graph( id='pie_chart_assets',figure=fig_piesector ),
          ], width=3,
        ),
      ]
    )
  ],
className="mt-4",
)


def Allocation():
  layout = html.Div([
    body
  ])
  
  return layout
  

 
