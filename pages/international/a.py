# inspired from https://towardsdatascience.com/visualise-covid-19-case-data-using-python-dash-and-plotly-e58feb34f70f

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from os.path import isfile
from app import app


#https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/allData.pkl
#https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
#baseURL = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/"
baseURL = "static/csv/"
fileNamePickle = "allData.pkl"

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

def loadData(fileName, columnName): 
    data = pd.read_csv(baseURL + fileName) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore')
    data['Province/State'].fillna('<all>', inplace=True)
    data[columnName].fillna(0, inplace=True)
    return data

def refreshData():
    allData = loadData("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
        .merge(loadData("time_series_covid19_deaths_global.csv", "CumDeaths")) \
        .merge(loadData("time_series_covid19_recovered_global.csv", "CumRecovered"))
    allData.to_pickle(fileNamePickle)
    return allData

def allData():
    if not isfile(fileNamePickle):
        refreshData()
    allData = pd.read_pickle(fileNamePickle)
    return allData

countries = allData()['Country/Region'].unique()
countries.sort()

def display_a():
    return [
        html.H1('Case History of the Coronavirus (COVID-19)'),
        html.Div(className="row", children=[
            html.Div(className="four columns", children=[
                html.H5('Country'),
                dcc.Dropdown(
                    id='country',
                    options=[{'label':c, 'value':c} for c in countries],
                    value='Italy'
                )
            ]),
            html.Div(className="four columns", children=[
                html.H5('State / Province'),
                dcc.Dropdown(
                    id='state'
                )
            ]),
            html.Div(className="four columns", children=[
                html.H5('Selected Metrics'),
                dcc.Checklist(
                    id='metrics',
                    options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths', 'Recovered']],
                    value=['Confirmed', 'Deaths']
                )
            ])
        ]),
        dcc.Graph(
            id="plot_new_metrics",
            config={ 'displayModeBar': False }
        ),
        dcc.Graph(
            id="plot_cum_metrics",
            config={ 'displayModeBar': False }
        ),
        dcc.Interval(
            id='interval-component',
            interval=3600*1000, # Refresh data each hour.
            n_intervals=0
        )

    ]


def callback_a(app):

    @app.callback(
        [Output('state', 'options'), Output('state', 'value')],
        [Input('country', 'value')]
    )
    def update_states(country):
        d = allData()
        states = list(d.loc[d['Country/Region'] == country]['Province/State'].unique())
        states.insert(0, '<all>')
        states.sort()
        state_options = [{'label':s, 'value':s} for s in states]
        state_value = state_options[0]['value']
        return state_options, state_value
    
    def filtered_data(country, state):
        d = allData()
        data = d.loc[d['Country/Region'] == country].drop('Country/Region', axis=1)
        if state == '<all>':
            data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
        else:
            data = data.loc[data['Province/State'] == state]
        #data=pd.DataFrame(data[['CumConfirmed']], dtype='float32')
        newCases = data.select_dtypes(include='Int64')#.diff().fillna(0)
        newCases = pd.DataFrame(newCases, dtype='float32')
        newCases = newCases.diff().fillna(0)
        #print (newCases.dtypes)
        #print (newCases)
        #print (newCases.dtypes)
        #print (newCases.diff(axis=0))
        newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
        data = data.join(newCases)
        data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
        return data
    
    def barchart(data, metrics, prefix="", yaxisTitle=""):
        figure = go.Figure(data=[
            go.Bar( 
                name=metric, x=data.date, y=data[prefix + metric],
                marker_line_color='rgb(0,0,0)', marker_line_width=1,
                marker_color={ 'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
            ) for metric in metrics
        ])
        figure.update_layout( 
                  barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
                  plot_bgcolor='#FFFFFF', font=tickFont) \
              .update_xaxes( 
                  title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
                  tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
              .update_yaxes(
                  title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
        return figure
    
    @app.callback(
        [Output('plot_new_metrics', 'figure'), Output('plot_cum_metrics', 'figure')], 
        [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value'), Input('interval-component', 'n_intervals')]
    )
    def update_plots(country, state, metrics, n):
        refreshData()
        data = filtered_data(country, state)
        barchart_new = barchart(data, metrics, prefix="New", yaxisTitle="New Cases per Day")
        barchart_cum = barchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")
        return barchart_new, barchart_cum        

            
#print (update_plots('Belgium','<all>',['Confirmed'],'0') )          
            
#server = app.server
#
#if __name__ == '__main__':
#    app.run_server(host="0.0.0.0")
            
            
            