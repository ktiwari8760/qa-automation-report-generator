# Importing the required libraries
import matplotlib.pyplot as plt
import re
import streamlit as st
import pandas as pd
############################       Funtions Used        ######################################


def extract_method_name(input_string):
  match = re.search(r'[^.]+$', input_string)
  if match:
    return match.group()
  else:
    return None
def extract_lines_which_have_error_in_them(input_string):
    if input_string:
        # Match patterns for errors and exceptions in multiline text
        pattern1 = r"^.*Error.*$"
        pattern2 = r"^.*Exception.*$"
        matches1 = re.findall(pattern1, input_string, re.MULTILINE)
        matches2 = re.findall(pattern2, input_string, re.MULTILINE)
        matches = matches1 + matches2
        return matches if matches else None
    else:
        return None
def get_error_name(input_list):
  for ele in input_list:
      match = re.search(r'(\w+Error)', ele)  # Looks for a word ending with "Error"
      return match.group(1) if match else None
def get_exception_name(input_list):
    for ele in input_list:
        match = re.search(r'(\w+Exception)', ele)  # Looks for a word ending with "Exception"
        if match:
            return match.group(1)
    return None
def get_error_description(input_list):
    for ele in input_list:
      match = re.search(r':\s*(.*)', ele)  # Captures everything after the colon and space
      return match.group(1) if match else None
def extract_code_expected(text):
    # Regex to find the number after 'find'
    pattern = r'find \[(\d+)\]'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None
def extract_code_found(text):
    # Regex to find the number after 'found'
    pattern = r'found \[(\d+)\]'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None
def filtering(df , column1 , filtering_value , expectation = "Equals"):
  if expectation == "Equals":
    filtered_data_frame = df[df[column1] == filtering_value]
  elif  expectation == "Greater":
    filtered_data_frame = df[df[column1] > filtering_value]
  elif  expectation == "Lesser":
    filtered_data_frame = df[df[column1] < filtering_value]
  else:
    raise Exception(f"Invalid value for {expectation}")
  return filtered_data_frame
def test_cases_with_invalid_names(casesnames):
  # Generalized regex pattern for valid test case names
  pattern = r"^[A-Za-z]+_[A-Za-z]+[A-Za-z0-9]*_[A-Za-z]+[A-Za-z0-9]*$"
  if not re.match(pattern, casesnames):
    return "Test Cases Name Not Proper"
  else:
    None

################################################################################################


st.set_page_config(page_title="Paytm || OE - QA Test Cases", layout="wide")
st.title("Paytm || OE - QA Test Cases Report Analyzer" )

# Upload the file
st.header("Upload the Devices.xml file")
uploaded_file = st.file_uploader("Choose a file", type=["xml"])
if uploaded_file is not None:
    st.write("File uploaded successfully.")
    st.write("File details:")
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    if uploaded_file.type == "text/xml":
        df = pd.read_xml(uploaded_file)
        st.write("Uploaded File Data")
        st.dataframe(df)
    else:
        st.write("Please upload an XML file.")
if uploaded_file is not None:

########### Code for finding the test cases which are taking time longer than expected ###########

    st.header("Did you want to see the data for the cases which are taking time longer than expected ?")
    button = st.button("Yes")
    if button:
        if 'time' in df.columns:
            meantime = df['time'].mean()
            filtered_rows_based_on_time = df[df['time'] > meantime]
            st.write("The cases that are taking time longer than expected are:")
            filtered_rows_based_on_time[['name', 'time']]
        else:
            st.write("The uploaded file does not contain the 'time' column.")

##########################################Adding Columns to my Xml #################################################
    if 'time' in df.columns :
        df['mean_time'] = df['time'].mean()
    if 'classname' in df.columns:
        df['class_name'] = df['classname'].apply(extract_method_name)
    if 'failure' in df.columns:
        df['error'] = df['failure'].apply(extract_lines_which_have_error_in_them)
        error_rows = df[df["error"].notna()]
        error_rows.loc[:, 'error_name'] = error_rows["error"].apply(get_error_name)
        error_rows.loc[:, 'error_description'] = error_rows["error"].apply(get_error_description)
        error_rows.loc[:, 'exception_name'] = error_rows["error"].apply(get_exception_name)
        error_rows.loc[:, 'Status_code_expected'] = error_rows["error_description"].apply(extract_code_expected)
        error_rows.loc[:, 'Status_code_found'] = error_rows["error_description"].apply(extract_code_found)

