import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import app_data
import base64
import datetime
import io
covid = app_data.getCovidCountry()
countryList= covid.country.drop_duplicates()
indiceList=pd.read_csv('assets/worldIndices.csv')
indiceList=dict(zip(indiceList.Symbol,indiceList.Name))
confirmed = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
deaths = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
recovered = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')
port=pd.read_csv('assets/portfolio.csv')
box_shadow = {'box-shadow': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
              'padding': '16px', 'border-radius': '15px','position':'fixed'}
container_style={'width':'85%', 'backgroundColor': '#1B1C1D', 'padding': '16px', 'padding-top':'70px'}
rssDict={
    'r/Coronavirus':'http://www.reddit.com/r/Coronavirus/.rss', 
    'r/wallstreetbets':'http://www.reddit.com/r/wallstreetbets/.rss', 
    'WHO news':'https://www.who.int/rss-feeds/news-english.xml', 
    'bbc news':'http://feeds.bbci.co.uk/news/world/rss.xml', 
    'Reuters':'http://feeds.reuters.com/Reuters/worldNews'

}
upload_style={
        'width': '100%',
        'height': '40px',
        'lineHeight': '40px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'color' : '#8B8B8D'
    }
external_stylesheets = [{
    'href': 'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    'rel': 'stylesheet'},
    dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Protfolio'

upload=dcc.Upload(
        id='upload-data',
        children=html.P([
            'Drag and Drop Your Portfolio'
        ]), 
        style=upload_style
    )

graph=dcc.Graph(id='mainGraph')

subGraph=dcc.Graph(id='subGraph', figure=app_data.subGraph(port))

indicator=dcc.Graph(id='indicator')

title=dbc.Container(
    html.H4('The Coronavirus And Stock Market'),
    style={'width':'1300px', 'padding':'10px', 'position':'fixed', 'z-index':'1000', 'backgroundColor': '#1B1C1D'},
    fluid=True 
   )

import dash_bootstrap_components as dbc

form = dbc.Row(
    [
        dbc.Col(
            dbc.FormGroup(
                [
                    dbc.Label([html.I(className='fa fa-sliders')," Index"], html_for="example-email-grid"),
                    dbc.Select(
                        id='indexSelect',
                        options=[{'label':row[1], 'value':row[0]} for row in indiceList.items()],
                        value='^IXIC', 
                        style={'backgroundColor': '#1B1C1D','color':'white'}),
                ]
            ),
            width=6,
        ),
        dbc.Col(
            dbc.FormGroup(
                [
                    dbc.Label([html.I(className='fa fa-globe')," Country"], html_for="example-password-grid"),
                    dbc.Select(
                        id='countrySelect',
                        options=[{'label':i, 'value':i} for i in countryList],
                        value='US',
                        style={'backgroundColor': '#1B1C1D','color':'white'})
                ]
            ),
            width=6,
        ),
    ],
    form=True,
)
portfolio=html.Div([
    dbc.Label([html.I(className='fa fa-pie-chart')," Portfolio"], html_for="example-email-grid"), 
    subGraph,
    ],
    style={'margin-top':'30px'}
    )

rss_input = dbc.FormGroup(
    [
        dbc.Label("RSS Feeds"),
        dbc.Select(
            id="rssSelect",
            options=[{"label": i[0], "value": i[1]} for i in rssDict.items()],
            style={'backgroundColor': '#1B1C1D','color':'white' }, 
            value='http://www.reddit.com/r/Coronavirus/.rss'
        ),
        dbc.FormText("Get the most updated news"),
    ], 
    style={'width':'30%'}
)

reddit=app_data.getRss('http://www.reddit.com/r/Coronavirus/.rss')

rss=html.Div(id='rss')

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([graph, indicator,rss_input,rss],md=8),
                dbc.Col([form,upload, portfolio],md=3, style=box_shadow, width={"offset": 7}),
            ])
    ],
    style=container_style,
    fluid=True
)


app.layout = html.Div(
    [title,body], 
    style={'backgroundColor': '#1B1C1D', 'color': '#FEFDFD',})

@app.callback(
    [Output(component_id='mainGraph', component_property='figure'), 
    Output(component_id='indicator', component_property='figure')],
    [Input(component_id='countrySelect', component_property='value'),
    Input(component_id='indexSelect', component_property='value') ]
)
def updateGraph(country, index):
    return [app_data.mainGraph(indiceList[index], index, country), app_data.indicator(country)]

@app.callback(Output('subGraph', 'figure'),
              [Input('upload-data', 'contents')],)
def update_output(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return app_data.subGraph(df)


@app.callback(Output('rss', 'children'),
              [Input('rssSelect', 'value')],)
def update_rss(contents):
    df=app_data.getRss(contents)
    return [html.P([html.A(row[1][0], href=row[1][1], style={'color': '#FEFDFD'}), ' - ',html.Small(['(',row[1][2].split('+')[0].replace('T', ': '), ')'])]) for row in df.iterrows()]



if __name__ == '__main__':

    app.run_server(host='0.0.0.0', port='8050')


