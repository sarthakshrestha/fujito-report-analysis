from io import BytesIO
import io
import os
import boto3
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

load_dotenv()

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
BUCKET_NAME = 'fujito-mis'  
FILE_NAME = 'DPR 17.08.xlsx'      


# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title='Fujito Report Analysis', page_icon='📊', layout='wide')

# Page title
st.title('Report Analytics')

with st.expander('Description of the Report Analysis App'):
    st.markdown('**What can this app do?**')
    st.info('This app allows you to perform a data analysis on the PDR Report.')
    
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
with st.sidebar:
    st.title('Upload Data')
    
    # Button to download file from S3
    if st.button("Fetch File from S3"):
        st.info("Downloading the file from S3...")

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

# Main content
if st.session_state["uploaded_file"]:
    uploaded_file = st.session_state['uploaded_file']  # Use session state to get the uploaded file

    with st.status("Analyzing report...", expanded=True) as status:
        if isinstance(uploaded_file, bytes):
            file_buffer = io.BytesIO(uploaded_file)
        else:
            file_buffer = uploaded_file
        # Skip rows if necessary and use the appropriate row as the header
        df = pd.read_excel(file_buffer, sheet_name="Main", skiprows=1)
        
        # Drop the first column (if it's unwanted)
        df = df.drop(df.columns[0], axis=1)
        
        st.write("**Preview of the Data**")
        st.write(df.head(5))
    
    st.subheader('Overdue Analysis')

    # New section to show top customers with the most Overdue PDCs
    if 'No. of Overdue PDCs' in df.columns and 'Customer Name' in df.columns and 'PDC Max Age' in df.columns:
        with st.expander("Top Customers with Overdue PDCs "):
            overdue_pdc = df[df['No. of Overdue PDCs'] > 0][['Customer Name', 'No. of Overdue PDCs', 'PDC Max Age']].sort_values(by='No. of Overdue PDCs', ascending=False)
            st.dataframe(overdue_pdc, use_container_width=True)

    # Check if "Active/Non-Active" column exists
    if "Active/ Non-Active" in df.columns:

        # Count the number of active and non-active accounts
        active_count = df[df["Active/ Non-Active"] == "Active"].shape[0]
        non_active_count = df[df["Active/ Non-Active"] == "Non-Active"].shape[0]
        
        # Show success message with the active count
        st.success(f"Number of Active Accounts: {active_count}")
        st.warning(f"Number of Non-active Accounts: {non_active_count}")
        
        # Create a pie chart showing the ratio of Active to Non-Active accounts
        pie_data = pd.DataFrame({
            'Account Status': ['Active', 'Non-Active'],
            'Count': [active_count, non_active_count]
        })
        
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Account Status", type="nominal", legend=alt.Legend(title="Account Status")),
            tooltip=["Account Status", "Count"]
        ).properties(
            width=400,
            height=400,
            title="Ratio of Active vs Non-Active Accounts"
        )
        
        st.subheader("Customer Account Status")  # Added subheader
        st.altair_chart(pie_chart, use_container_width=True)

        active_customers = df[df["Active/ Non-Active"] == "Active"][['Customer Name']]
        non_active_customers = df[df["Active/ Non-Active"] == "Non-Active"][['Customer Name']]

        # Create a single expander for both active and non-active customers
        with st.expander("Customer Accounts Overview of Active/Non-Active Accounts", expanded=True):
            # Create two columns for side-by-side display
            col1, col2 = st.columns([3, 3])

            # Center the content in the columns
            with col1:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.write("**Customers with Active Accounts:**")
                st.dataframe(active_customers, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.write("**Customers with Non-Active Accounts:**")
                st.dataframe(non_active_customers, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # Check if 'Latest Status' column exists
    if 'Latest Status' in df.columns:
        # Count the occurrences of each status
        green_count = df[df['Latest Status'] == 'Green'].shape[0]
        inactive_count = df[df['Latest Status'] == 'Inactive'].shape[0]
        red_count = df[df['Latest Status'] == 'Red'].shape[0]
        yellow_count = df[df['Latest Status'] == 'Yellow'].shape[0]

      
        # Create a DataFrame for the counts of customers by latest status
        status_counts_df = pd.DataFrame({
            'Status': ['Green', 'Inactive', 'Red', 'Yellow'],
            'Count': [green_count, inactive_count, red_count, yellow_count]
        })

        st.markdown(f"**Green Status:** {green_count}")
        st.markdown(f"**Inactive Status:** {inactive_count}")
        st.markdown(f"**Red Status:** {red_count}")
        st.markdown(f"**Yellow Status:** {yellow_count}")

        def highlight_status(row):
            color_map = {
                'Green': 'darkgreen',
                'Inactive': 'darkblue',
                'Red': 'lightcoral',
                'Yellow': 'darkorange'
            }
            return [f'background-color: {color_map[row["Status"]]}' for _ in row]

        # Display the counts in a DataFrame format
        st.write("**Count of Customers by Latest Status:**")
        st.dataframe(status_counts_df.style.apply(highlight_status, axis=1), use_container_width=True, hide_index=True)
        

        # Count the occurrences of each status and get corresponding customer names from column D
        status_counts = df.groupby("Latest Status")['Customer Name'].apply(list).reset_index(name='Customers')
        status_counts['Count'] = status_counts['Customers'].apply(len)

        # Ensure 'Count' is treated as numeric
        status_counts['Count'] = pd.to_numeric(status_counts['Count'], errors='coerce')

        # Create a DataFrame for the bar chart
        status_data = pd.DataFrame({
            'Status': status_counts['Latest Status'],
            'Count': status_counts['Count'],
            'Customers': status_counts['Customers']
        })
        
        # Create a bar chart showing the distribution of Latest Status
        status_bar_chart = alt.Chart(status_data).mark_bar().encode(
            x=alt.X('Status', title='Status'),
            y=alt.Y('Count', title='Count'),
            color=alt.Color(
                'Status:N',
                scale=alt.Scale(
                    domain=['Green', 'Inactive', 'Red', 'Yellow'],
                    range=['lightgreen', 'lightpink', 'lightcoral', 'lightyellow']
                ),
                legend=alt.Legend(title="Status")
            ),
            tooltip=[alt.Tooltip("Status", title="Status"), 
                     alt.Tooltip("Count", title="Count")
                     ]
        ).properties(
            width=400,
            height=400,
            title="Distribution of Latest Status"
        )
        
        st.subheader("Customer Account Status")  # Added subheader
        st.altair_chart(status_bar_chart, use_container_width=True)

        # Show a preview of the Latest Status of customers in an expander
        with st.expander("View the Latest Status of Customers 📊"):
            # Create a select box for statuses
            selected_status = st.selectbox("Select a Status", status_data['Status'].unique())

            status_colors = {
                'Green': 'lightgreen',
                'Inactive': 'lightblue',
                'Red': 'lightcoral',
                'Yellow': 'lightorange'
            }

            if selected_status in status_colors:
                st.markdown(f"<div style='background-color: {status_colors[selected_status]}; padding: 10px; border-radius: 5px; margin-top:10px; margin-bottom: 10px'>"
                 f"<strong>Selected Status: {selected_status}</strong></div>", unsafe_allow_html=True)

            # Filter the customers based on the selected status
            filtered_customers = status_data[status_data['Status'] == selected_status]['Customers'].values[0]

            # Create a search box for customer names
            search_term = st.text_input("Search Customers 🔍", "")

            # Filter customers based on the search term
            if search_term:
                filtered_customers = [customer for customer in filtered_customers if search_term.lower() in customer.lower()]

            # Display the filtered customer names in a text area
            st.write(f"**Customers for {selected_status}:**")
            if filtered_customers:
                st.text_area("Filtered Customers", "\n".join(filtered_customers), height=300)
            else:
                st.write("No customers found.")
    
    # New section to calculate and display average balances
    if 'Balance (Latest)' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Average Balance of Customers ⚖️"):
            st.subheader("Average Balance of Customers")
            average_balance = df.groupby('Customer Name')['Balance (Latest)'].mean().reset_index()
            average_balance.columns = ['Customer Name', 'Average Balance']
            
            # Display the average balance data using st.dataframe for full width
            st.dataframe(average_balance, use_container_width=True)
    
    

    st.subheader('Collection Efficiency')

    # New section to show remaining balance to collect
    if 'Remaining Balance to Collect' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Customers with the Most Remaining Balance (Top 10)"):
            remaining_balance = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect']].sort_values(by='Remaining Balance to Collect', ascending=False).head(10)
            st.dataframe(remaining_balance, use_container_width=True)

    # New section to show reasons for overdue balances
    if 'Reason' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Reasons for Overdue Balances"):
            # Create the overdue reasons DataFrame and sort it by 'Remaining Balance to Collect' in descending order
            overdue_reasons = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect', 'Reason', 'To change to green']]
            overdue_reasons = overdue_reasons.sort_values(by='Remaining Balance to Collect', ascending=False)  # Sort in descending order
            
            st.dataframe(overdue_reasons, use_container_width=True)

    else:
        st.error("The 'Latest Status' column was not found in the 'Main' sheet.")

    status.update(label="Analysis complete", state="complete", expanded=False)
else:
    st.warning('👈 Upload the DPR File for Analysis.')
