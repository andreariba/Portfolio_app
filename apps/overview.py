import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table


def Overview(pdb):

  cg = pdb.current_content

  fig_capital_growth = cg.homepage_capital_growth
  perfomance_df = cg.homepage_perfomance_df
  loser_gainer_df = cg.homepage_loser_gainer_df

  body = dbc.Container(
    [
      html.Center(dbc.Row(
        [
          dbc.Col(
            [        
              dcc.Graph( id='total_capital',figure=fig_capital_growth )
            ], width=7,
          ),
          dbc.Col(
            [        
              dash_table.DataTable(data=perfomance_df.to_dict('records'), columns=[{"name": i, "id": i} for i in perfomance_df.columns], fill_width=False,
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
              ),
              html.P('List of the top losers and gainers from the last year:'),
              dash_table.DataTable(data=loser_gainer_df.to_dict('records'), columns=[{"name": i, "id": i} for i in loser_gainer_df.columns], fill_width=True),
            ], width=5, align='center', style={'marginLeft': 'auto', 'marginRight': 'auto'}),
        ]))
    ]
  )

  layout = html.Div([
    body
  ])
  
  return layout
  

 
