import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

import plotly.express as px
import plotly.graph_objects as go


from utils.Portfolio import PortfolioManager, PortfolioSimulation, create_allocation_figures

pm = PortfolioManager()
ps = PortfolioSimulation(pm)



fig_piesector, fig_sector_growth, fig_piesector_initial = create_allocation_figures(pm)

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
  

 
