# User Requirement Specification
## Roles
- User
  - Chemist
  - LabTech
- Technical Expert
- IT System Owner
- IT System Manager

## 1: Paste and Submit SST Data
As a User,  
I want to be able to paste CSV data from UNIFI into the application and submit it,  
so that I can store the SST data in a centralized database.

### Acceptance Criteria
- The application should provide a text area in the sidebar for pasting CSV data.
- The pasted data should be correctly parsed with appropriate column names.
- The submit button should trigger data validation before storage.
- The application should handle duplicate entries appropriately.

## 2: Add Comments to Data
As a User,  
I want to add comments to each data point before submission,  
so that I can provide additional context or information about the measurements.

### Acceptance Criteria
- After submitting CSV data, comment fields should appear for each data point.
- Each comment field should be clearly labeled with the corresponding peptide name.
- Comments should be stored in the database along with the measurement data.
- The interface should clearly indicate that comments can be added.

## 3: View Stored Data
As a User,  
I want to view all stored SST data in a table format,  
so that I can review historical measurements and their associated information.

### Acceptance Criteria
- Data should be displayed in an expandable table view.
- Table should show all relevant columns including ID, Date, Instrument, Response, Mass Error, Peptide, Sample Set, and Comments.
- Data should be sorted by date with newest entries first.
- Table should be easily readable with appropriate column widths.

## 4: Delete Data Entries
As a User,  
I want to delete specific data entries using their ID number,  
so that I can remove incorrect or outdated entries from the database.

### Acceptance Criteria
- The application should provide a deletion interface in an expandable section.
- Users must enter their initials to confirm deletion.
- The application should show a confirmation prompt before final deletion.
- Successfully deleted entries should be removed from the database and table view.

## 5: Data Validation and Error Handling
As a User,  
I want the application to validate my input data and provide clear error messages,  
so that I can ensure data integrity and correct any issues.

### Acceptance Criteria
- The application should validate CSV data format and content.
- Clear error messages should be displayed when invalid data is detected.
- Duplicate entries should be identified and reported.
- Mass error values should be validated as numerical values.

## 6: Database Storage
As a Technical Expert,  
I want the data to be stored securely in a PostgreSQL database with appropriate schema,  
so that data persistence and integrity is maintained.

### Acceptance Criteria
- Data should be stored in a properly structured PostgreSQL database.
- Each entry should have a unique ID as primary key.
- The database schema should accommodate all required fields.
- Database connections should be handled securely using environment variables.

## 7: Data Visualization
As a User,  
I want to see visualizations of the SST data across different instruments and peptides,  
so that I can track trends and identify potential issues.

### Acceptance Criteria
- Display separate plots for mass error (ppm) and response values.
- Show different plots for each instrument (Luke and Leia).
- Highlight the most recent data points in the mass error plots.
- Include reference lines at +5 and -5 ppm for mass error plots.
- Display response trends for different peptides in separate colors.
- Organize plots in a clear, multi-panel layout.

## 8: Manual Data Entry
As a User,  
I want to manually enter individual SST data points through a form interface,  
so that I can add single measurements to the database.

### Acceptance Criteria
- Provide input fields for all necessary data points (Date, Response, Mass error, etc.).
- Include dropdown menus for fixed choices (Instrument, Peptide).
- Validate input formats before submission.
- Show clear error messages for invalid inputs.
- Confirm successful data submission.

## 9: Data Input Validation
As a User,  
I want the application to validate my manual data entries,  
so that I can ensure the accuracy and consistency of the stored data.

### Acceptance Criteria
- Verify that Response and Mass error values use decimal points, not commas.
- Validate Sampleset format (YYYYMMDD_).
- Check for duplicate entries before submission.
- Display specific error messages for each validation failure.

## 10: Interactive Data Visualization
As a User,  
I want to interact with the data visualizations,  
so that I can better analyze trends and specific data points.

### Acceptance Criteria
- Enable zooming and panning in all plots.
- Show data values on hover.
- Allow toggling of different peptide traces.
- Maintain consistent color coding across all plots.
- Provide clear labels and titles for all plots.

## 11: Time-Based Data Analysis
As a User,  
I want to see how SST measurements change over time,  
so that I can identify trends and potential instrument issues.

### Acceptance Criteria
- Display data chronologically in all plots.
- Show clear date formatting on x-axes.
- Highlight temporal trends in response values.
- Enable easy comparison between different time periods.
- Separate visualization of recent vs. historical data points.