# Skywalker SST

Web application for managing LC-MS System Suitability Test (SST) data from UNIFI instruments.

## What It Does

- Submit SST data via CSV upload or manual entry
- Track mass error (ppm) and response values for Luke and Leia instruments
- Visualize trends with interactive charts
- Store and manage data in PostgreSQL database

## Setup

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Create `.env` file** with database credentials:
   ```env
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=5432
   ```

3. **Run the app:**
   ```powershell
   cd C:\Users\NOFR\Desktop\skywalkersst
   ~\AppData\Local\Microsoft\WindowsApps\python3.11.exe -m streamlit run src\main.py
   ```

   The app opens at `http://localhost:8501`

## How to Use

### Submit CSV Data
1. Go to **Skywalker SST** page in sidebar
2. Upload CSV file or paste data
3. Instrument auto-detected from filename (Luke/Leia)
4. Click **Submit CSV** → add comments → **Final Submit**

**Supported formats:** UNIFI export, Intact Mass, Component format

### Manual Entry
1. Expand **"Manual Data Entry"**
2. Fill date, response, mass error, peptide, instrument
3. Click **Submit**

### View & Delete Data
- **View:** Expand "View Stored Data" to see all entries
- **Delete:** Expand "Delete Data by ID", enter ID and initials

### Charts
Auto-generated plots show mass error (±5 ppm reference) and response trends by instrument and peptide.

## Troubleshooting

- **CSV errors:** Use decimal points (`.`) not commas, check required fields
- **Database errors:** Verify `.env` credentials

**Support:** [pwdg@novonordisk.com](mailto:pwdg@novonordisk.com)
