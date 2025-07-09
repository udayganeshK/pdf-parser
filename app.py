import streamlit as st
import pandas as pd
import pdfplumber
import io
import re
import json
from datetime import datetime, date

def extract_fields_from_text(text, debug=False):
    """Extract field-value pairs from semi-structured text"""
    
    # List of known fields to look for
    known_fields = ['DOB', 'GOTHRAM', 'TOB', 'POB', 'STAR', 'NAME', 'SURNAME', 
                   'HT&', 'COMPLEX', 'EDUCATION', 'JOB', 'INCOME', 'ADDRESS',
                   'FATHER', 'OCCUPATION', 'CONTACT', 'MOTHER', 
                   'SIBLINGS', 'SUBSECT', 'REQUIREMENTS']
    
    # Map field names to standardized JSON keys
    field_map = {
        'dob': 'date_of_birth',
        'gothram': 'gothram',
        'tob': 'time_of_birth',
        'pob': 'place_of_birth', 
        'star': 'star',
        'name': 'name',
        'surname': 'surname',
        'ht&': 'height',
        'complex': 'complexion',
        'education': 'education',
        'job': 'job',
        'income': 'income',
        'address': 'address',
        'father': 'father_name',
        'occupation': 'occupation',
        'contact': 'contact',
        'mother': 'mother_name',
        'siblings': 'siblings',
        'subsect': 'subsect',
        'requirements': 'requirements'
    }
    
    # Skip these tokens as they are artifacts
    skip_tokens = ['LATE', 'NO', 'BAR']
    
    def extract_profile_from_words(words):
        """Extract profile data from a list of words"""
        result = {}
        i = 0
        
        while i < len(words):
            word = words[i]
            
            if word in known_fields:
                field_name = word.lower()
                values = []
                i += 1
                
                # Collect values until next field or end
                while i < len(words) and words[i] not in known_fields:
                    token = words[i]
                    # Skip single digits and artifacts
                    if not (token.isdigit() and len(token) == 1) and token not in skip_tokens:
                        values.append(token)
                    i += 1
                
                if values:
                    value = ' '.join(values).strip()
                    clean_field = field_map.get(field_name, field_name)
                    result[clean_field] = value
            else:
                i += 1
        
        return result
    
    # Clean text and split into tokens
    cleaned_text = text.replace('\n', ' ').replace('  ', ' ')
    words = cleaned_text.split()
    
    debug_info = {}
    if debug:
        debug_info = {
            "total_words": len(words),
            "first_20_words": words[:20],
            "found_fields": [w for w in words if w in known_fields]
        }
    
    # Check for multiple profiles by counting DOB occurrences
    dob_count = text.count('DOB ')
    
    if dob_count > 1:
        # Multiple profiles detected
        sections = text.split('DOB ')
        profiles = []
        
        for idx, section in enumerate(sections[1:], 1):  # Skip first empty section
            section_text = 'DOB ' + section
            section_words = section_text.replace('\n', ' ').split()
            profile = extract_profile_from_words(section_words)
            
            if profile:
                profile['profile_id'] = f"profile_{idx}"
                profiles.append(profile)
        
        result = {"profiles": profiles}
        if debug:
            result["debug"] = debug_info
            result["debug"]["sections_found"] = len(sections) - 1
        
        return result
    else:
        # Single profile
        profile = extract_profile_from_words(words)
        
        if profile:
            result = {"profile": profile}
            if debug:
                result["debug"] = debug_info
            return result
        else:
            if debug:
                return {"error": "No profile data found", "debug": debug_info}
            return {"error": "No profile data found"}

def parse_date(date_str):
    """Parse date string in DD-MM-YYYY format"""
    try:
        return datetime.strptime(date_str, '%d-%m-%Y').date()
    except:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except:
            return None

def parse_income(income_str):
    """Extract numeric income value from income string"""
    if not income_str:
        return 0
    
    # Remove common suffixes and convert to number
    income_clean = income_str.upper().replace('LPA', '').replace('PER MONTH', '').replace('K', '000').strip()
    
    # Extract numbers
    numbers = re.findall(r'[\d.]+', income_clean)
    if numbers:
        try:
            value = float(numbers[0])
            # If it contains 'LPA', it's already in lakhs
            if 'LPA' in income_str.upper():
                return value
            # If it contains 'per month', convert to annual (lakhs)
            elif 'PER MONTH' in income_str.upper():
                return (value * 12) / 100000  # Convert to lakhs per annum
            else:
                return value
        except:
            return 0
    return 0

