from io import BytesIO
import io

import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

AWS_ACCESS_KEY_ID = st.secrets["aws"]['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = st.secrets["aws"]['AWS_SECRET_ACCESS_KEY']
AWS_REGION = st.secrets["aws"]['AWS_REGION']


BUCKET_NAME = 'fujito-mis'  
FILE_NAME = 'DPR 17.08.xlsx'
   


# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title='Fujito Report Analysis', page_icon='📊', layout='wide')
with open( "./styles.css" ) as css:
            st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# Page title
st.title('Report Analytics')


# Button to download file from S3
if st.button("Fetch File from DB"):
    st.info("Downloading the file from DB...")

    # Initialize the S3 client with credentials
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    try:
        # Download the file from S3
        s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        uploaded_file = s3_response['Body'].read()
        
        # Store the uploaded file in session state
        st.session_state['uploaded_file'] = uploaded_file
        st.success(f"{FILE_NAME} downloaded successfully from S3!")
    except Exception as e:
        st.error(f"Error downloading {FILE_NAME} from S3: {e}")
else:
    # Option to upload manually if not using S3
    uploaded_file = st.file_uploader("Upload the excel file of (DPR Report)", type=["xlsx"])
    
    if uploaded_file:
        st.session_state['uploaded_file'] = uploaded_file


with st.expander('Description of the Report Analysis App', expanded=False):
    st.markdown('**What can this app do?**')
    st.info('This app allows you to perform a data analysis along with visual chart elements on the Master sheet within the PDR Report.')
    
    st.markdown('**How to use the app?**')
    st.warning('To use the app, simply upload the DPR report through the file uploader in the sidebar. The app will then display various analyses and visualizations based on the uploaded data.')
    
    st.markdown('**Under the hood**')
    st.markdown('Libraries used:')
    st.code('''
    - Pandas for data wrangling
    - Numpy for numerical operations
    - Altair for chart creation
    - Streamlit for the user interface
    ''', language='markdown')

if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None

# Sidebar for accepting input parameters

   
# Main content
if st.session_state["uploaded_file"]:
    uploaded_file = st.session_state['uploaded_file']

    with st.status("Analyzing report...", expanded=True) as status:
        if isinstance(uploaded_file, bytes):
            file_buffer = io.BytesIO(uploaded_file)
        else:
            file_buffer = uploaded_file
        # Skip rows if necessary and use the appropriate row as the header
        df = pd.read_excel(file_buffer, sheet_name="Main", skiprows=1)
        st.session_state["df"] = df
        
        # Drop the first column (if it's unwanted)
        df = df.drop(df.columns[0], axis=1)
        
        st.write("**Preview of the Data**")
        st.write(df.head(5))

    # Enhanced Average Balance Analysis


    # Overdue Reasons Analysis
   

    

    status.update(label="Analysis complete", state="complete", expanded=False)
else:
    st.info('Upload the Report for the analysis at the top of the page.')
    st.caption('Built by:')
    st.text('Digital Horizons')
