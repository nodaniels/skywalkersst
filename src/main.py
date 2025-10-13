import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import src.configs as configs

# Authentication
try:
    configs.oauth_client.get_token_silent_or_interactive_redirect(configs.oauth_scopes.NETAPI)
except KeyError as e:
    st.query_params.clear()
    st.rerun()

user = configs.oauth_client.get_username()

import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from io import StringIO
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

st.set_page_config(
    page_title="SST Data and Visualization",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# Database connection parameters
conn_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Streamlit app
col_title = st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<span style='font-size:3.7em; font-weight:bold;'>Skywalker SST</span>"
        "</div>",
        unsafe_allow_html=True
    )

def insert_data_to_postgres(data):
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Check for duplicates
        check_query = """
        SELECT COUNT(*) FROM "Data"
        WHERE "Date" = %s 
        AND "Response"::text = %s 
        AND "Masserrorppm"::text = %s 
        AND "Peptide" = %s 
        AND "Samplename" = %s 
        AND "Instrument" = %s 
        AND "Kommentar" = %s
        """
        cursor.execute(check_query, (
            data["Date"], 
            str(data["Response"]),
            str(data["Masserrorppm"]), 
            data["Peptide"], 
            data["Samplename"], 
            data["Instrument"], 
            data["Kommentar"]
        ))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert data if no duplicates found
            insert_query = """
            INSERT INTO "Data" ("Date", "Response", "Masserrorppm", "Peptide", "Samplename", "Instrument", "Kommentar")
            VALUES (%s, %s::numeric, %s::numeric, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data["Date"], 
                str(data["Response"]),
                str(data["Masserrorppm"]), 
                data["Peptide"], 
                data["Samplename"], 
                data["Instrument"], 
                data["Kommentar"]
            ))
            conn.commit()
            st.sidebar.success("Data submitted successfully!")
        else:
            st.sidebar.warning("Duplicate data found. Data not inserted.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        st.sidebar.error(f"An error occurred: {e}")

# Sidebar for data input

# CSV Data Input Section
st.sidebar.title("Paste CSV Data")

# Add help text
with st.sidebar.expander("ℹ️ CSV Format Help", expanded=False):
    st.write("**Supported CSV formats:**")
    st.write("1. **Original Unifi format:**")
    st.code("""Item Name CC,Description CC,Component name,Response,Mass error (ppm)
SST_sample_001,Insulin icodec,Insulin icodec,691565,1.3""")
    st.write("2. **New Intact Mass format (with Type/Molecule ID):**")
    st.code("""Type,Molecule ID,Component,Response,Mass error (ppm)
Product,Apomyoglobin,Apomyoglobin,691565,1.3""")
    st.write("3. **New Component format:**")
    st.code("""Component,Mass error,MS response,Item description