def filter_profiles(profiles, filters):
    """Apply filters to profiles list"""
    filtered = []
    
    for profile in profiles:
        # DOB filter
        if filters.get('dob_range'):
            dob_str = profile.get('date_of_birth', '')
            if dob_str:
                profile_date = parse_date(dob_str)
                if profile_date:
                    if filters['dob_range'][0] and profile_date < filters['dob_range'][0]:
                        continue
                    if filters['dob_range'][1] and profile_date > filters['dob_range'][1]:
                        continue
        
        # Income filter
        if filters.get('income_range'):
            income_str = profile.get('income', '')
            if income_str:
                income_value = parse_income(income_str)
                if filters['income_range'][0] and income_value < filters['income_range'][0]:
                    continue
                if filters['income_range'][1] and income_value > filters['income_range'][1]:
                    continue
        
        # Location filter
        if filters.get('location'):
            address = profile.get('address', '').lower()
            pob = profile.get('place_of_birth', '').lower()
            location_filter = filters['location'].lower()
            if location_filter and location_filter not in address and location_filter not in pob:
                continue
        
        # Education filter
        if filters.get('education'):
            education = profile.get('education', '').lower()
            education_filter = filters['education'].lower()
            if education_filter and education_filter not in education:
                continue
        
        # Job filter
        if filters.get('job'):
            job = profile.get('job', '').lower()
            job_filter = filters['job'].lower()
            if job_filter and job_filter not in job:
                continue
        
        filtered.append(profile)
    
    return filtered

def convert_profiles_to_csv(profiles):
    """Convert profiles list to CSV format"""
    if not profiles:
        return None
    
    # Flatten the profiles data
    flattened_data = []
    for profile in profiles:
        row = {}
        for key, value in profile.items():
            row[key] = value
        flattened_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_data)
    return df

def create_download_data(profiles, format_type="json"):
    """Create downloadable data in specified format"""
    if not profiles:
        return None, None
    
    if format_type == "json":
        data = {"profiles": profiles, "total_count": len(profiles), "extracted_at": datetime.now().isoformat()}
        json_str = json.dumps(data, indent=2, default=str)
        return json_str.encode('utf-8'), "application/json"
    
    elif format_type == "csv":
        df = convert_profiles_to_csv(profiles)
        if df is not None:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue().encode('utf-8'), "text/csv"
    
    elif format_type == "excel":
        try:
            df = convert_profiles_to_csv(profiles)
            if df is not None:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Profiles', index=False)
                    
                    # Add a summary sheet
                    summary_df = pd.DataFrame({
                        'Metric': ['Total Profiles', 'Extracted At', 'Average Age', 'Most Common Location'],
                        'Value': [
                            len(profiles),
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'N/A',  # Could calculate if DOB is available
                            'N/A'   # Could analyze addresses
                        ]
                    })
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                return excel_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        except (ImportError, Exception) as e:
            # openpyxl not available or other error, fall back to CSV
            return create_download_data(profiles, "csv")
    
    return None, None

def add_download_buttons(profiles, prefix=""):
    """Add download buttons for different formats"""
    if not profiles:
        return
    
    st.write("**📥 Download Results:**")
    col1, col2, col3 = st.columns(3)
    
    # JSON Download
    with col1:
        json_data, json_mime = create_download_data(profiles, "json")
        if json_data:
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"{prefix}extracted_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime=json_mime,
                help="Download as JSON format"
            )
    
    # CSV Download
    with col2:
        csv_data, csv_mime = create_download_data(profiles, "csv")
        if csv_data:
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"{prefix}extracted_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime=csv_mime,
                help="Download as CSV format"
            )
    
    # Excel Download
    with col3:
        excel_data, excel_mime = create_download_data(profiles, "excel")
        if excel_data:
            st.download_button(
                label="📈 Download Excel",
                data=excel_data,
                file_name=f"{prefix}extracted_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime=excel_mime,
                help="Download as Excel format with summary"
            )

