# Smart Document Field & Value Extractor

A powerful Streamlit application that extracts structured field-value pairs from semi-structured text documents (PDF/TXT) containing multiple profiles. The app intelligently parses documents where field names are in ALL CAPS and values follow until the next field.

## 🚀 Features

- **Multi-format Support**: Process PDF, TXT, CSV, and Excel files
- **Intelligent Field Extraction**: Automatically detects and extracts profile data from semi-structured text
- **Multiple Profile Detection**: Handles documents with multiple profiles by detecting repeated patterns
- **Advanced Filtering**: Filter profiles by:
  - Date of Birth range
  - Income range (LPA)
  - Location (address/place of birth)
  - Education level
  - Job/Occupation
- **Multiple Export Formats**: Download results as JSON, CSV, or Excel
- **Debug Mode**: Detailed extraction information for troubleshooting
- **Profile Visualization**: Clean, expandable profile cards for easy viewing
- **Real-time Demo**: Built-in demo with sample data for testing

## 📋 Expected Input Format

The app works best with text where:
- Field names are in **ALL CAPS** (e.g., DOB, NAME, EDUCATION)
- Values follow immediately after field names
- Multiple profiles are separated by repeated field patterns (like DOB)

**Example:**
```
DOB 08-02-1979 GOTHRAM Kousikasa TOB 03.20 AM POB HYD STAR Arudra
NAME Dharanidhar SURNAME Eleswarapu HT& COMPLEX 5.10 Fair
EDUCATION B Sc JOB Software Engineer INCOME 04.80 LPA
ADDRESS Block No 6, F-51, TSIIC Colony KAPRA HYD 62
FATHER E V Sastry OCCUPATION Engineer CONTACT 9959242663
```

## 🛠 Installation & Setup

### Quick Start (Recommended)

**For Unix/Linux/macOS:**
```bash
# Clone and setup in one go
git clone git@github.com:udayganeshK/pdf-parser.git
cd pdf-parser/field-parser
./setup.sh
./run.sh
```

**For Windows:**
```cmd
# Clone and setup in one go
git clone git@github.com:udayganeshK/pdf-parser.git
cd pdf-parser/field-parser
setup.bat
run.bat
```

### Manual Setup

#### Prerequisites
- Python 3.7 or higher
- pip package manager

#### 1. Clone the Repository
```bash
git clone git@github.com:udayganeshK/pdf-parser.git
cd pdf-parser/field-parser
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📦 Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **pdfplumber**: PDF text extraction
- **openpyxl**: Excel file handling (optional, falls back to CSV if unavailable)

## 🎯 Usage Guide

### 1. Upload Document
- Click "Browse files" to upload a PDF, TXT, CSV, or Excel file
- The app will automatically detect the file type and process accordingly

### 2. Configure Filters (Optional)
Use the sidebar to set up filters:
- **Date of Birth**: Filter by age range
- **Income**: Set minimum/maximum income in LPA
- **Location**: Search for specific cities/locations
- **Education**: Filter by education level
- **Job**: Search for specific occupations

### 3. View Results
- Extracted profiles are displayed as JSON
- Profile cards provide a clean, organized view
- Filter results show how many profiles match your criteria

### 4. Download Results
Choose from three download formats:
- **JSON**: Complete data with metadata
- **CSV**: Spreadsheet-compatible format
- **Excel**: Multi-sheet workbook with summary

### 5. Debug Mode
Enable debug mode in the sidebar to see:
- Token analysis
- Field detection details
- Processing statistics

## 🔧 Advanced Features

### Filtering Examples
Try these filter combinations with the demo:

**Date Filters:**
- 1979-1980: Shows older profiles
- 1985-1990: Shows younger profiles

**Income Filters:**
- Min 10 LPA: High-income profiles only
- Max 5 LPA: Entry-level income profiles

**Location Filters:**
- "HYD": Hyderabad-based profiles
- "Mumbai": Mumbai-based profiles

### Supported Field Types
The app recognizes these field patterns:
- DOB (Date of Birth)
- NAME/SURNAME
- EDUCATION/JOB/INCOME
- ADDRESS/CONTACT
- FATHER/MOTHER details
- GOTHRAM/STAR (traditional fields)
- And more...

## 🧪 Testing

Use the built-in demo feature:
1. Click "Run Demo with Sample Text"
2. Apply different filters to see how they work
3. Download sample results to test export functionality

## 🛠 Development

### Project Structure
```
field-parser/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
├── setup.sh           # Unix/Linux/macOS setup script
├── run.sh             # Unix/Linux/macOS run script
├── setup.bat          # Windows setup script
├── run.bat            # Windows run script
└── .venv/             # Virtual environment (created after setup)
```

### Key Functions
- `extract_fields_from_text()`: Core extraction logic using token-based parsing
- `filter_profiles()`: Apply user-defined filters to extracted profiles
- `create_download_data()`: Generate export files in multiple formats
- `add_download_buttons()`: Streamlit download interface components
- `parse_date()` / `parse_income()`: Data type conversion utilities

## 🚀 Live Demo

Visit the deployed application: [Coming Soon]

Or run locally with the quick start scripts above!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Troubleshooting

### Common Issues

**"No structured fields detected"**
- Ensure field names are in ALL CAPS
- Check that values follow immediately after field names
- Try the debug mode to see what the app is detecting

**Excel download not working**
- Install openpyxl: `pip install openpyxl`
- The app will fall back to CSV if Excel isn't available

**Poor extraction quality**
- Enable debug mode to see token analysis
- Check for special characters or formatting issues
- Ensure consistent field naming patterns

### Performance Tips
- For large PDFs, the extraction may take a few seconds
- Use filters to reduce processing time on large datasets
- Debug mode provides insights into processing bottlenecks

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using Streamlit and Python**