Apomyoglobin,1.3,691565,Luke-20240101-sst""")
    st.write("**Important:**")
    st.write("• Use decimal points, not commas (1.3 not 1,3)")  
    st.write("• Make sure all required fields are filled")
    st.write("• For Component format: Instrument name detected from 'Item description'")
    st.write("• For other formats: Include instrument name (Luke/Leia) in filename")


data_input = []
# Add file upload option
uploaded_file = st.sidebar.file_uploader("Upload CSV file (instrument name will be extracted from filename)", type=['csv'], key="csv_file_upload")

# Initialize session states for CSV handling
if 'comments' not in st.session_state:
    st.session_state.comments = []
if 'show_comments' not in st.session_state:
    st.session_state.show_comments = False
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'detected_instrument' not in st.session_state:
    st.session_state.detected_instrument = None

# Handle uploaded file or pasted data
if uploaded_file is not None:
    # Extract instrument name from filename
    filename = uploaded_file.name
    if "Leia" in filename or "leia" in filename.lower():
        st.session_state.detected_instrument = "Leia"
        st.sidebar.success(f"🎯 Detected instrument: **Leia** from filename")
    elif "Luke" in filename or "luke" in filename.lower():
        st.session_state.detected_instrument = "Luke" 
        st.sidebar.success(f"🎯 Detected instrument: **Luke** from filename")
    else:
        st.session_state.detected_instrument = None
        st.sidebar.info(f"No instrument detected in filename. Please select manually below.")
    
    # Read the uploaded file
    data_input = uploaded_file.getvalue().decode('utf-8')
    st.sidebar.info(f"📁 **File uploaded:** {filename}")

# Add instrument selection for CSV data
if st.session_state.detected_instrument:
    csv_instrument = st.session_state.detected_instrument
    st.sidebar.info(f"🔧 **Using detected instrument:** {csv_instrument}")
else:
    csv_instrument = st.sidebar.selectbox("Select Instrument for CSV data", ["Luke", "Leia"], key="csv_instrument")

# Add peptide selection for new format (when peptide info is missing)
if 'current_df' in st.session_state and st.session_state.current_df is not None:
    # Check if this is the new format by looking at the peptide values
    sample_peptides = st.session_state.current_df['peptide'].unique()
    if len(sample_peptides) > 0 and all(peptide == sample_peptides[0] for peptide in sample_peptides):
        # All peptide values are the same (likely Molecule ID), so we need user to select
        if sample_peptides[0] not in ['Insulin icodec', 'Semaglutide', 'Somapacitan']:
            # For new format, the peptide IS the Molecule ID (e.g., "Apomyoglobin")
            # (Alert removed - peptide detected silently)
            pass

# Advanced CSV validation and parsing
if data_input or uploaded_file is not None:
    def validate_csv_format(data_input):
        """
        Comprehensive CSV validation with detailed error reporting and field mapping
        Enhanced for new Intact Mass format with Molecule ID handling
        """
        errors = []
        warnings = []
        
        try:
            # First, try to detect the structure without forcing column names
            data = StringIO(data_input)
            df_raw = pd.read_csv(data)
            
            # Check for different CSV formats
            if 'Component' in df_raw.columns and 'Mass error' in df_raw.columns and 'MS response' in df_raw.columns and 'Item description' in df_raw.columns:
                # New Component format detected
                df_valid = df_raw[df_raw['Component'].notna() & (df_raw['Component'] != "")].copy()
                
                if len(df_valid) == 0:
                    errors.append("No rows with valid Component found in the data")
                    return None, errors, warnings
                
                # Map the new Component format columns to our expected format
                try:
                    # Create standardized DataFrame for Component format
                    standardized_data = {
                        'sample_id': df_valid['Component'].astype(str) + "_" + datetime.now().strftime("%Y%m%d"),
                        'peptide': df_valid['Component'].astype(str),    # Use Component as peptide name
                        'component': df_valid['Component'].astype(str),  # Same as peptide for this format
                        'response': df_valid['MS response'],
                        'mass_error': df_valid['Mass error'],
                        'item_description': df_valid['Item description']  # For instrument detection
                    }
                    
                    df_standardized = pd.DataFrame(standardized_data)
                    
                except KeyError as e:
                    errors.append(f"Missing expected column in Component format: {str(e)}")
                    return None, errors, warnings
                    
            elif 'Type' in df_raw.columns and 'Molecule ID' in df_raw.columns:
                # New Intact Mass format detected - filter for rows with valid Molecule ID
                # (processing continues without warning message)
                
                # Filter to only rows with non-empty Molecule ID (instead of just Product rows)
                df_valid = df_raw[df_raw['Molecule ID'].notna() & (df_raw['Molecule ID'] != "")].copy()
                
                if len(df_valid) == 0:
                    errors.append("No rows with valid Molecule ID found in the data")
                    return None, errors, warnings
                
                # Show detected molecules (no warning message)
                unique_molecules = df_valid['Molecule ID'].unique()
                
                # Map the new format columns to our expected format
                try:
                    # Create standardized DataFrame for new format
                    # Use Molecule ID as peptide name (e.g., "Apomyoglobin")
                    standardized_data = {
                        'sample_id': df_valid['Molecule ID'].astype(str) + "_" + datetime.now().strftime("%Y%m%d"),
                        'peptide': df_valid['Molecule ID'].astype(str),    # Use Molecule ID as peptide name
                        'component': df_valid['Component'].astype(str),    # Use Component column if available
                        'response': df_valid['Response'],
                        'mass_error': df_valid['Mass error (ppm)']
                    }
                    
                    df_standardized = pd.DataFrame(standardized_data)
                    # Processing complete (no warning messages)
                    
                except KeyError as e:
                    errors.append(f"Missing expected column in new format: {str(e)}")
                    return None, errors, warnings
                    
            else:
                # Original format handling
                # Expected column patterns (multiple variations supported)
                expected_patterns = {
                    'sample_id': ['Item Name CC', 'item name cc', 'sample id', 'sampleid', 'sample name', 'item_name_cc'],
                    'peptide': ['Description CC', 'description cc', 'peptide', 'component name', 'compound', 'description_cc'],
                    'component': ['Component name', 'component name', 'component_name', 'component'],
                    'response': ['Response', 'response', 'intensity', 'peak area', 'area'],
                    'mass_error': ['Mass error (ppm)', 'mass error', 'mass_error_ppm', 'mass error ppm', 'ppm', 'mass_error']
                }
                
                # Analyze the actual columns in the data
                actual_columns = [col.strip().lower() for col in df_raw.columns]
                column_mapping = {}
                missing_fields = []
                
                st.sidebar.info(f"🔍 **Detected {len(actual_columns)} columns:** {', '.join(df_raw.columns)}")
                
                # Try to map each expected field to actual columns
                for field_type, patterns in expected_patterns.items():
                    mapped = False
                    for pattern in patterns:
                        if pattern.lower() in actual_columns:
                            original_col = df_raw.columns[actual_columns.index(pattern.lower())]
                            column_mapping[field_type] = original_col
                            mapped = True
                            break
                    
                    if not mapped:
                        missing_fields.append(field_type)
                
                # If we have missing fields, show what's missing and provide manual mapping
                if missing_fields:
                    st.sidebar.error(f"❌ **Missing required fields:** {', '.join(missing_fields)}")
                    
                    # Allow user to manually map columns
                    st.sidebar.write("**Manual Column Mapping:**")
                    manual_mapping = {}
                    
                    for missing_field in missing_fields:
                        field_name = missing_field.replace('_', ' ').title()
                        if missing_field == 'sample_id':
                            field_name = "Sample ID/Name"
                        elif missing_field == 'mass_error':
                            field_name = "Mass Error (ppm)"
                        
                        options = ["-- Select Column --"] + list(df_raw.columns)
                        selected = st.sidebar.selectbox(
                            f"Map '{field_name}' to:", 
                            options, 
                            key=f"map_{missing_field}"
                        )
                        if selected != "-- Select Column --":
                            manual_mapping[missing_field] = selected
                    
                    # Update column mapping with manual selections
                    column_mapping.update(manual_mapping)
                    
                    # Check if all fields are now mapped
                    still_missing = [field for field in missing_fields if field not in manual_mapping]
                    if still_missing:
                        st.sidebar.warning(f"⚠️ Still missing: {', '.join(still_missing)}")
                        return None, errors, warnings
                
                # Create standardized DataFrame with mapped columns
                try:
                    standardized_data = {}
                    required_fields = ['sample_id', 'peptide', 'response', 'mass_error']
                    
                    for field in required_fields:
                        if field in column_mapping:
                            standardized_data[field] = df_raw[column_mapping[field]]
                        else:
                            errors.append(f"Required field '{field}' is not mapped")
                            return None, errors, warnings
                    
                    # Add component field if available, otherwise use peptide
                    if 'component' in column_mapping:
                        standardized_data['component'] = df_raw[column_mapping['component']]
                    else:
                        standardized_data['component'] = standardized_data['peptide']
                        warnings.append("Component column not found, using Peptide column instead")
                    
                    df_standardized = pd.DataFrame(standardized_data)
                    
                except Exception as e:
                    errors.append(f"Error creating standardized data: {str(e)}")
                    return None, errors, warnings
                
            # Validate data content for both formats
            validation_errors = []
            for index, row in df_standardized.iterrows():
                row_errors = []
                
                # Check for empty required fields
                if pd.isna(row['sample_id']) or str(row['sample_id']).strip() == "":
                    row_errors.append("Missing Sample ID")
                
                if pd.isna(row['peptide']) or str(row['peptide']).strip() == "":
                    row_errors.append("Missing Peptide name")
                
                # Validate numeric fields
                try:
                    response_val = float(str(row['response']).replace(',', '.'))
                    if ',' in str(row['response']) and '.' in str(row['response']):
                        row_errors.append("Response has both comma and decimal point")
                except (ValueError, TypeError):
                    row_errors.append(f"Invalid Response value: '{row['response']}'")
                
                try:
                    mass_error_val = float(str(row['mass_error']).replace(',', '.'))
                    if ',' in str(row['mass_error']) and '.' in str(row['mass_error']):
                        row_errors.append("Mass error has both comma and decimal point")
                except (ValueError, TypeError):
                    row_errors.append(f"Invalid Mass error value: '{row['mass_error']}'")
                
                if row_errors:
                    validation_errors.append(f"Row {index+1}: {'; '.join(row_errors)}")
            
            if validation_errors:
                errors.extend(validation_errors)
                return None, errors, warnings
            
            return df_standardized, errors, warnings
                
        except Exception as e:
            errors.append(f"Error parsing CSV: {str(e)}")
            return None, errors, warnings
    
    # Validate the CSV data
    validated_df, validation_errors, validation_warnings = validate_csv_format(data_input)
    
    if validation_errors:
        st.sidebar.error("❌ **Validation Errors:**")
        for error in validation_errors:
            st.sidebar.write(f"• {error}")
        st.session_state.current_df = None
    else:
        st.session_state.current_df = validated_df
        st.sidebar.success(f"✅ Successfully validated {len(validated_df)} rows of data")
        
        # Show preview of the data - show all rows that will be inserted
        with st.sidebar.expander(f"📋 Data Preview ({len(validated_df)} rows to insert)", expanded=False):
            if len(validated_df) <= 20:
                # Show all rows if 20 or fewer
                st.dataframe(validated_df, use_container_width=True)
            else:
                # For larger datasets, show first 10 and last 5 with summary
                st.write(f"**First 10 rows:**")
                st.dataframe(validated_df.head(10), use_container_width=True)
                st.write(f"**... {len(validated_df) - 15} more rows ...**")
                st.write(f"**Last 5 rows:**")
                st.dataframe(validated_df.tail(5), use_container_width=True)

# Show Submit CSV button only if comments are not already shown
if not st.session_state.show_comments and st.sidebar.button("Submit CSV", key="submit_csv"):
    if data_input or uploaded_file is not None:
        st.session_state.show_comments = True
        st.sidebar.info("Add comments for each data point below (optional):")
    else:
        st.sidebar.error("Please paste data or upload a file.")

# Show comment fields if show_comments is True
if st.session_state.show_comments and st.session_state.current_df is not None:
    # Show comment fields for each row
    for index, row in st.session_state.current_df.iterrows():
        st.sidebar.text_area(
            f"Add a comment for {row['peptide']}", 
            height=68, 
            key=f"comment_{index}"
        )
    
    if st.sidebar.button("Final submit", key="submit_csv_comments"):
        successful_inserts = 0
        failed_inserts = 0
        error_details = []
        
        # Process each row in the DataFrame (using standardized column names)
        for index, row in st.session_state.current_df.iterrows():
            try:
                # Validate Response - auto-convert comma to decimal point and round to integer
                try:
                    response_raw = float(str(row["response"]).replace(',', '.'))
                    response_value = round(response_raw)  # Round to nearest integer (no decimals)
                except (ValueError, TypeError):
                    error_details.append(f"Row {index+1}: Invalid Response value '{row['response']}' - must be numeric")
                    failed_inserts += 1
                    continue
                
                # Validate Mass error - auto-convert comma to decimal point
                try:
                    mass_error = float(str(row["mass_error"]).replace(',', '.'))
                except (ValueError, TypeError):
                    error_details.append(f"Row {index+1}: Invalid Mass error value '{row['mass_error']}' - must be numeric")
                    failed_inserts += 1
                    continue
                
                # Final check for missing required fields (should not happen after validation)
                if pd.isna(row["sample_id"]) or str(row["sample_id"]).strip() == "":
                    error_details.append(f"Row {index+1}: Missing Sample ID")
                    failed_inserts += 1
                    continue
                    
                if pd.isna(row["peptide"]) or str(row["peptide"]).strip() == "":
                    error_details.append(f"Row {index+1}: Missing Peptide name")
                    failed_inserts += 1
                    continue
                
                # Get comment from the text_area widget using its key
                comment_key = f"comment_{index}"
                comment = st.session_state.get(comment_key, "") if comment_key in st.session_state else ""
                
                # Debug: Show what comment was found (remove this later)
                if comment:
                    st.write(f"Debug - Found comment for {row['peptide']}: '{comment}'")
                
                # Determine instrument: use Item description if available, otherwise use selected instrument
                if 'item_description' in row and pd.notna(row['item_description']):
                    item_desc = str(row['item_description']).lower()
                    if 'leia' in item_desc:
                        instrument = "Leia"
                    elif 'luke' in item_desc:
                        instrument = "Luke"
                    else:
                        instrument = csv_instrument  # Fallback to selected instrument
                else:
                    instrument = csv_instrument
                
                data = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Response": response_value,  # Now rounded integer without decimals
                    "Masserrorppm": mass_error,
                    "Peptide": row["peptide"],
                    "Samplename": row["sample_id"],
                    "Instrument": instrument,
                    "Kommentar": comment
                }
                
                # Insert data into PostgreSQL
                insert_data_to_postgres(data)
                successful_inserts += 1
                
            except Exception as e:
                error_details.append(f"Row {index+1}: Unexpected error - {str(e)}")
                failed_inserts += 1
                continue
        
        # Show summary of results
        if successful_inserts > 0:
            st.sidebar.success(f"✅ Successfully inserted {successful_inserts} rows using instrument: **{csv_instrument}**")
        
        if failed_inserts > 0:
            st.sidebar.error(f"❌ Failed to insert {failed_inserts} rows")
            
            # Show detailed errors in an expander
            with st.sidebar.expander("View Error Details", expanded=True):
                for error in error_details:
                    st.sidebar.write(f"• {error}")
                
                st.sidebar.info("💡 **Suggestion**: If you have data validation errors, try entering the data manually using the form below instead of CSV paste.")
                
            # Show manual entry suggestion
            st.sidebar.markdown("---")
            st.sidebar.info("🔧 **Alternative**: Use the manual data entry form below to add individual data points.")
        
        # Reset states after processing (success or failure)
        if successful_inserts > 0 or failed_inserts > 0:
            st.session_state.show_comments = False
            st.session_state.current_df = None
            st.session_state.comments = []            


st.sidebar.markdown("---")  # Add a separator

st.sidebar.title("Enter SST Data")

date = st.sidebar.date_input("Date")
response = st.sidebar.text_input("Response")
mass_error = st.sidebar.text_input("Mass error (ppm)")
peptide = st.sidebar.selectbox("Peptide", ["Apomyoglobin", "Digest1", "Digest2", "Digest3"])
samplename = st.sidebar.text_input("Samplename")
instrument = st.sidebar.selectbox("Instrument", ["Luke", "Leia"])
kommentar = st.sidebar.text_input("Kommentar")

def is_valid_number(value):
    try:
        # Prøv at konvertere til float
        float(value)
        # Tjek om der er komma i værdien
        if ',' in value:
            return False
        return True
    except ValueError:
        return False

def is_valid_samplename(value):
    # Check if the field is not empty
    return bool(value.strip())

def is_valid_mass_error(value):
    try:
        # Try to convert to float
        float(value)
        # Check if it contains a comma
        if ',' in value:
            return False
        return True
    except ValueError:
        return False

# Når du opretter data-ordbogen, skal du automatisk tilføje den aktuelle dato og tid
if st.sidebar.button("Submit"):
    error_messages = []

    if not is_valid_number(response):
        error_messages.append("Response should be a number with a decimal point (.), not a comma (,).")
    
    if not is_valid_number(mass_error):
        error_messages.append("Mass error should be a number with a decimal point (.), not a comma (,).")
    
    if not is_valid_samplename(samplename):
        error_messages.append("Remember to fill out Samplename")

    if error_messages:
        for message in error_messages:
            st.sidebar.error(message)
    else:
        try:
            # Create a dictionary from the input data
            data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Automatically set current date and time
                "Response": response,
                "Masserrorppm": mass_error,
                "Peptide": peptide,
                "Samplename": samplename,
                "Instrument": instrument,
                "Kommentar": kommentar
            }
            
            # Insert data into PostgreSQL
            insert_data_to_postgres(data)
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")

# Add this right after the first submit button section


# Fetch and display data from the PostgreSQL database
def fetch_data():
    try:
        conn = psycopg2.connect(**conn_params)
        query = 'SELECT * FROM "Data"'
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Clean the Peptide column by stripping whitespace
        if 'Peptide' in df.columns:
            df['Peptide'] = df['Peptide'].str.strip()
        
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

df = fetch_data()

# Add time period filter controls
st.subheader("Data Visualization Settings")

col1, col2 = st.columns([2, 3])

with col1:
    time_period = st.selectbox(
        "🗓️ Select time period for graphs:",
        options=["Data range", "All", "12 months", "6 months", "3 months", "1 month"],
        index=0,
        help="Choose how far back in time to display data in the graphs. 'Data range' shows from first data entry."
    )

with col2:
    # Add some vertical space to align with selectbox
    st.write("")  # Empty line for vertical alignment
    
    # Information about time periods
    period_info = {
        "Data range": "Shows from first data entry onwards - focuses on actual data period",
        "All": "Shows all available data from 2024 onwards",
        "12 months": "Shows data from the last 12 months",
        "6 months": "Shows data from the last 6 months", 
        "3 months": "Shows data from the last 3 months",
        "1 month": "Shows data from the last month"
    }
    st.info(f"ℹ️ {period_info[time_period]}")

st.markdown("---")  # Separator line

def get_date_filter(period):
    """Get the date cutoff based on selected time period"""
    today = datetime.now()
    
    if period == "All":
        return pd.Timestamp('2024-01-01')  # Show from 2024 onwards
    elif period == "12 months":
        return pd.Timestamp(today - timedelta(days=365))
    elif period == "6 months":
        return pd.Timestamp(today - timedelta(days=183))
    elif period == "3 months":
        return pd.Timestamp(today - timedelta(days=92))
    elif period == "1 month":
        return pd.Timestamp(today - timedelta(days=31))
    else:
        return pd.Timestamp('2024-01-01')

# Filter data to include only rows from selected time period
if df is not None:
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is in datetime format
    
    # Apply time period filter
    if time_period == "Data range":
        # For "Data range", use all available data from first entry
        df = df[df['Date'] >= df['Date'].min()]
    else:
        date_cutoff = get_date_filter(time_period)
        df = df[df['Date'] >= date_cutoff]
    
    if len(df) == 0:
        st.warning(f"No data available for the selected time period ({time_period}). Showing all available data.")
        df = fetch_data()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'] >= pd.Timestamp('2024-01-01')]

    # Sort data by date
    df = df.sort_values('Date')
    
    # Data is ready for visualization - no alert needed

    # Opret separate dataframes for Luke og Leia
    df_luke = df[df['Instrument'] == 'Luke']
    df_leia = df[df['Instrument'] == 'Leia']

    def plot_masserrorppm(df, title):
        fig = go.Figure()
        
        # Plot alle punkter undtagen det sidste
        fig.add_trace(go.Scatter(
            x=df['Date'][:-1], 
            y=df['Masserrorppm'][:-1], 
            mode='markers', 
            name='Previous Data', 
            marker=dict(color='blue'),
            hovertemplate='<b>Previous Data</b><br>' +
                          'Date: %{x}<br>' +
                          'Mass error (ppm): %{y:.2f}<br>' +
                          '<extra></extra>'
        ))
        
        # Plot det sidste punkt i rødt
        last_point = df.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_point['Date']], 
            y=[last_point['Masserrorppm']], 
            mode='markers', 
            name='Latest Data Point', 
            marker=dict(color='red', size=10),
            hovertemplate='<b>Latest Data Point</b><br>' +
                          'Date: %{x}<br>' +
                          'Mass error (ppm): %{y:.2f}<br>' +
                          '<extra></extra>'
        ))
        
        # Formatering af akser
        fig.update_layout(
            title=title, 
            xaxis_title='Date', 
            yaxis_title='Masserrorppm',
            xaxis=dict(
                tickformat='%Y-%m-%d',  # Kun dato
                type='date'
            )
        )
        return fig

    def plot_mass_error_combined(df, title, time_period="All"):
        """Kombineret Mass Error plot for alle peptider på ét instrument"""
        fig = go.Figure()
        
        # Definer farver for hver peptid
        colors = {
            'Apomyoglobin': 'rgb(31, 119, 180)',  # Blå
            'Digest1': 'rgb(255, 127, 14)',     # Orange
            'Digest2': 'rgb(44, 160, 44)',      # Grøn
            'Digest3': 'rgb(214, 39, 40)'       # Rød
        }
        
        # Samle alle datoer fra faktisk plottede data (kun for "Data range")
        all_plotted_dates = [] if time_period == "Data range" else None
        
        # Tilføj alle peptider til samme plot
        for peptide in ['Apomyoglobin', 'Digest1', 'Digest2', 'Digest3']:
            # Søg efter både versioner - med og uden underscore, og trim whitespace
            df_peptide = df[(df['Peptide'].str.strip() == peptide) | 
                            (df['Peptide'].str.strip() == f"{peptide}_")]
            if len(df_peptide) > 0:  # Kun tilføj hvis der er data
                # Tilføj datoerne fra dette peptid til listen (kun for "Data range")
                if time_period == "Data range":
                    all_plotted_dates.extend(df_peptide['Date'].tolist())
                
                fig.add_trace(go.Scatter(
                    x=df_peptide['Date'], 
                    y=df_peptide['Masserrorppm'], 
                    mode='lines+markers', 
                    name=peptide,
                    line=dict(color=colors[peptide]),
                    marker=dict(color=colors[peptide]),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Date: %{x}<br>' +
                                  'Mass error (ppm): %{y:.2f}<br>' +
                                  '<extra></extra>'  # Fjerner default hover box
                ))
        
        # Tilføj røde linjer ved ±10 ppm
        if time_period == "Data range" and all_plotted_dates:
            # For "Data range" brug plottet data range
            min_plotted_date = min(all_plotted_dates)
            max_plotted_date = max(all_plotted_dates)
            fig.add_shape(type="line", 
                         x0=min_plotted_date, x1=max_plotted_date, 
                         y0=10, y1=10, 
                         line=dict(color="red", width=2, dash="dash"),
                         name="+10 ppm limit")
            fig.add_shape(type="line", 
                         x0=min_plotted_date, x1=max_plotted_date, 
                         y0=-10, y1=-10, 
                         line=dict(color="red", width=2, dash="dash"),
                         name="-10 ppm limit")
        elif len(df) > 0:
            # For andre tidsperioder brug hele dataset range (som før)
            fig.add_shape(type="line", 
                         x0=df['Date'].min(), x1=df['Date'].max(), 
                         y0=10, y1=10, 
                         line=dict(color="red", width=2, dash="dash"),
                         name="+10 ppm limit")
            fig.add_shape(type="line", 
                         x0=df['Date'].min(), x1=df['Date'].max(), 
                         y0=-10, y1=-10, 
                         line=dict(color="red", width=2, dash="dash"),
                         name="-10 ppm limit")
        
        # Formatering af akser
        xaxis_config = {
            'tickformat': '%Y-%m-%d',  # Kun dato
            'type': 'date'
        }
        
        # Kun for "Data range" sæt x-aksen til faktisk plottede data
        if time_period == "Data range" and all_plotted_dates:
            min_plotted_date = min(all_plotted_dates)
            max_plotted_date = max(all_plotted_dates)
            xaxis_config['range'] = [min_plotted_date, max_plotted_date]
        # For alle andre tidsperioder: normal auto-range (som før)
        
        fig.update_layout(
            title=title, 
            xaxis_title='Date', 
            yaxis_title='Mass Error (ppm)',
            xaxis=xaxis_config,
            yaxis=dict(
                tickformat='.2f'
            ),
            height=400
        )
        return fig

    def plot_single_peptide(df, peptide_name, title):
        """Plot for en enkelt peptid - håndterer både versioner med og uden underscore"""
        fig = go.Figure()
        
        colors = {
            'Apomyoglobin': 'rgb(31, 119, 180)',  # Blå
            'Digest1': 'rgb(255, 127, 14)',     # Orange
            'Digest2': 'rgb(44, 160, 44)'            # Grøn
        }
        
        # Søg efter både versioner - med og uden underscore, og trim whitespace
        df_peptide = df[(df['Peptide'].str.strip() == peptide_name) | 
                        (df['Peptide'].str.strip() == f"{peptide_name}_")]
        
        if len(df_peptide) > 0:
            fig.add_trace(go.Scatter(
                x=df_peptide['Date'], 
                y=df_peptide['Response'], 
                mode='lines+markers', 
                name=peptide_name,
                line=dict(color=colors.get(peptide_name, 'rgb(128, 128, 128)')),
                marker=dict(color=colors.get(peptide_name, 'rgb(128, 128, 128)')),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x}<br>' +
                              'Response: %{y:,.0f}<br>' +
                              '<extra></extra>'  # Fjerner default hover box
            ))
        
        # Formatering af akser
        fig.update_layout(
            title=title, 
            xaxis_title='Date', 
            yaxis_title='Response',
            xaxis=dict(
                tickformat='%Y-%m-%d',  # Kun dato
                type='date'
            ),
            yaxis=dict(
                tickformat='.2s',  # Smart formatering
                separatethousands=True
            )
        )
        return fig

    def plot_response(df, title, time_period="All"):
        fig = go.Figure()
        
        # Definer farver for hver peptid
        colors = {
            'Apomyoglobin': 'rgb(31, 119, 180)',  # Blå
            'Digest1': 'rgb(255, 127, 14)',     # Orange
            'Digest2': 'rgb(44, 160, 44)',      # Grøn
            'Digest3': 'rgb(214, 39, 40)'       # Rød
        }
        
        # Samle alle datoer fra faktisk plottede data (kun for "Data range")
        all_plotted_dates = [] if time_period == "Data range" else None
        
        # Tilføj alle peptider til samme plot
        for peptide in ['Apomyoglobin', 'Digest1', 'Digest2', 'Digest3']:
            # Søg efter både versioner - med og uden underscore, og trim whitespace
            df_peptide = df[(df['Peptide'].str.strip() == peptide) | 
                            (df['Peptide'].str.strip() == f"{peptide}_")]
            if len(df_peptide) > 0:  # Kun tilføj hvis der er data
                # Tilføj datoerne fra dette peptid til listen (kun for "Data range")
                if time_period == "Data range":
                    all_plotted_dates.extend(df_peptide['Date'].tolist())
                
                fig.add_trace(go.Scatter(
                    x=df_peptide['Date'], 
                    y=df_peptide['Response'], 
                    mode='lines+markers', 
                    name=peptide,
                    line=dict(color=colors[peptide]),
                    marker=dict(color=colors[peptide]),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Date: %{x}<br>' +
                                  'Response: %{y:,.0f}<br>' +
                                  '<extra></extra>'  # Fjerner default hover box
                ))
        
        # Formatering af akser
        xaxis_config = {
            'tickformat': '%Y-%m-%d',  # Kun dato, ikke tidspunkt
            'type': 'date'
        }
        
        # Kun for "Data range" sæt x-aksen til faktisk plottede data
        if time_period == "Data range" and all_plotted_dates:
            min_plotted_date = min(all_plotted_dates)
            max_plotted_date = max(all_plotted_dates)
            xaxis_config['range'] = [min_plotted_date, max_plotted_date]
        # For alle andre tidsperioder: normal auto-range (som før)
        
        fig.update_layout(
            title=title, 
            xaxis_title='Date', 
            yaxis_title='Response',
            xaxis=xaxis_config,
            yaxis=dict(
                tickformat='.2s',  # Maksimalt 2 decimaler, smart formatering
                separatethousands=True  # Tusindtalsseparatorer
            )
        )
        return fig

    # Opret Mass Error plots
    st.subheader("Mass Error Analysis")
    
    # Create two columns for Luke and Leia Mass Error plots side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # Luke Mass Error plot - alle komponenter kombineret
        luke_mass_error_fig = plot_mass_error_combined(df_luke, "Luke - Mass Error", time_period)
        st.plotly_chart(luke_mass_error_fig, use_container_width=True)
    
    with col2:
        # Leia Mass Error plot - alle komponenter kombineret
        leia_mass_error_fig = plot_mass_error_combined(df_leia, "Leia - Mass Error", time_period)
        st.plotly_chart(leia_mass_error_fig, use_container_width=True)
    
    # Opret separate MS Response plots
    st.subheader("MS Response Analysis")
    
    # Create two columns for Luke and Leia MS Response plots side by side
    col3, col4 = st.columns(2)
    
    with col3:
        # Luke MS Response plot
        luke_response_fig = plot_response(df_luke, "Luke - MS Response", time_period)
        st.plotly_chart(luke_response_fig, use_container_width=True)
    
    with col4:
        # Leia MS Response plot  
        leia_response_fig = plot_response(df_leia, "Leia - MS Response", time_period)
        st.plotly_chart(leia_response_fig, use_container_width=True)

else:
    st.write("No data available.")

with st.expander("View Data Table", expanded=False):
    if df is not None:
        # Sort the dataframe by date, newest first
        df_sorted = df.sort_values('Date', ascending=False)
        
        # Convert 'Date' column to datetime if it's not already
        df_sorted['Date'] = pd.to_datetime(df_sorted['Date'])
        
        # Format the date as 'YYYY-MM-DD'
        df_sorted['Date'] = df_sorted['Date'].dt.strftime('%Y-%m-%d')
        
        # Reorder columns to include ID first
        columns_order = ['ID', 'Date', 'Instrument', 'Response', 'Masserrorppm', 'Peptide', 'Samplename', 'Kommentar']
        df_sorted = df_sorted[columns_order]
        
        # Display the dataframe without index
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
    else:
        st.write("No data available to display.")
        
def delete_data_by_id(id_number):
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Slet direkte baseret på ID
        delete_query = """
        DELETE FROM "Data"
        WHERE "ID" = %s
        """
        cursor.execute(delete_query, (id_number,))
        affected_rows = cursor.rowcount
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return affected_rows
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return 0

with st.expander("Delete Data", expanded=False):
    st.warning("Caution: This action will permanently delete data.")
    id_to_delete = st.number_input("Enter the ID number of the row to delete:", min_value=1, step=1)
    
    if st.button("Request Deletion"):
        if id_to_delete:
            st.session_state.show_confirmation = True
            st.session_state.id_to_delete = id_to_delete
        else:
            st.error("Please enter an ID number to delete.")

    if 'show_confirmation' in st.session_state and st.session_state.show_confirmation:
        st.warning(f"Are you sure you want to delete row with ID {id_to_delete}?")
        user_initials = st.text_input("Enter your initials to confirm:")
        
        if st.button("Confirm Deletion"):
            if user_initials:
                affected_rows = delete_data_by_id(st.session_state.id_to_delete)
                if affected_rows > 0:
                    st.success(f"Row with ID {st.session_state.id_to_delete} deleted successfully by {user_initials}.")
                else:
                    st.info("No matching data found to delete.")
                st.session_state.show_confirmation = False
            else:
                st.error("Please enter your initials to confirm the deletion.")