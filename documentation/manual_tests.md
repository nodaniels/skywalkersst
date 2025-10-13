## Test Cases for User Stories
### User Story 1: Paste and Submit SST Data
1. **Test Case 1:** Paste valid CSV data
   - **Steps:**
     1. Navigate to the sidebar
     2. Paste valid CSV data into the text area
     3. Click "Submit"
   - **Expected Result:** Data is successfully parsed and comment fields appear for each entry

2. **Test Case 2:** Submit data with invalid format
   - **Steps:**
     1. Paste incorrectly formatted data into the text area
     2. Click "Submit"
   - **Expected Result:** Application displays appropriate error message

3. **Test Case 3:** Submit duplicate data
   - **Steps:**
     1. Paste CSV data that already exists in the database
     2. Click "Submit"
   - **Expected Result:** Warning message about duplicate data is displayed

### User Story 2: Manual Data Entry
1. **Test Case 4:** Enter valid single data point
   - **Steps:**
     1. Fill in all fields with valid data:
        - Date: Current date
        - Response: "271773"
        - Mass error: "-3.5"
        - Peptide: "Semaglutide"
        - Sampleset: "20250303_LLS_SST_peptid"
        - Instrument: "Luke"
     2. Click "Submit"
   - **Expected Result:** Data is successfully added to database

2. **Test Case 5:** Enter invalid Response format
   - **Steps:**
     1. Enter Response with comma instead of decimal point (e.g., "271,773")
     2. Click "Submit"
   - **Expected Result:** Error message about invalid number format

3. **Test Case 6:** Enter invalid Sampleset format
   - **Steps:**
     1. Enter Sampleset without correct date prefix
     2. Click "Submit"
   - **Expected Result:** Error message about incorrect Sampleset format

### User Story 3: View Data Table
1. **Test Case 7:** View data table with existing entries
   - **Steps:**
     1. Click "View Data Table" expander
   - **Expected Result:** 
     - Table displays with all columns in correct order
     - Data is sorted by date (newest first)
     - ID column is visible as first column

2. **Test Case 8:** View empty data table
   - **Steps:**
     1. Clear database
     2. Click "View Data Table" expander
   - **Expected Result:** Message indicating no data available

### User Story 4: Delete Data
1. **Test Case 9:** Delete existing entry
   - **Steps:**
     1. Open "Delete Data" expander
     2. Enter valid ID number
     3. Click "Request Deletion"
     4. Enter initials
     5. Click "Confirm Deletion"
   - **Expected Result:** Success message and entry removed from database

2. **Test Case 10:** Attempt deletion without initials
   - **Steps:**
     1. Open "Delete Data" expander
     2. Enter valid ID number
     3. Click "Request Deletion"
     4. Leave initials empty
     5. Click "Confirm Deletion"
   - **Expected Result:** Error message requesting initials

### User Story 5: Data Visualization
1. **Test Case 11:** View mass error plots
   - **Steps:**
     1. Add test data for both instruments
     2. Check mass error plots
   - **Expected Result:**
     - Separate plots for Luke and Leia
     - Red reference lines at +5 and -5 ppm
     - Latest point highlighted in red

2. **Test Case 12:** View response plots
   - **Steps:**
     1. Add test data for different peptides
     2. Check response plots
   - **Expected Result:**
     - Separate plots for each instrument
     - Different colors for each peptide
     - Correct separation of NN8640 data

3. **Test Case 13:** Interactive plot features
   - **Steps:**
     1. Hover over data points
     2. Zoom in on plots
     3. Pan across time range
   - **Expected Result:**
     - Data values shown on hover
     - Zoom and pan functions work
     - Plot layout maintains integrity