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
        name=country+' Confirmed Cases',
        fillcolor='rgba(209, 55, 31, 0.3)',
        mode='none'
    ))

    fig.add_trace(go.Scatter(
        x=x, 
        y=y,
        mode='lines',
        line_color='#43CE99',
        name=title + ' (' + ticker+')',
    ))
    fig.update_layout(yaxis_title='Index' )

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
    fig.update_layout(font=dict(size=9, color="white"))
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        title={"text": "<span style='color:#7f7f7f'>Comfirmed</span>"},
        value = today[2],
        number={'font':{'size':40}},
        domain = {'row': 0, 'column': 0},
        delta = {'reference': yesterday[2],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        title={"text": "<span style='color:#7f7f7f'>Recovered</span>"},
        value = today[4],
        number={'font':{'size':40}},
        delta = {'reference': yesterday[4],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}},
        domain = {'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = today[3],
        title={"text": "<span style='color:#7f7f7f'>Deaths</span>"},
        number={'font':{'size':40}},
        delta = {'reference': yesterday[3],'font':{'size':20}, 'relative': True, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':"#3D9970"}},
        domain = {'row': 0, 'column': 2}))

    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})
    fig.update_layout(
        # autosize=False,
        # width=900,
        # height=300,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=200
        ),
        paper_bgcolor='#1B1C1D',
    )
    return fig, str(today[1]).split()[0]


def subGraph(port):
    port[['Symbol', 'Stock']]
    portDict=dict(zip(port.Symbol, port.Stock))
    
    df=getIndices('2018-01-01',datetime.today(),port.Symbol)
    fig = go.Figure()
    fig.update_layout({'legend_orientation': 'h'})
    fig.update_layout(legend=dict(x=-.1, y=1.2))
    fig.update_layout(font=dict(size=9, color="#7f7f7f"))
    fig.update_layout(plot_bgcolor='#1B1C1D')
    fig.update_layout(
        autosize=False,
        width=450,
        height=200,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        paper_bgcolor='#1B1C1D',
    )
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


def getQuote(port):
    quote=data.get_quote_yahoo(port.Symbol).price
    quote=quote.rename('currentPrice')
    port=port.merge(quote.to_frame(),left_on='Symbol', right_index=True)
    port['Profit']=(port.currentPrice-port.Price)*port.Share
    port['Total']=port.currentPrice*port.Share
    return port, datetime.now().strftime("%m/%d/%Y, %H:%M:%S")



def portIndicator(port):
    quote, time=getQuote(port)
    fig = go.Figure(go.Indicator(
        title={"text": "<span style='font-size:15; color:#7f7f7f'>Value</span>"},
        mode = "number+delta",
        value = quote.Total.sum(),
        number = {'prefix': "$"},
        delta = {'relative': True,'reference': sum(quote.Price*quote.Share)},
        domain = {'x': [0, 1], 'y': [0, 1]}
        ))
    fig.update_layout(font=dict(color="white"))
    fig.update_layout(
        autosize=False,
        width=450,
        height=200,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        paper_bgcolor='#1B1C1D',
    )

    return fig

def portTable(port):
    quote, time=getQuote(port)
    values = [quote.Stock, quote.Share,quote.Price,quote.currentPrice,round(quote.Profit,2)]

    fig = go.Figure(data=[go.Table(
      columnorder = [1,2,3,4,5],
      columnwidth = [20,20, 20],
      header = dict(
        values = ['Watch List','Shares','Purchase Price', 'Current Price', 'Profit'],
        align=['left'],
        fill=dict(color=['#1B1C1D', '#1B1C1D']),
        font=dict(color=['white', '#7f7f7f', '#7f7f7f'], size=[15, 11, 11]),
          line_color='#1B1C1D',
        height=25
      ),
      cells=dict(
        values=values,
        line_color='black',
        fill=dict(color=['#1B1C1D', '#1B1C1D']),
        align=['left', 'left', 'left'],
        font=dict(color='white', size=12),
        height=30)
        )
    ])

    fig.update_layout(
        autosize=False,
        width=500,
        height=120,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        paper_bgcolor='#1B1C1D',
    )
    return fig