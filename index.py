import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table
import dash_bootstrap_components as dbc

from apps.homepage import Homepage
from apps.allocation import Allocation
from apps.forecast import Forecast
from navbar import Navbar

from utils.Portfolio import PortfolioManager, PortfolioSimulation, forecast_asset_figure


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.LUX])
app.config.suppress_callback_exceptions = True


app.layout = html.Div([
  dcc.Location(id='url',refresh=False),
  Navbar(),
  html.Div(id='page-content')
])

pm = PortfolioManager()
ps = PortfolioSimulation(pm)

#create app pages
home_page = Homepage()
forecast_page = Forecast()
allocation_page = Allocation()

@app.callback( Output('page-content','children'), [Input('url','pathname')] )
def display_page(pathname):
  print(pathname)
  if pathname=='/forecast':
    return forecast_page
  elif pathname=='/allocation':
    return allocation_page
  elif pathname=='/home':
    return home_page
  else:
    return home_page


@app.callback( [Output('asset_forecast', 'figure'), Output('table_asset_perfomance', 'children')], Input('asset_dropdown', 'value') )
def update_asset_forecast(value):
  figure, perfomance_df = forecast_asset_figure(ps, value)
  return figure, dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False)

    
if __name__=='__main__':
  app.run_server(debug=True)
  
