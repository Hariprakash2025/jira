#jira 5 is working to update without table

import streamlit as st
import requests
import json
from datetime import datetime
import pytz
from collections import Counter

# Timezone Setup
timezone_ist = pytz.timezone("Asia/Kolkata")
timezone_est = pytz.timezone("America/New_York")
current_utc_time = datetime.now(pytz.utc)
ist_time = current_utc_time.astimezone(timezone_ist).strftime("%d %b %Y %H:%M:%S")
est_time = current_utc_time.astimezone(timezone_est).strftime("%d %b %Y %H:%M:%S")

# JIRA Credentials (Replace with actual API token)
JIRA_URL = "https://thenameishari.atlassian.net/"
JIRA_EMAIL = "hariromil@gmail.com"
JIRA_API_TOKEN = ""

st.title("JIRA Bug Tracking & Reporting")

# User Inputs for Bug Count Calculation
start_date = st.date_input("Start Date for Bug Count", datetime(2024, 1, 1))
end_date = st.date_input("End Date for Bug Count", datetime(2024, 12, 31))
search_words_input = st.text_area("Enter Words to Search in Bug Summaries (comma-separated)", "Env Issue, PT Issue")
search_words = [word.strip() for word in search_words_input.split(",")]

# Function to Fetch JIRA Bug Data for a Search Word
def get_bug_data(search_word):
    JQL_query = f"project = EPE AND issuetype = Bug AND summary ~ '{search_word}' AND createdDate >= '{start_date}' AND createdDate <= '{end_date}'"
    url = f"{JIRA_URL}/rest/api/3/search?jql={JQL_query}&fields=summary,status"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        return []

# Process Bug Data and Count Word Occurrences
bug_summary_data = {}

if st.button("Fetch and Group Bugs"):
    for search_word in search_words:
        bug_data = get_bug_data(search_word)
        
        # Group by Summary
        bug_summaries = [bug["fields"]["summary"] for bug in bug_data]
        grouped_bugs = Counter(bug_summaries)
        
        # Count Bugs Closed and Open only for the given search word
        bugs_closed = sum(1 for bug in bug_data if bug["fields"]["status"]["name"] == "Done")
        bugs_open = sum(1 for bug in bug_data if bug["fields"]["status"]["name"] in ["Open", "In Progress"])

        # Store in Session State
        bug_summary_data[search_word] = {
            "bugs_closed": bugs_closed,
            "bugs_open": bugs_open,
            "grouped_bugs": grouped_bugs
        }

    st.session_state["bug_summary_data"] = bug_summary_data

# Display Results
for search_word, data in st.session_state.get("bug_summary_data", {}).items():
    st.subheader(f"{search_word} - Bug Summary")
    st.text_input(f"Bugs Closed ({search_word})", value=data["bugs_closed"], disabled=True)
    st.text_input(f"Bugs Still Open ({search_word})", value=data["bugs_open"], disabled=True)

    if data["grouped_bugs"]:
        st.subheader(f"Grouped Bug Summaries for {search_word}")
        for summary, count in data["grouped_bugs"].items():
            st.write(f"**{summary}** - {count} times")

# User Inputs for JIRA Issue Update
issue_key = st.text_input("Full JIRA Issue Key (e.g., EPE-23271)", "")
planned_end_date = st.date_input("Planned End Date (Leave empty for Sprint End Date)", None)
actual_start_date = st.date_input("Actual Start Date (First Work Log Entry)", None)

# Clear button for Actual Start Date
if st.button("Clear Actual Start Date"):
    actual_start_date = None

scripts_planned = st.number_input("Scripts Planned", min_value=0, value=5)
scripts_created = st.number_input("Scripts Created", min_value=0, value=3)
tests_planned = st.number_input("Tests Planned", min_value=0, value=10)
tests_executed = st.number_input("Tests Executed", min_value=0, value=8)
triage_flag = st.selectbox("Triage Flag", ["Yes", "No"])
task_type_flag = st.selectbox("Task Type", ["Planned", "Adhoc", "Extension"])
extension_reason = st.text_area("Reason for Extension (If applicable)")

if st.button("Submit to JIRA"):
    if not issue_key:
        st.error("Please enter a valid JIRA Issue Key!")
    else:
        planned_end_date_str = planned_end_date.strftime("%Y-%m-%d") if planned_end_date else "Sprint End Date"
        actual_start_date_str = actual_start_date.strftime("%Y-%m-%d") if actual_start_date else "Not Available"

        bug_details = ""
        for search_word, data in st.session_state.get("bug_summary_data", {}).items():
            bug_details += f"\n{search_word} :-\n"
            bug_details += f"   Bugs Closed: {data['bugs_closed']}\n"
            bug_details += f"   Bugs Still Open: {data['bugs_open']}\n"

            # if data["grouped_bugs"]:
            #     bug_details += "\nGrouped Bugs:\n"
            #     for summary, count in data["grouped_bugs"].items():
            #         bug_details += f"- {summary} ({count} times)\n"

        message = f"""
        Issue Key: {issue_key}
        Planned End Date: {planned_end_date_str}
        Actual Start Date: {actual_start_date_str}
        Scripts Planned: {scripts_planned}
        Scripts Created: {scripts_created}
        Tests Planned: {tests_planned}
        Tests Executed: {tests_executed}
        Triage Flag: {triage_flag}
        Task Type: {task_type_flag}
        Reason for Extension: {extension_reason}
        {bug_details}
        Last Updated:
        IST: {ist_time}
        EST: {est_time}
        """
       

        # for comment

        # payload = {
        #     "body": {
        #         "type": "doc",
        #         "version": 1,
        #         "content": [
        #             {
        #                 "type": "paragraph",
        #                 "content": [{"type": "text", "text": message}]
        #             }
        #         ]
        #     }
        # }

        # for description

        # payload = {
        #     "fields": {
        #         "description": {
        #             "type": "doc",
        #             "version": 1,
        #             "content": [
        #                 {
        #                     "type": "paragraph",
        #                     "content": [{"type": "text", "text": message}]
        #                 }
        #             ]
        #         }
        #     }
        # }
        false="false"
        with open('payload.json', 'r') as file:
            data = json.load(file)
        payload = data.replace("${issue_key}",issue_key)
               
        # JIRA API Request
        # url_comment = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
        url_comment = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
        
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        # response = requests.post(url_comment, headers=headers, auth=(JIRA_EMAIL, JIRA_API_TOKEN), data=json.dumps(payload))
        response = requests.put(url_comment, headers=headers, auth=(JIRA_EMAIL, JIRA_API_TOKEN), data=json.dumps(payload))
        if response.status_code == 204:
            st.success(f"Comment successfully added to JIRA issue {issue_key}!")
        else:
            st.error(f"Failed to add comment: {response.status_code}, {response.text}")