st.title("Smart Document Field & Value Extractor")
st.write("Upload a document to extract structured field-value pairs from semi-structured text.")

# Sidebar for filters and debug mode
st.sidebar.header("Settings & Filters")

# Add debug mode toggle
debug_mode = st.sidebar.checkbox("Enable debug mode", value=False)

# Filtering controls
st.sidebar.subheader("🔍 Filter Profiles")

# Date of Birth filter
st.sidebar.write("**Date of Birth Range:**")
use_dob_filter = st.sidebar.checkbox("Filter by DOB")
dob_from = None
dob_to = None
if use_dob_filter:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        dob_from = st.date_input("From", value=date(1980, 1, 1), key="dob_from")
    with col2:
        dob_to = st.date_input("To", value=date(2000, 12, 31), key="dob_to")

# Income filter
st.sidebar.write("**Income Range (LPA):**")
use_income_filter = st.sidebar.checkbox("Filter by Income")
income_from = None
income_to = None
if use_income_filter:
    income_from = st.sidebar.number_input("Min Income (LPA)", min_value=0.0, value=0.0, step=0.5)
    income_to = st.sidebar.number_input("Max Income (LPA)", min_value=0.0, value=50.0, step=0.5)

# Location filter
st.sidebar.write("**Location:**")
use_location_filter = st.sidebar.checkbox("Filter by Location")
location_search = None
if use_location_filter:
    location_search = st.sidebar.text_input("Location (Address/Place of Birth)", placeholder="e.g., HYD, Mumbai, Chennai")

# Education filter
st.sidebar.write("**Education:**")
use_education_filter = st.sidebar.checkbox("Filter by Education")
education_search = None
if use_education_filter:
    education_search = st.sidebar.text_input("Education", placeholder="e.g., B.Tech, MBA, M.Sc")

# Job filter
st.sidebar.write("**Job/Occupation:**")
use_job_filter = st.sidebar.checkbox("Filter by Job")
job_search = None
if use_job_filter:
    job_search = st.sidebar.text_input("Job/Occupation", placeholder="e.g., Engineer, Doctor, Teacher")

# Build filters dictionary
filters = {}
if use_dob_filter and dob_from and dob_to:
    filters['dob_range'] = (dob_from, dob_to)
if use_income_filter and (income_from > 0 or income_to > 0):
    filters['income_range'] = (income_from if income_from > 0 else None, income_to if income_to > 0 else None)
if use_location_filter and location_search:
    filters['location'] = location_search.strip()
if use_education_filter and education_search:
    filters['education'] = education_search.strip()
if use_job_filter and job_search:
    filters['job'] = job_search.strip()

