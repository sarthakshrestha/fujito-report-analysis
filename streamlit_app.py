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
with open( "./styles.css" ) as css:
            st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# Page title
st.title('Report Analytics')

with st.expander('Description of the Report Analysis App', expanded=True):
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
with st.sidebar:
    st.title('Upload Data')
    
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
        
        # Drop the first column (if it's unwanted)
        df = df.drop(df.columns[0], axis=1)
        
        st.write("**Preview of the Data**")
        st.write(df.head(5))
    
    st.subheader('Overdue Analysis')

    # Top customers with most Overdue PDCs
    if 'No. of Overdue PDCs' in df.columns and 'Customer Name' in df.columns and 'PDC Max Age' in df.columns:
        with st.expander("Top Customers with Overdue PDCs ", expanded=True):
            overdue_pdc = df[df['No. of Overdue PDCs'] > 0][['Customer Name', 'No. of Overdue PDCs', 'PDC Max Age']].sort_values(by='No. of Overdue PDCs', ascending=False)
            st.dataframe(overdue_pdc, use_container_width=True)

    if 'PDC Max Age' in df.columns and 'Customer Name' in df.columns:
        with st.expander("PDC Analysis", expanded=True):
            st.subheader("Post-Dated Cheque (PDC) Analysis")
            
            # PDC Max Age Analysis
            pdc_age = df[['Customer Name', 'PDC Max Age']].sort_values(by='PDC Max Age', ascending=False)
            
            chart = alt.Chart(pdc_age).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('PDC Max Age:Q', axis=alt.Axis(title='PDC Max Age (Days)')),
                color=alt.Color('PDC Max Age:Q', scale=alt.Scale(scheme='reds')),
                tooltip=['Customer Name', 'PDC Max Age']
            ).properties(
                title='PDC Max Age by Customer',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(pdc_age, use_container_width=True)
    if 'Overdue PDC' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Overdue PDC Analysis", expanded=True):
            st.subheader("Overdue Post-Dated Cheque Analysis")
            
            overdue_pdc = df[['Customer Name', 'Overdue PDC']].sort_values(by='Overdue PDC', ascending=False)
            overdue_pdc = overdue_pdc[overdue_pdc['Overdue PDC'] > 0]
            
            chart = alt.Chart(overdue_pdc).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Overdue PDC:Q', axis=alt.Axis(title='Overdue PDC Amount')),
                color=alt.Color('Overdue PDC:Q', scale=alt.Scale(scheme='oranges')),
                tooltip=['Customer Name', 'Overdue PDC']
            ).properties(
                title='Overdue PDC Amount by Customer',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(overdue_pdc, use_container_width=True)
    
    if 'LBP' in df.columns and 'LBS' in df.columns and 'Customer Name' in df.columns:
        with st.expander("LBP and LBS Analysis", expanded=True):
            st.subheader("LBP (Last Bill Paid) and LBS (Last Bill Sent) Analysis")
            
            lbp_lbs = df[['Customer Name', 'LBP', 'LBS']].sort_values(by='LBS', ascending=False)
            
            # Calculate the difference between LBS and LBP
            lbp_lbs['Days Since Last Payment'] = lbp_lbs['LBS'] - lbp_lbs['LBP']
            
            chart = alt.Chart(lbp_lbs).mark_bar().encode(
                x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Days Since Last Payment:Q', axis=alt.Axis(title='Days')),
                color=alt.Color('Days Since Last Payment:Q', scale=alt.Scale(scheme='viridis')),
                tooltip=['Customer Name', 'LBP', 'LBS', 'Days Since Last Payment']
            ).properties(
                title='Days Since Last Payment by Customer',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(lbp_lbs, use_container_width=True)
    
   




    # Active/Non-Active Analysis
    if "Active/ Non-Active" in df.columns:
        active_count = df[df["Active/ Non-Active"] == "Active"].shape[0]
        non_active_count = df[df["Active/ Non-Active"] == "Non-Active"].shape[0]
        
        st.success(f"Number of Active Accounts: {active_count}")
        st.warning(f"Number of Non-active Accounts: {non_active_count}")
        
        pie_data = pd.DataFrame({
            'Account Status': ['Active', 'Non-Active'],
            'Count': [active_count, non_active_count]
        })
        
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Account Status", type="nominal", scale=alt.Scale(domain=["Active", "Non-Active"], range=['#2ecc71', '#e74c3c']), legend=alt.Legend(title="Account Status")),
            tooltip=["Account Status", "Count"]
        ).properties(
            width=400,
            height=400,
            title="Ratio of Active vs Non-Active Accounts"
        )
        
        st.subheader("Customer Account Status")
        st.altair_chart(pie_chart, use_container_width=True)

        active_customers = df[df["Active/ Non-Active"] == "Active"][['Customer Name']]
        non_active_customers = df[df["Active/ Non-Active"] == "Non-Active"][['Customer Name']]

        with st.expander("Customer Accounts Overview of Active/Non-Active Accounts", expanded=True):
            col1, col2 = st.columns([3, 3])

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

    # Latest Status Analysis
    if 'Latest Status' in df.columns:
        green_count = df[df['Latest Status'] == 'Green'].shape[0]
        inactive_count = df[df['Latest Status'] == 'Inactive'].shape[0]
        red_count = df[df['Latest Status'] == 'Red'].shape[0]
        yellow_count = df[df['Latest Status'] == 'Yellow'].shape[0]

        status_counts_df = pd.DataFrame({
            'Status': ['Green', 'Inactive', 'Red', 'Yellow'],
            'Count': [green_count, inactive_count, red_count, yellow_count]
        })

        st.divider()

        st.subheader("**Status of Customers:**")


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

        # st.dataframe(status_counts_df.style.apply(highlight_status, axis=1), use_container_width=True, hide_index=True)

        status_counts = df.groupby("Latest Status")['Customer Name'].apply(list).reset_index(name='Customers')
        status_counts['Count'] = status_counts['Customers'].apply(len)
        status_counts['Count'] = pd.to_numeric(status_counts['Count'], errors='coerce')

        status_data = pd.DataFrame({
            'Status': status_counts['Latest Status'],
            'Count': status_counts['Count'],
            'Customers': status_counts['Customers']
        })
        
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
                     alt.Tooltip("Count", title="Count")]
        ).properties(
            width=400,
            height=400,
            title="Distribution of Latest Status"
        )
        
        st.subheader("Customer Account Status")
        st.altair_chart(status_bar_chart, use_container_width=True)

        st.divider()
        st.subheader("Balance Analysis")

        if 'Balance Cash' in df.columns and 'PDC' in df.columns and 'Customer Name' in df.columns:
            with st.expander("Balance Cash and PDC Analysis", expanded=True):
                st.subheader("Balance Cash and PDC Analysis")
                
                balance_pdc = df[['Customer Name', 'Balance Cash', 'PDC']].sort_values(by='Balance Cash', ascending=False)
                
                # Melt the dataframe to create a long format for stacked bar chart
                balance_pdc_melted = pd.melt(balance_pdc, id_vars=['Customer Name'], var_name='Type', value_name='Amount')
                
                chart = alt.Chart(balance_pdc_melted).mark_bar().encode(
                    x=alt.X('Customer Name:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('Amount:Q', stack='zero'),
                    color=alt.Color('Type:N', scale=alt.Scale(domain=['Balance Cash', 'PDC'], range=['#1f77b4', '#ff7f0e'])),
                    tooltip=['Customer Name', 'Type', 'Amount']
                ).properties(
                    title='Balance Cash and PDC by Customer',
                    width=600,
                    height=400
                )
                
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(balance_pdc, use_container_width=True)

        with st.expander("View the Latest Status of Customers 📊", expanded=True):
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

            filtered_customers = status_data[status_data['Status'] == selected_status]['Customers'].values[0]
            search_term = st.text_input("Search Customers 🔍", "")

            if search_term:
                filtered_customers = [customer for customer in filtered_customers if search_term.lower() in customer.lower()]

            st.write(f"**Customers for {selected_status}:**")
            if filtered_customers:
                st.text_area("Filtered Customers", "\n".join(filtered_customers), height=300)
            else:
                st.write("No customers found.")

    # Enhanced Average Balance Analysis
    if 'Balance (Latest)' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Average Balance of Customers ", expanded=True):
            st.subheader("Average Balance of Customers")
            
            # Calculate average balance and sort by balance amount
            average_balance = df.groupby('Customer Name')['Balance (Latest)'].mean().reset_index()
            average_balance.columns = ['Customer Name', 'Average Balance']
            average_balance = average_balance.sort_values(by='Average Balance', ascending=True)

            # Create two columns for the visualizations
          
            
          

            bar_chart = alt.Chart(average_balance).mark_bar().encode(
                x=alt.X('Customer Name', sort=None, title='Customer'),
                y=alt.Y('Average Balance', title='Average Balance'),
                color=alt.condition(
                    alt.datum['Average Balance'] > 10000,  # Example threshold
                    alt.value('green'),  # Color for balances above threshold
                    alt.value('red')     # Color for balances below threshold
                ),
                tooltip=[
                    alt.Tooltip('Customer Name', title='Customer'),
                    alt.Tooltip('Average Balance', title='Balance', format=',.2f')
                ]
            ).properties(
                height=400,
                title='Customer Average Balances Distribution'
            )

            st.altair_chart(bar_chart, use_container_width=True)


            line_chart = alt.Chart(average_balance).mark_line(
                point=alt.OverlayMarkDef(color="red", size=100)
            ).encode(
                x=alt.X('Customer Name', sort=None, title='Customer'),
                y=alt.Y('Average Balance', title='Average Balance'),
                tooltip=[
                    alt.Tooltip('Customer Name', title='Customer'),
                    alt.Tooltip('Average Balance', title='Balance', format=',.2f')
                ]
            ).properties(
                height=400,
                title='Customer Average Balances Distribution'
            ).configure_axis(
                labelAngle=-45
            )
            st.altair_chart(line_chart, use_container_width=True)

            st.markdown("**Detailed Balance Data**")
            st.dataframe(
                average_balance.style.format({'Average Balance': '{:,.2f}'}),
                use_container_width=True,
                height=400
            )

            
                # Add statistics
            st.markdown("**Summary Statistics:**")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                highest_balance = average_balance['Average Balance'].max()
                st.caption("Highest Average Balance")
                st.markdown(f"Rs. {highest_balance:,.2f}")
            with col_stats2:
                mean_balance = average_balance['Average Balance'].mean()
                st.caption(" Average Balance")
                st.markdown(f"Rs. {mean_balance:,.2f}")

            with col_stats3:
                lowest_balance = average_balance['Average Balance'].min()
                st.caption("Lowest Balance")
                st.markdown(f"Rs. {lowest_balance:,.2f}")
            
            
            
            # Add top and bottom 5 customers
            col_top, col_bottom = st.columns(2)
            
            with col_top:
                st.markdown("**Top 5 Customers by Balance**")
                top_5 = average_balance.nlargest(5, 'Average Balance')
                st.dataframe(
                    top_5.style.format({'Average Balance': '{:,.2f}'}),
                    use_container_width=True
                )
            
            with col_bottom:
                st.markdown("**Bottom 5 Customers by Balance**")
                bottom_5 = average_balance.nsmallest(5, 'Average Balance')
                st.dataframe(
                    bottom_5.style.format({'Average Balance': '{:,.2f}'}),
                    use_container_width=True
                )
            col_new = st.columns(1)

    st.divider()
    st.subheader('Collection Efficiency')

    # Remaining Balance Analysis
    if 'Remaining Balance to Collect' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Customers with the Most Remaining Balance (Top 10)", expanded=True):
            remaining_balance = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect']].sort_values(by='Remaining Balance to Collect', ascending=False).head(10)
            chart = alt.Chart(remaining_balance).mark_bar().encode(
            x=alt.X('Customer Name:N', 
                    sort='-y',
                    axis=alt.Axis(title='Customer Name', labelAngle=-45)),
            y=alt.Y('Remaining Balance to Collect:Q',
                    axis=alt.Axis(title='Remaining Balance (Rs.)')),
            color=alt.Color('Remaining Balance to Collect:Q',
                        scale=alt.Scale(scheme='blues'),
                        legend=alt.Legend(title='Balance (Rs.)')),
            tooltip=[
                alt.Tooltip('Customer Name:N', title='Customer'),
                alt.Tooltip('Remaining Balance to Collect:Q', 
                        title='Remaining Balance (In Rupees)',
                        format=',.2f')
            ]
        ).properties(
            title='Top 10 Customers by Remaining Balance',
            width=600,
            height=400
        )

        # Add text labels on top of bars
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5
        ).encode(
            text=alt.Text('Remaining Balance to Collect:Q', format=',.0f')
        )

        final_chart = (chart + text).interactive()
        st.altair_chart(final_chart, use_container_width=True)
        st.dataframe(remaining_balance, use_container_width=True)

            


    # Overdue Reasons Analysis
    if 'Reason' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Reasons for Overdue Balances", expanded=True):
            overdue_reasons = df[df['Remaining Balance to Collect'] > 0][['Customer Name', 'Remaining Balance to Collect', 'Reason', 'To change to green']]
            overdue_reasons = overdue_reasons.sort_values(by='Remaining Balance to Collect', ascending=False)
            st.dataframe(overdue_reasons, use_container_width=True)
    
    if 'Visit Date' in df.columns and 'Customer Name' in df.columns:
        with st.expander("Customers with Visit Days", expanded=True):
            # Convert 'Visit Date' to datetime
            df['Visit Date'] = pd.to_datetime(df['Visit Date'], errors='coerce')
            
            # Create a custom sorting order for days of the week
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Sort the dataframe by the Visit Date
            due_this_week = df[['Customer Name', 'Visit Date']].dropna(subset=['Visit Date'])
            due_this_week = due_this_week.sort_values('Visit Date')
            
            # Display the dataframe
            st.dataframe(due_this_week, use_container_width=True)
            
            # Create a bar chart to visualize the distribution of visit days
            visit_day_counts = due_this_week['Visit Date'].dt.day_name().value_counts().reindex(day_order).reset_index()
            visit_day_counts.columns = ['Day', 'Count']
            
            chart = alt.Chart(visit_day_counts).mark_bar().encode(
                x=alt.X('Day:N', sort=day_order),
                y='Count:Q',
                color=alt.Color('Day:N', scale=alt.Scale(scheme='category10')),
                tooltip=['Day', 'Count']
            ).properties(
                title='Distribution of Customer Visit Days',
                width=600,
                height=400
            )
            
            st.altair_chart(chart, use_container_width=True)


       

    status.update(label="Analysis complete", state="complete", expanded=False)
else:
    st.warning('👈 Upload the DPR File for Analysis.')