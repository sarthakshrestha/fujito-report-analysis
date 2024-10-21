import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title='Fujito Report Analysis', page_icon='📊', layout='wide')

with open("styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Page title
st.title('Fujito Report Analysis')

with st.expander('About this app'):
    st.subheader('**What can this app do?**')
    st.info('This app allows users to upload an Excel file containing report data and performs a basic analysis on it.')

    st.markdown('**How to use the app?**')
    st.warning('To use the app, upload an Excel file using the file uploader in the sidebar. The app will then display various analyses and visualizations based on the uploaded data.')

    st.markdown('**Under the hood**')
    st.markdown('Libraries used:')
    st.code('''
- Pandas for data wrangling
- Numpy for numerical operations
- Altair for chart creation
- Streamlit for user interface
    ''', language='markdown')

# Sidebar for accepting input parameters
with st.sidebar:
    st.title('Upload Data')
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Main content
if uploaded_file is not None:
    with st.status("Analyzing report...", expanded=True) as status:
        st.write("Loading data...")
        time.sleep(1)
        df = pd.read_excel(uploaded_file)

        st.write("Processing data...")
        time.sleep(1)
        
        # Simulating some basic analysis
        total_sales = df['Sales'].sum()
        avg_sales = df['Sales'].mean()
        top_product = df.groupby('Product')['Sales'].sum().idxmax()

        st.write("Generating visualizations...")
        time.sleep(1)

    status.update(label="Analysis complete", state="complete", expanded=False)

    # Display data info
    st.header('Report Overview', divider='rainbow')
    col = st.columns(3)
    col[0].metric(label="Total Sales", value=f"${total_sales:,.2f}", delta="")
    col[1].metric(label="Average Sales", value=f"${avg_sales:,.2f}", delta="")
    col[2].metric(label="Top Product", value=top_product, delta="")
    
    with st.expander('Raw Data', expanded=True):
        st.dataframe(df.style.highlight_max(axis=0), height=210, use_container_width=True)

    # Display charts
    st.header('Sales Analysis', divider='rainbow')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Product
        product_sales = df.groupby('Product')['Sales'].sum().reset_index()
        bars = alt.Chart(product_sales).mark_bar().encode(
            x=alt.X('Product', sort='-y'),
            y='Sales',
            color=alt.Color('Product', scale=alt.Scale(scheme='category10'))
        ).properties(title='Sales by Product', height=300)
        st.altair_chart(bars, use_container_width=True)

    with col2:
        # Sales Trend
        df['Date'] = pd.to_datetime(df['Date'])
        sales_trend = df.groupby('Date')['Sales'].sum().reset_index()
        line = alt.Chart(sales_trend).mark_line(point=True).encode(
            x='Date',
            y='Sales',
            tooltip=['Date', 'Sales']
        ).properties(title='Sales Trend', height=300)
        st.altair_chart(line, use_container_width=True)

    # Additional analysis
    st.header('Product Performance', divider='rainbow')
    product_performance = df.groupby('Product').agg({
        'Sales': ['sum', 'mean', 'count']
    }).reset_index()
    product_performance.columns = ['Product', 'Total Sales', 'Average Sale', 'Number of Sales']
    st.dataframe(product_performance.sort_values('Total Sales', ascending=False).style.highlight_max(axis=0), 
                 height=210, use_container_width=True)

else:
    st.warning('👈 Please upload an Excel file to start the analysis.')