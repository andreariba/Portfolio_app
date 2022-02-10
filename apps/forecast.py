import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

import plotly.express as px
import plotly.graph_objects as go
#from plotly.subplots import make_subplots

import yaml
import datetime
import pandas as pd
import numpy as np

from copulas.univariate import ParametricType, Univariate
from copulas.multivariate import GaussianMultivariate
from copulas.visualization import scatter_3d, compare_3d



portfolio_file = 'portfolio.yml'

with open('portfolio.yml','r') as file:
  portfolio_data = yaml.load(file, Loader=yaml.FullLoader)
    
stocks = portfolio_data['stocks']
currency = portfolio_data['currency']
sectors = portfolio_data['sectors']
stock_sectors = portfolio_data['stock_sectors']

n_simulations = 200
trading_days = 253

def make_predictions(input_file):
  
  asset_values = pd.read_csv('asset_values.csv',index_col=0)
  pct_values = pd.read_csv('pct_values.csv',index_col=0)
  
  pct_values = pct_values.dropna(axis=1, how='all')
  pct_values = pct_values.dropna(axis=0, how='any')
  asset_values = asset_values.fillna(0)
  
  symbols = list(pct_values.columns)
  
  data_pct = round(pct_values[symbols],2)
  data_price = round(asset_values[symbols],2)
  
  least_recent_date = data_price.index.min()
  most_recent_date = data_price.index.max()
  
  univariate = Univariate(parametric=ParametricType.PARAMETRIC)
  dist = GaussianMultivariate(distribution=univariate)
  dist.fit(data_pct)

  sampled = dist.sample(trading_days*n_simulations)

  x0 = data_price.loc[most_recent_date].loc[sampled.columns].to_numpy()

  simulations = np.array([], dtype=float)

  # run the simulations
  for i in range(n_simulations):
    
    # x stores the changing values of the variables across the simulation.
    # x starts by copying the initial values stored in x0.
    x = np.copy(x0).astype(float) 
    
    # function to sample 'size'(=lenght=4) times from  
    # a multivariate normal distribution with specified mean and covariance
    pct_changes = sampled.iloc[i*trading_days:(i+1)*trading_days]

    #print( i, (i+1)*trading_days )
    # array storing a single simulation initialized 
    # with the initial value x that is equal to x0
    simulation = np.array(x)
    
    # for each of the 4 sampled returns I update iteratively
    # the values in the vector x
    for idx, row in pct_changes.iterrows():

      for a in range(len(row)):
        x[a] = x[a]*(1+row[a]/100)
        if x[a]<0:
          x[a]=0.0
            
      simulation = np.append(simulation, x)

    #reshape the simulation array
    simulation = simulation.reshape(trading_days+1,-1)
    
    # appending the single simulation to the simulations array
    if i==0:
        simulations = simulation[...,np.newaxis]
    else:
        simulations = np.append(simulations,simulation[...,np.newaxis], axis=2)
        
  return data_price, data_pct, simulations


def generate_portfolio_figure(data_price, simulations):
  
  portfolio_simulations = simulations.sum(axis=1)
  portfolio_median = np.median(portfolio_simulations, axis=1)
  portfolio_std = portfolio_simulations.std(axis=1)
  portfolio_q95 = np.quantile(portfolio_simulations, q=0.95, axis=1)
  portfolio_q05 = np.quantile(portfolio_simulations, q=0.05, axis=1)
  
  historical_portfolio = data_price.sum(axis=1)
  business_days_to_add = trading_days
  current_date = datetime.datetime.strptime(historical_portfolio.index.max(),'%Y-%m-%d')
  forecasted_dates = [current_date]
  while business_days_to_add > 0:
    current_date += datetime.timedelta(days=1)
    weekday = current_date.weekday()
    if weekday >= 5: # sunday = 6
      continue
    business_days_to_add -= 1
    forecasted_dates.append(current_date)
  
  lines = []
  for i in range(n_simulations):
    line = go.Scatter(x=forecasted_dates, y=portfolio_simulations[:,i], mode="lines", opacity=.1, line_color='gray')
    lines.append(line) 
            
  fig_portfolio_prediction = go.Figure(
    data=lines,
    layout=go.Layout(showlegend=False)
  )

  fig_portfolio_prediction.add_trace(go.Scatter(x=historical_portfolio.index, 
                           y=historical_portfolio, line_color='blue',
                           fill=None, showlegend=False))

  fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                           y=portfolio_q05, line_color='orange',
                           fill=None, showlegend=False))
  fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                           y=portfolio_q95, line_color='orange', 
                           fill='tonexty', showlegend=False))
  fig_portfolio_prediction.add_trace(go.Scatter(x=forecasted_dates, 
                           y=portfolio_median, line_color='red',
                           showlegend=False))

  fig_portfolio_prediction.update_yaxes(type="log")
  fig_portfolio_prediction.update_layout(title_text="Portfolio Forecast", xaxis_title="Trading days",yaxis_title="Value (€)",title_x=0.5)
  
  forecast_pct_q95 = (portfolio_q95[-1]/historical_portfolio[-1]-1)*100
  forecast_pct_median = (portfolio_median[-1]/historical_portfolio[-1]-1)*100
  forecast_pct_q05 = (portfolio_q05[-1]/historical_portfolio[-1]-1)*100
  perfomance_array = np.array([[portfolio_median[-1],portfolio_q05[-1],portfolio_q95[-1]],
                               [forecast_pct_median,forecast_pct_q05,forecast_pct_q95]])

  perfomance_df = pd.DataFrame(perfomance_array.astype(int), 
                               columns=['Median','Value at Risk 5%', 'q95'],
                               index=['Value (€)', 'Relative change (%)' ]
                              ).reset_index()
                              
  perfomance_df.columns.values[0] = ''                 
  
  return fig_portfolio_prediction, perfomance_df
  