############################################## Code to see the cases which are failing ########################################################################

    st.header("Do you want to see the Test Cases which are failing ?")
    button_testcase_failing = st.button("Yes", key="button_testcase_failing")
    if button_testcase_failing:
        error_rows[["name", "error", "error_name", "exception_name", "error_description", "Status_code_expected","Status_code_found"]]

########################################## Error Searching in File #################################################

    st.header("The types of errors found in the report are:")
    grouped_error_data = pd.DataFrame(error_rows.groupby("error_name").count())
    grouped_error_data["failure"]
    Error = st.text_input("Enter the Error you want to search for " , key = "Error")
    button_error_search = st.button("Search" , key = "button_error_search")
    if button_error_search:
        filtered = filtering(error_rows, column1="error_name", filtering_value=Error)
        filtered
    st.write("The types of exceptions found in the report are:")
    grouped_exception_data = pd.DataFrame(error_rows.groupby("exception_name").count())
    grouped_exception_data["failure"]
    Exceptions = st.text_input("Enter the Exception you want to search for " , key = "Exceptions")
    button_exception_search = st.button("Search", key="button_exception_search")
    if button_exception_search:
        filtered = filtering(error_rows, column1="exception_name", filtering_value=Exceptions)
        filtered

########################################## Error Searches in file based upon Status Code #################################################

    st.header("List of Status Codes Found")
    statuscode_unique_values = error_rows['Status_code_found'].unique()
    statuscode_unique_values
    statuscode = st.number_input("Enter Status Code", step=1)
    button_statuscode_search = st.button("Search", key="button_statuscode_search")
    if button_statuscode_search:
        filtered = filtering(error_rows , column1 = "Status_code_found" , filtering_value = statuscode , expectation = "Equals")
        filtered

########################################## Cases which might have names which are not having names proper #################################################
    st.header("Do you want to see test cases which might have names not proper ?")
    button_cases_name_not_proper = st.button("Yes", key="button_cases_name_not_proper")
    if button_cases_name_not_proper:
        df["Cases Name not Proper"] = df["name"].apply(test_cases_with_invalid_names)
        cases_name_not_proper = filtering(df, column1="Cases Name not Proper", filtering_value="Test Cases Name Not Proper",expectation="Equals")
        cases_name_not_proper[["name", "Cases Name not Proper"]]

########################################## Plotting the data #################################################
    st.header("Do you want to see the plots for the data ?")
    button_plot = st.button("Yes", key="button_plot")
    if button_plot:
        grouped_error_data = pd.DataFrame(error_rows.groupby("error_name").count())
        grouped_error_Data_byname = grouped_error_data["name"]
        try:
            fig, ax = plt.subplots()
            grouped_error_Data_byname.plot(kind='bar', color='violet', legend=False)
            ax.set_title("Errors vs Count Plot")
            ax.set_xlabel('Errors')
            ax.set_ylabel('Counts of Errors')
            ax.set_xticklabels(grouped_error_Data_byname.index, rotation=0)
            st.pyplot(fig)
        except Exception as e:
            print(f"Following Error Occured {e}")
        grouped_exception_data = error_rows.groupby("exception_name").count()
        grouped_exception_data_name = grouped_exception_data["name"]
        try:
            # Plot the data
            fig, ax = plt.subplots()  # Create a figure and axis
            grouped_exception_data_name.plot(kind='bar', color='violet', legend=False, ax=ax)
            ax.set_title("Exceptions vs Count Plot")
            ax.set_xlabel('Exceptions')
            ax.set_ylabel('Counts of Exceptions')
            ax.set_xticklabels(grouped_exception_data_name.index, rotation=0)

            # Show plot in Streamlit
            st.pyplot(fig)  # Display the plot in Streamlit

        except Exception as e:
            st.write(f"Following error occurred: {e}")
