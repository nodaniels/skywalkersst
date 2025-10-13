# Operation and Maintenance Description

## Operation

### Starting the Application

1. **Ensure Dependencies are Installed:**

   - Before running the Streamlit app, make sure all necessary dependencies are installed. These can be installed using `pip`:
     ```sh
     pip install -r [requirements.txt]
     ```

2. **Running the Application:**

   - Navigate to the directory containing the Streamlit script file (e.g., `startpage.py`).
   - Run the application using the following command:
     ```sh
     streamlit run main.py
     ```
   - This command will start the Streamlit server, and a URL (typically `http://localhost:8501`) will be provided to access the application in a web browser.

## Maintenance

### Updating the Application

1. **Updating Dependencies:**

   - If necessary, update the dependencies using `pip`:
     ```sh
     pip install --upgrade streamlit plotly
     ```

2. **Modifying the Code:**

   - Open the script file (e.g., `startpage.py`) in your preferred code editor.
   - Make the necessary changes to the code. Save the file and restart the Streamlit server to apply the changes.

3. **Version Updates:**

   - Update the version number and date in the script file as shown below:
     ```python
     st_ver = "0.04"  # New version number
     st_date = "2025-02-01"  # New update date
     ```

### Error Handling

1. **File Upload Issues:**

   - Ensure the uploaded files are in the correct ARW format. If an error message is displayed, check the file type and content.

2. **Parameter Input Errors:**

   - Ensure the input values for "Main peak RT start", "Main peak RT end", and "Spacing" are numerical. Non-numerical values will prompt an error message.

3. **Troubleshooting:**

   - For any other issues, refer to the Streamlit and Plotly documentation or contact the technical support team.

## Contact Information

- **Technical Support:**

  - For solution specific questions, contact [pwdg@novonordisk.com](pwdg@novonordisk.com)
  - For any technical infrastructure issues, contact the DAS Team via their incident link on their [sharepoint](http://dasteam) page.

- **Documentation:**
  - Refer to the official [Streamlit Documentation](https://docs.streamlit.io) and [Plotly Documentation](https://plotly.com/python/) for additional guidance.