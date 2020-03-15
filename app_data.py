import pandas as pd
from pandas_datareader import data
from datetime import datetime
import plotly.graph_objects as go
import feedparser as fp

def getCovidCountry():
    confirmed = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
    deaths = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
    recovered = pd.read_csv('assets/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')
    country_confirmed = confirmed.drop(['Province/State', 'Lat','Long'], 1).groupby('Country/Region').sum()
    country_deaths = deaths.drop(['Province/State', 'Lat','Long'], 1).groupby('Country/Region').sum()
    country_recovered = recovered.drop(['Province/State', 'Lat','Long'], 1).groupby('Country/Region').sum()
    country_confirmed = country_confirmed.stack()
    country_deaths = country_deaths.stack()
    country_recovered = country_recovered.stack()
    country_confirmed = country_confirmed.to_frame().reset_index(level=[0,1])
    country_confirmed.rename(columns={'Country/Region':'country', 'level_1':'Date', 0:'confirmed'}, inplace=True)
    country_deaths = country_deaths.to_frame().reset_index(level=[0,1])
    country_deaths.rename(columns={'Country/Region':'country', 'level_1':'Date', 0:'deaths'}, inplace=True)
    country_recovered = country_recovered.to_frame().reset_index(level=[0,1])
    country_recovered.rename(columns={'Country/Region':'country', 'level_1':'Date', 0:'recovered'}, inplace=True)
    df = pd.merge(country_confirmed, country_deaths,on=['country', 'Date'])
    df = pd.merge(df, country_recovered,on=['country', 'Date'])
    return df

def getIndices(start, end, ticker):
    start_date = start
    end_date = end
    ticker = ticker

    df = data.get_data_yahoo(ticker, start_date, end_date)
    df = df.reset_index()
    return df[['Date', 'Close']]


def mainGraph(title, ticker, country, start='2020-01-22', end=datetime.today()):
    fig = go.Figure()
    # fig.update_layout(width=900, height=300)
    fig.update_layout(font=dict(size=9, color="#7f7f7f"))
    fig.update_layout({'legend_orientation': 'h'})
    # fig.update_layout(legend=dict(x=-.1, y=1.2))
    fig.update_layout(plot_bgcolor='#1B1C1D')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    stock=getIndices(start,end,ticker)
    covid=getCovidCountry()
    covid=covid[covid.country==country]
    covid.Date=pd.to_datetime(covid.Date, format='%m/%d/%y')
    df=stock.merge(covid, on=['Date', 'Date'])
    x=df.Date
    y=df['Close']
    y_upper=y+df['confirmed']/2
    y_lower=y-df['confirmed']/2

    fig.add_trace(go.Scatter(
        x=x,
        y=y_upper,
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=y_lower,
        fill='tonexty',
        name=country+' confirmed',
        fillcolor='rgba(209, 55, 31, 0.3)',
        mode='none'
    ))

    fig.add_trace(go.Scatter(
        x=x, 
        y=y,
        mode='lines',
        line_color='#43CE99',
        name=ticker,
    ))
    fig.update_layout(title_text=title, 
                      yaxis_title='Index' )

    fig.update_layout(yaxis=dict(zeroline=False))
    return fig

def getRecent(country):
    df= getCovidCountry()
    df.Date=pd.to_datetime(df.Date, format='%m/%d/%y')
    df=df[df.country==country]
    df=df.sort_values(by=['Date'], ascending=False)
    df=df.iloc[0:2] if df.iloc[0].confirmed!=0 else df.iloc[1:3]
    return [list(df.iloc[0]), list(df.iloc[1])]


def indicator(country):
    df=getRecent(country)
    today, yesterday=df
    fig = go.Figure()
    fig.update_layout(width=900, height=300)
    fig.update_layout(paper_bgcolor='#1B1C1D')
    fig.update_layout(font=dict(size=9, color="#7f7f7f"))
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        title = 'Comfirmed',
        value = today[2],
        number={'font':{'size':40}},
        domain = {'row': 0, 'column': 0},
        delta = {'reference': yesterday[2],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        title = 'Recovered',
        value = today[4],
        number={'font':{'size':40}},
        delta = {'reference': yesterday[4],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}},
        domain = {'row': 0, 'column': 2}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = today[3],
        title = 'Deaths',
        number={'font':{'size':40}},
        delta = {'reference': yesterday[3],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}},
        domain = {'row': 0, 'column': 4}))

    fig.update_layout(
        grid = {'rows': 1, 'columns': 5, 'pattern': "independent"})
    fig.update_layout(title_text='Last Updated: '+str(today[1]).split()[0] )
    return fig


def subGraph(port):
    port[['Symbol', 'Stock']]
    portDict=dict(zip(port.Symbol, port.Stock))
    
    df=getIndices('2018-01-01',datetime.today(),port.Symbol)
    fig = go.Figure()
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(width=500, height=300)
    fig.update_layout({'legend_orientation': 'h'})
    fig.update_layout(legend=dict(x=-.1, y=1.2))
    fig.update_layout(font=dict(size=9, color="#7f7f7f"))
    fig.update_layout(plot_bgcolor='#1B1C1D')
    for i in df.Close.columns:
        fig.add_trace(go.Scatter(
            x=df.Date,
            y=df.Close[i],
            mode='lines',
            name=portDict[i]
        ))
    return fig

def getRss(link):
    rss = fp.parse(link)
    posts=[]
    for post in rss.entries:
        posts.append((post.title, post.link, post.updated))
    df=pd.DataFrame(posts, columns=['title', 'link', 'updated'])
    return df.sort_values(by=['updated'], ascending=False)
