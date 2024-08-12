import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tool import *
from PIL import Image
import requests
from io import BytesIO
import plotly.graph_objs as go

def main():
        
    # Set page config
    st.set_page_config(page_title="Options Data Dashboard", layout="wide")


    # Title
    st.title("CC and CSP Options Annualized Yield Calculator")

    # Sidebar for filtering
    st.sidebar.header("Filters")
    ticker = st.sidebar.text_input("Ticker", "AAPL")
    ticker = ticker.upper()

    range = st.sidebar.slider("Percentage shift from current price")


    #Display Ticker Symbol and Last Price
    st.subheader(get_company_name(ticker))

    col1, col2, col3, col4 = st.columns(4)
    low, high, yoy, last_year_price = get_yoy_price_data(ticker)
    with col1:
        st.metric("Last Price", f"${get_last_price(ticker):.2f}")
    with col2:
        st.metric("Price Difference (YoY)", f"${(get_last_price(ticker)-last_year_price):.2f}", f"{yoy:+.2f}%")
    with col3:
        st.metric("52-Week High", f"${low:.2f}")
    with col4:
        st.metric("52-Week Low", f"${high:.2f}")
    
    # st.subheader("Candlestick Chart")
    # candlestick_chart = go.Figure(data=[go.Candlestick(x=stock_data.index, open=stock_data['Open'], high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close'])])
    # candlestick_chart.update_layout(title=f"{symbol} Candlestick Chart", xaxis_rangeslider_visible=False)
    # st.plotly_chart(candlestick_chart, use_container_width=True)
    
    callbelow_df, callabove_df = get_relevant_call_options(ticker, range)
    putbelow_df, putabove_df = get_relevant_put_options(ticker, range)
    
    st.text(f"Call Options {range}% above the strike price")
    st.dataframe(callabove_df, height=int(35.2*(len(callabove_df)+1)))
    
    st.text(f"Put Options {range}% below the strike price")
    st.dataframe(putbelow_df, height=int(35.2*(len(putbelow_df)+1)))



if __name__ == '__main__' :
    main()