#!/usr/bin/env python3

import plotly.graph_objects as go

indicator = go.Indicator(
  domain = {'x': [0, 1], 'y': [0, 1]},
  value = 450,
  mode = "gauge+number+delta",
  title = {'text': "Speed"},
  delta = {'reference': 380},
  gauge = {'axis': {'range': [None, 500]},
           'steps' : [
               {'range': [0, 250], 'color': "lightgray"},
               {'range': [250, 400], 'color': "gray"}
            ],
            'threshold' : {
              'line': {
                'color': "red",
                'width': 4
              },
              'thickness': 0.75, 'value': 490
            }
          }
)

fig = go.Figure(indicator)

#fig.show()

import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True, use_reloader=False)