def forecast_asset_figure(ticker):

  simulated_medians = np.median(simulations, axis=2)
  simulated_stds = np.std(simulations, axis=2)
  simulated_q95 = np.quantile(simulations, q=0.95, axis=2)
  simulated_q05 = np.quantile(simulations, q=0.05, axis=2)

  historical_prices = data_price.replace(0,np.nan)[ticker]
  business_days_to_add = trading_days
  current_date = datetime.datetime.strptime(historical_prices.index.max(),'%Y-%m-%d')
  forecasted_dates = [current_date]
  while business_days_to_add > 0:
    current_date += datetime.timedelta(days=1)
    weekday = current_date.weekday()
    if weekday >= 5: # sunday = 6
      continue
    business_days_to_add -= 1
    forecasted_dates.append(current_date)
  
  i = data_price.columns.get_loc(ticker)
  
  lines = []
  for j in range(n_simulations):
    line = go.Scatter(x=forecasted_dates, y=simulations[:,i,j], mode="lines", opacity=.1, line_color='gray', showlegend=False)
    lines.append(line)       

  fig = go.Figure(
    data=lines,
    layout=go.Layout(showlegend=False)
  )

  fig.add_trace(go.Scatter(x=data_price.index, 
                             y=historical_prices, line_color='blue',
                             fill=None, showlegend=False))    
  fig.add_trace(go.Scatter(x=forecasted_dates, 
                             y=simulated_q05[:,i], line_color='orange',
                             fill=None, showlegend=False))
  fig.add_trace(go.Scatter(x=forecasted_dates, 
                             y=simulated_q95[:,i], line_color='orange', 
                             fill='tonexty', showlegend=False))
  fig.add_trace(go.Scatter(x=forecasted_dates, 
                             y=simulated_medians[:,i], line_color='red',
                             showlegend=False))

  fig.update_layout(title_text=ticker,xaxis_title="Trading days",yaxis_title="Value (€)",title_x=0.5)
  
  historical_prices = historical_prices.to_numpy()
  
  forecast_pct_q95 = (simulated_q95[-1,i]/historical_prices[-1]-1)*100
  forecast_pct_median = (simulated_medians[-1,i]/historical_prices[-1]-1)*100
  forecast_pct_q05 = (simulated_q05[-1,i]/historical_prices[-1]-1)*100
  perfomance_array = np.array([[simulated_medians[-1,i],simulated_q05[-1,i],simulated_q95[-1,i]],
                               [forecast_pct_median,forecast_pct_q05,forecast_pct_q95]])

  #print(perfomance_array)
  #print(perfomance_array.astype(int))
  perfomance_df = pd.DataFrame(perfomance_array.astype(int), 
                               columns=['Median','Value at Risk 5%', 'q95'],
                               index=['Value (€)', 'Relative change (%)' ]
                              ).reset_index()
                              
  perfomance_df.columns.values[0] = ''

  return fig, perfomance_df


data_price, data_pct, simulations = make_predictions(portfolio_file)
fig_portfolio_prediction, portfolio_perfomance_df = generate_portfolio_figure(data_price, simulations)
#fig_asset_forecast = forecast_asset([0])


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
                {'label':i, 'value':i} for i in stocks
              ],
              value=list(stocks.keys())[0],
              placeholder="Select an asset"
            ),
            dcc.Graph( id='asset_forecast' ),
            #html.P( "Montecarlo simulations predict the following scenario for the portfolio:"),
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
  

 
