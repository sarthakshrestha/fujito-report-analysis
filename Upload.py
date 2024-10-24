from io import BytesIO
import io
import boto3
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

# AWS Configuration
AWS_ACCESS_KEY_ID = st.secrets["aws"]['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = st.secrets["aws"]['AWS_SECRET_ACCESS_KEY']
AWS_REGION = st.secrets["aws"]['AWS_REGION']
BUCKET_NAME = 'fujito-mis'
FILE_NAME = 'DPR 17.08.xlsx'

# Page Configuration
st.set_page_config(page_title='Report Analysis', page_icon='📊', layout='wide')
with open("./styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title('Report Analytics')

# Initialize session state if needed
if 'previous_report_type' not in st.session_state:
    st.session_state['previous_report_type'] = None
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'report_type' not in st.session_state:
    st.session_state['report_type'] = None

# Add report type selector with initial "Select Report Type" option
report_type = st.selectbox(
    "Select Report Type",
    ["Select Report Type", "DPR", "ABC", "DEF"],
    help="Choose the type of report you want to analyze"
)

# Check if report type has changed and is not the initial selection
if report_type != st.session_state['previous_report_type'] and report_type != "Select Report Type":
    st.session_state['previous_report_type'] = report_type
    # Clear previous file if report type changes
    st.session_state['uploaded_file'] = None

if report_type == "Select Report Type":
    st.info("Please select a report type to begin analysis.")
elif report_type == "DPR":
    st.info("Automatically fetching DPR file from DB...")
    
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
        st.session_state['report_type'] = "DPR"
        st.success(f"{FILE_NAME} downloaded successfully from S3!")
    except Exception as e:
        st.error(f"Error downloading {FILE_NAME} from S3: {e}")
        # Fallback to manual upload if S3 fails
        st.warning("Falling back to manual upload...")
        uploaded_file = st.file_uploader("Upload the DPR Report", type=["xlsx"])
        if uploaded_file:
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['report_type'] = "DPR"
else:
    # For ABC and DEF reports, only manual upload is available
    uploaded_file = st.file_uploader(f"Upload the {report_type} Report", type=["xlsx"])
    if uploaded_file:
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['report_type'] = report_type

# Description Expander
with st.expander('Description of the Report Analysis App', expanded=False):
    st.markdown('**What does this app do?**')
    st.info("This app automatically fetches report files from the database and performs data analysis with visual charts for different report types.")

    st.markdown('**How to use the app?**')
    st.success('1. **Select Report Type**: Start by choosing a report type (e.g., DPR, ABC, DEF) from the dropdown.\n'
               '2. **Automatic Fetch**: The app automatically retrieves the selected report from the database.\n'
               '3. **View Data**: A preview of the fetched data is shown for quick validation.\n'
               '4. **Analyze and Visualize**: You can explore the data through visual charts and summaries.')
    
    st.markdown('**Under the Hood**')
    st.code('''- Pandas: Data analysis\n- NumPy: Numerical operations\n- Altair: Charts\n- Streamlit: User interface''', language='markdown')


# Main content
if st.session_state["uploaded_file"]:
    uploaded_file = st.session_state['uploaded_file']
    
    with st.status(f"Analyzing {st.session_state['report_type']} report...", expanded=True) as status:
        if isinstance(uploaded_file, bytes):
            file_buffer = io.BytesIO(uploaded_file)
        else:
            file_buffer = uploaded_file
            
        # Adjust sheet name and skip rows based on report type
        sheet_params = {
            "DPR": {"sheet_name": "Main", "skiprows": 1},
            "ABC": {"sheet_name": "Sheet1", "skiprows": 0},
            "DEF": {"sheet_name": "Sheet1", "skiprows": 0}
        }
        
        current_params = sheet_params[st.session_state['report_type']]
        df = pd.read_excel(file_buffer, **current_params)
        st.session_state["df"] = df
        
        if st.session_state['report_type'] == "DPR":
            df = df.drop(df.columns[0], axis=1)
        
        st.write(f"**Preview of the {st.session_state['report_type']} Data**")
        st.write(df.head(5))
    
    status.update(label="Analysis complete", state="complete", expanded=False)
else:
    st.caption('Built by:')
    st.text('Digital Horizons')