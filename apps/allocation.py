import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


def Allocation(pdb):

  cg = pdb.current_content

  fig_piesector = cg.allocation_piesector
  fig_sector_growth = cg.allocation_sector_growth
  fig_piesector_initial = cg.allocation_piesector_initial

  body = dbc.Container(
    [
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

  layout = html.Div([
    body
  ])
  
  return layout
  

 