uploaded_file = st.file_uploader("Upload a document (PDF, TXT, XLSX, CSV)", type=["pdf", "txt", "xlsx", "csv"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
        st.write("**CSV File Analysis:**")
        st.write("Detected columns:", list(df.columns))
        st.dataframe(df.head())
        
        # Analyze data types and content
        st.write("**Field Analysis:**")
        analysis = {}
        for col in df.columns:
            sample_values = df[col].dropna().head(5).tolist()
            data_type = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            analysis[col] = {
                "data_type": data_type,
                "null_count": null_count,
                "sample_values": sample_values
            }
        st.json(analysis)
        
    elif file_type == "xlsx":
        df = pd.read_excel(uploaded_file)
        st.write("**Excel File Analysis:**")
        st.write("Detected columns:", list(df.columns))
        st.dataframe(df.head())
        
        # Analyze data types and content
        st.write("**Field Analysis:**")
        analysis = {}
        for col in df.columns:
            sample_values = df[col].dropna().head(5).tolist()
            data_type = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            analysis[col] = {
                "data_type": data_type,
                "null_count": null_count,
                "sample_values": sample_values
            }
        st.json(analysis)
        
    elif file_type == "txt":
        content = uploaded_file.read().decode("utf-8")
        st.write("**Text File Content:**")
        
        if debug_mode:
            st.text_area("Raw Content", content, height=200)
        else:
            st.text_area("Raw Content", content[:500] + "..." if len(content) > 500 else content, height=100)
        
        # Extract fields from text
        st.write("**Extracted Profile Data:**")
        extracted_fields = extract_fields_from_text(content, debug=debug_mode)
        
        if extracted_fields and not extracted_fields.get('error'):
            # Get the profiles list
            profiles_to_display = []
            if 'profiles' in extracted_fields:
                profiles_to_display = extracted_fields['profiles']
            elif 'profile' in extracted_fields:
                profiles_to_display = [extracted_fields['profile']]
            
            # Apply filters if any are set
            if filters and profiles_to_display:
                original_count = len(profiles_to_display)
                profiles_to_display = filter_profiles(profiles_to_display, filters)
                filtered_count = len(profiles_to_display)
                
                st.info(f"🔍 Filtered: {filtered_count} profiles (from {original_count} total)")
            
            # Display results
            if profiles_to_display:
                if len(profiles_to_display) == 1:
                    st.json({"profile": profiles_to_display[0]})
                    st.success("✅ Found 1 profile (after filtering)" if filters else "✅ Found 1 profile")
                else:
                    st.json({"profiles": profiles_to_display})
                    st.success(f"✅ Found {len(profiles_to_display)} profiles (after filtering)" if filters else f"✅ Found {len(profiles_to_display)} profiles")
                
                # Add download buttons
                st.write("---")
                add_download_buttons(profiles_to_display, "txt_")
                
                # Show profile cards for better visualization
                st.write("---")
                st.write("**📋 Profile Summary:**")
                for i, profile in enumerate(profiles_to_display, 1):
                    with st.expander(f"Profile {i}: {profile.get('name', 'Unknown')} {profile.get('surname', '')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**DOB:** {profile.get('date_of_birth', 'N/A')}")
                            st.write(f"**Education:** {profile.get('education', 'N/A')}")
                            st.write(f"**Job:** {profile.get('job', 'N/A')}")
                            st.write(f"**Income:** {profile.get('income', 'N/A')}")
                        with col2:
                            st.write(f"**Place of Birth:** {profile.get('place_of_birth', 'N/A')}")
                            st.write(f"**Address:** {profile.get('address', 'N/A')}")
                            st.write(f"**Contact:** {profile.get('contact', 'N/A')}")
                            st.write(f"**Gothram:** {profile.get('gothram', 'N/A')}")
            else:
                if filters:
                    st.warning("⚠️ No profiles match the selected filters. Try adjusting your filter criteria.")
                else:
                    st.warning("⚠️ No profiles found in the extracted data.")
            
            # Show debug info if enabled
            if debug_mode and extracted_fields.get('debug'):
                st.write("**Debug Information:**")
                st.json(extracted_fields['debug'])
                
        else:
            st.warning("⚠️ No structured fields detected in the text.")
            st.info("Expected format: Field names in ALL CAPS followed by their values (e.g., DOB 06-01-1994 NAME John Doe)")
            
            if debug_mode and extracted_fields.get('debug'):
                st.write("**Debug Information:**")
                st.json(extracted_fields['debug'])
            
    elif file_type == "pdf":
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            # Extract all text from PDF
            all_text = ""
            pdf_data = {
                "document_info": {
                    "total_pages": len(pdf.pages),
                    "file_name": uploaded_file.name
                },
                "pages": []
            }
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    
                page_data = {
                    "page_number": i + 1,
                    "content": page_text if page_text else "",
                    "word_count": len(page_text.split()) if page_text else 0
                }
                pdf_data["pages"].append(page_data)
            
            if debug_mode:
                st.write("**PDF Document Structure:**")
                st.json(pdf_data)
            else:
                st.write(f"**PDF Info:** {len(pdf.pages)} pages, {uploaded_file.name}")
            
            # Extract fields from all text
            st.write("**Extracted Profile Data from PDF:**")
            
            if debug_mode:
                st.write("**Debug - PDF Text Content:**")
                st.text_area("Extracted Text", all_text[:1000] + "..." if len(all_text) > 1000 else all_text, height=200)
            
            extracted_fields = extract_fields_from_text(all_text, debug=debug_mode)
            
            if extracted_fields and not extracted_fields.get('error'):
                # Get the profiles list
                profiles_to_display = []
                if 'profiles' in extracted_fields:
                    profiles_to_display = extracted_fields['profiles']
                elif 'profile' in extracted_fields:
                    profiles_to_display = [extracted_fields['profile']]
                
                # Apply filters if any are set
                if filters and profiles_to_display:
                    original_count = len(profiles_to_display)
                    profiles_to_display = filter_profiles(profiles_to_display, filters)
                    filtered_count = len(profiles_to_display)
                    
                    st.info(f"🔍 Filtered: {filtered_count} profiles (from {original_count} total)")
                
                # Display results
                if profiles_to_display:
                    if len(profiles_to_display) == 1:
                        st.json({"profile": profiles_to_display[0]})
                        st.success("✅ Found 1 profile (after filtering)" if filters else "✅ Found 1 profile")
                    else:
                        st.json({"profiles": profiles_to_display})
                        st.success(f"✅ Found {len(profiles_to_display)} profiles (after filtering)" if filters else f"✅ Found {len(profiles_to_display)} profiles")
                    
                # Add download buttons
                st.write("---")
                add_download_buttons(profiles_to_display, "pdf_")
                
                # Show profile cards for better visualization
                st.write("---")
                st.write("**📋 Profile Summary:**")
                for i, profile in enumerate(profiles_to_display, 1):
                    with st.expander(f"Profile {i}: {profile.get('name', 'Unknown')} {profile.get('surname', '')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**DOB:** {profile.get('date_of_birth', 'N/A')}")
                            st.write(f"**Education:** {profile.get('education', 'N/A')}")
                            st.write(f"**Job:** {profile.get('job', 'N/A')}")
                            st.write(f"**Income:** {profile.get('income', 'N/A')}")
                        with col2:
                            st.write(f"**Place of Birth:** {profile.get('place_of_birth', 'N/A')}")
                            st.write(f"**Address:** {profile.get('address', 'N/A')}")
                            st.write(f"**Contact:** {profile.get('contact', 'N/A')}")
                            st.write(f"**Gothram:** {profile.get('gothram', 'N/A')}")
                else:
                    if filters:
                        st.warning("⚠️ No profiles match the selected filters. Try adjusting your filter criteria.")
                    else:
                        st.warning("⚠️ No profiles found in the extracted data.")
                
                # Show debug info if enabled
                if debug_mode and extracted_fields.get('debug'):
                    st.write("**Debug Information:**")
                    st.json(extracted_fields['debug'])
                    
            else:
                st.warning("⚠️ No structured fields detected in the PDF content.")
                st.info("Expected format: Field names in ALL CAPS followed by their values (e.g., DOB 06-01-1994 NAME John Doe)")
                
                if debug_mode and extracted_fields.get('debug'):
                    st.write("**Debug Information:**")
                    st.json(extracted_fields['debug'])

# Add a demo section
st.write("---")
st.write("**🔍 Try the Demo:**")

demo_text = """DOB 08-02-1979 GOTHRAM Kousikasa TOB 03.20 AM POB HYD STAR Arudra 1P
NAME Dharanidhar SURNAME Eleswarapu HT& COMPLEX 5.10 Fair
EDUCATION B Sc JOB BITS Pilani Hyd campus Lab Technician
INCOME 04.80 LPA ADDRESS Block No 6, F-51, TSIIC Colony KAPRA HYD 62
FATHER E V Sastry LATE OCCUPATION CONTACT 9959242663
MOTHER Usha Devi LATE OCCUPATION CONTACT 9885995973
SIBLINGS One brother married SUBSECT V V NO BAR
REQUIREMENTS Minimum education Xth Class

DOB 15-05-1985 GOTHRAM Bharadwaj TOB 02.30 PM POB Mumbai STAR Pushya
NAME Priya SURNAME Sharma HT& COMPLEX 5.4 Fair
EDUCATION M Tech JOB Software Engineer
INCOME 12.50 LPA ADDRESS Flat 203, Green Valley Apartments, Bandra Mumbai
FATHER Rajesh Sharma OCCUPATION Engineer CONTACT 9876543210
MOTHER Sunita Sharma OCCUPATION Teacher CONTACT 9876543211
SIBLINGS Two sisters SUBSECT None NO BAR
REQUIREMENTS MBA preferred"""

col1, col2 = st.columns(2)
with col1:
    if st.button("Run Demo with Sample Text"):
        st.write("**Sample Text (Multiple Profiles):**")
        st.code(demo_text)
        
        st.write("**Demo Extraction Results:**")
        demo_fields = extract_fields_from_text(demo_text, debug=debug_mode)
        
        if demo_fields and not demo_fields.get('error'):
            # Get the profiles list
            demo_profiles = []
            if 'profiles' in demo_fields:
                demo_profiles = demo_fields['profiles']
            elif 'profile' in demo_fields:
                demo_profiles = [demo_fields['profile']]
            
            # Apply filters if any are set
            if filters and demo_profiles:
                original_count = len(demo_profiles)
                demo_profiles = filter_profiles(demo_profiles, filters)
                filtered_count = len(demo_profiles)
                
                st.info(f"🔍 Demo Filtered: {filtered_count} profiles (from {original_count} total)")
            
            # Display results
            if demo_profiles:
                if len(demo_profiles) == 1:
                    st.json({"profile": demo_profiles[0]})
                else:
                    st.json({"profiles": demo_profiles})
                
                # Add download buttons for demo
                st.write("**📥 Download Demo Results:**")
                add_download_buttons(demo_profiles, "demo_")
                
                # Show profile cards
                st.write("**📋 Demo Profile Summary:**")
                for i, profile in enumerate(demo_profiles, 1):
                    with st.expander(f"Demo Profile {i}: {profile.get('name', 'Unknown')} {profile.get('surname', '')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**DOB:** {profile.get('date_of_birth', 'N/A')}")
                            st.write(f"**Education:** {profile.get('education', 'N/A')}")
                            st.write(f"**Job:** {profile.get('job', 'N/A')}")
                            st.write(f"**Income:** {profile.get('income', 'N/A')}")
                        with col_b:
                            st.write(f"**Place of Birth:** {profile.get('place_of_birth', 'N/A')}")
                            st.write(f"**Address:** {profile.get('address', 'N/A')}")
                            st.write(f"**Contact:** {profile.get('contact', 'N/A')}")
                            st.write(f"**Gothram:** {profile.get('gothram', 'N/A')}")
            else:
                if filters:
                    st.warning("⚠️ No demo profiles match the selected filters.")
                else:
                    st.json(demo_fields)
        else:
            st.json(demo_fields)

with col2:
    st.write("**💡 Filter Testing Tips:**")
    st.info("""
    Try these filter combinations with the demo:
    
    **Date Filter:**
    - From: 1979-01-01 to 1980-12-31 (Shows Dharanidhar)
    - From: 1985-01-01 to 1990-12-31 (Shows Priya)
    
    **Income Filter:**
    - Min: 10 LPA (Shows only Priya)
    - Max: 5 LPA (Shows only Dharanidhar)
    
    **Location Filter:**
    - "HYD" (Shows Dharanidhar)
    - "Mumbai" (Shows Priya)
    
    **Education Filter:**
    - "B Sc" (Shows Dharanidhar)
    - "M Tech" (Shows Priya)
    
    **Job Filter:**
    - "Lab Technician" (Shows Dharanidhar)
    - "Software Engineer" (Shows Priya)
    """)

# Add filter information box
if filters:
    st.write("---")
    st.write("**🔧 Active Filters:**")
    filter_info = []
    if 'dob_range' in filters:
        filter_info.append(f"**DOB:** {filters['dob_range'][0]} to {filters['dob_range'][1]}")
    if 'income_range' in filters:
        min_inc = filters['income_range'][0] or "0"
        max_inc = filters['income_range'][1] or "∞"
        filter_info.append(f"**Income:** {min_inc} to {max_inc} LPA")
    if 'location' in filters:
        filter_info.append(f"**Location:** '{filters['location']}'")
    if 'education' in filters:
        filter_info.append(f"**Education:** '{filters['education']}'")
    if 'job' in filters:
        filter_info.append(f"**Job:** '{filters['job']}'")
    
    if filter_info:
        for info in filter_info:
            st.write(info)
    else:
        st.write("No active filters")