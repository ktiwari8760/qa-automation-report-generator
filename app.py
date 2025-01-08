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
      #match = re.search(r'(\w+Error)', ele)  # Looks for a word ending with "Error"
      match = re.search(r'([a-zA-Z]+Error)' , ele)
      return match.group(1) if match else None
def get_exception_name(input_list):
    for ele in input_list:
        match = re.search(r'([a-zA-Z]+Exception)', ele)  # Looks for a word ending with "Exception"
        if match:
            return match.group(1)
    return None
def get_error_description(input_list):
    for ele in input_list:
      match = re.search(r':\s*(.*)', ele)  # Captures everything after the colon and space
      return match.group(1) if match else None
def extract_code_expected(text):
    # Regex to find the number after 'find'
    pattern = r'expected \[(\d+)\]'
    #pattern = r'expected \[([^\]]+)\]'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None
def extract_code_found(text):
    # Regex to find the number after 'found'
    pattern = r'found \[(\d+)\]'
    #pattern = r'found \[([^\]]+)\]'

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
  pattern = r'^TC_\d+$'
  if re.match(pattern, casesnames):
    return "Test Cases Name Not Proper"
  return "Name is valid"


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

###################################### Jacoco Code ##########################################################

st.header("Latest Jacoco Report - OE ")
jacocoreport_button = st.button("Click here to see the latest Jacoco Report")

try:
    report = pd.read_html("index.html")
    jacoco_df = pd.DataFrame(report[0])
    jacoco_df.rename(columns={'Element': 'Packages', 'Cov.': 'Instructions Coverage', 'Cov..1': 'Branch Coverage',
                              'Missed.1': 'Missed Lines in Code', 'Lines': 'Total Lines in Code',
                              'Missed.2': 'Missed methods in Package', 'Methods': 'Methods in Package',
                              'Missed.3': 'Missed classes in Package'}, inplace=True)
    jacoco_df = jacoco_df[jacoco_df['Packages'] != 'Total']
except Exception as e:
    st.write(f"Following error occured {e}")

if jacocoreport_button:
    jacoco_df

jacocoreport_button_class = st.button("Click here to see the class level Jacoco Report")
if jacocoreport_button_class:
    st.write("The data for the class level Jacoco Report is : ")
    st.write('Total classes in the code are : ', jacoco_df['Classes'].sum())
    st.write('Missed classes in the code are : ', jacoco_df['Missed classes in Package'].sum())
    st.write('The percentage of the classes covered is : ',
             (jacoco_df['Classes'].sum() - jacoco_df['Missed classes in Package'].sum()) / jacoco_df['Classes'].sum() * 100)

    jacoco_df[['Packages' , 'Missed classes in Package' , 'Classes']]

    plt.figure(figsize=(2, 2))
    plt.pie([jacoco_df['Missed classes in Package'].sum(), jacoco_df['Classes'].sum() - jacoco_df['Missed classes in Package'].sum()], labels=['Missed', 'Covered'], autopct='%1.1f%%', startangle=90)
    plt.title("Overall Missed Classes vs Total Classes")
    plt.axis('equal')
    st.pyplot(plt)


jacocoreport_button_method = st.button("Click here to see the method level Jacoco Report")
if jacocoreport_button_method:
    st.write("The data for the method level Jacoco Report is : ")

    st.write('Total methods in the code are : ', jacoco_df['Methods in Package'].sum())
    st.write('Missed methods in the code are : ', jacoco_df['Missed methods in Package'].sum())
    st.write('The percentage of the methods covered is : ',
             (jacoco_df['Methods in Package'].sum() - jacoco_df['Missed methods in Package'].sum()) / jacoco_df[
                 'Methods in Package'].sum() * 100)
    jacoco_df[['Packages' , 'Missed methods in Package' , 'Methods in Package']]

    plt.figure(figsize=(2, 2))
    plt.pie([jacoco_df['Missed methods in Package'].sum(), jacoco_df['Methods in Package'].sum() - jacoco_df['Missed methods in Package'].sum()], labels=['Missed', 'Covered'], autopct='%1.1f%%', startangle=90)
    plt.title("Overall Missed Methods vs Total Methods")
    plt.axis('equal')
    st.pyplot(plt)
jacocoreport_button_lines = st.button("Click here to see the lines level Jacoco Report")
if jacocoreport_button_lines:
    st.write("The data for the lines level Jacoco Report is : ")
    total_lines = jacoco_df['Total Lines in Code'].sum()
    total_missed_lines = jacoco_df['Missed Lines in Code'].sum()
    st.write('Total lines in the code are : ' , total_lines)
    st.write('Missed lines in the code are : ' , total_missed_lines)
    st.write('The percentage of the code covered is : ' , (jacoco_df['Total Lines in Code'].sum() - jacoco_df['Missed Lines in Code'].sum()) / jacoco_df['Total Lines in Code'].sum() * 100)
    jacoco_df[['Packages' , 'Missed Lines in Code' , 'Total Lines in Code']]
    plt.figure(figsize=(2, 2))
    plt.pie([total_missed_lines, total_lines - total_missed_lines], labels=['Missed', 'Covered'], autopct='%1.1f%%', startangle=90)
    plt.title("Overall Missed Lines vs Total Lines")
    plt.axis('equal')
    st.pyplot(plt)



#################################################################################################################

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
        error_rows[["name", "error", "error_name", "exception_name", "error_description", "Status_code_expected","Status_code_found" ]]

########################################## Error Searching in File #################################################

    st.header("The types of errors found in the report are:")
    grouped_error_data = pd.DataFrame(error_rows.groupby("error_name").count())
    grouped_error_data["failure"]
    Error = st.text_input("Enter the Error you want to search for " , key = "Error")
    button_error_search = st.button("Search" , key = "button_error_search")
    if button_error_search:
        filtered = filtering(error_rows, column1="error_name", filtering_value=Error)
        filtered[["classname", "name" , "time" ,"failure" , "error" , "error_name" , "error_description" , "Status_code_expected" , "Status_code_found"]]
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
    statuscode_unique_values = error_rows['Status_code_found'].value_counts()
    statuscode_unique_values
    statuscode = st.number_input("Enter Status Code", step=1)
    button_statuscode_search = st.button("Search", key="button_statuscode_search")
    if button_statuscode_search:
        filtered = filtering(error_rows , column1 = "Status_code_found" , filtering_value = statuscode , expectation = "Equals")
        filtered

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
            ax.set_xticklabels(grouped_error_Data_byname.index, rotation=45)
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
            ax.set_xticklabels(grouped_exception_data_name.index, rotation=45)

            # Show plot in Streamlit
            st.pyplot(fig)  # Display the plot in Streamlit

        except Exception as e:
            st.write(f"Following error occurred: {e}")


########################################## Cases which might have names which are not having names proper #################################################
    st.header("Do you want to see test cases which might have names not proper ?")
    button_cases_name_not_proper = st.button("Yes", key="button_cases_name_not_proper")
    if button_cases_name_not_proper:
        df["Cases Name not Proper"] = df["name"].apply(test_cases_with_invalid_names)
        cases_name_not_proper = filtering(df, column1="Cases Name not Proper", filtering_value="Test Cases Name Not Proper",expectation="Equals")
        st.write("Number of test case which do not have correct names are : " , cases_name_not_proper.shape[0])
        cases_name_not_proper[["classname" , "name"]]

############################################################################################################




