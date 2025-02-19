import requests
import json
from datetime import datetime
import pytz

timezone_ist = pytz.timezone("Asia/Kolkata")
timezone_est = pytz.timezone("America/New_York")
current_utc_time = datetime.now(pytz.utc)
ist_time = current_utc_time.astimezone(timezone_ist).strftime("%d %b %Y %H:%M:%S")
est_time = current_utc_time.astimezone(timezone_est).strftime("%d %b %Y %H:%M:%S")

PROJECT="hariprakash_workspace"
LABEL=""
createdDate="2025-01-01"
JIRA_URL = ""
JIRA_EMAIL = ""
JIRA_API_TOKEN = ""  # Replace with your API token
ISSUE_KEY = "EPE-1"
url_comment = f"{JIRA_URL}/rest/api/3/issue/{ISSUE_KEY}/comment"

def jql(query):
    return f"{JIRA_URL}/rest/api/3/search?jql={query}"

JQL_query_1=f"project = {PROJECT} AND issuetype = Bug AND status = 'Done' AND createdDate > {createdDate}" 
# project = hariprakash_workspace AND issuetype = Bug AND status = "In Progress" AND createdDate > startOfYear()

def jql_statement(input,data):
    if input=="JQL_query_1":
        return f"Bugs Closed :{data}"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
last_updated="\n IST:"+str(ist_time)+"\n EST:"+str(est_time)


response_jql_1 = requests.get(jql(JQL_query_1), headers=headers, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
print("JQL_query_1 :"+JQL_query_1)
# Extract the total count of issues
if response_jql_1.status_code == 200:
    total_issues = response_jql_1.json().get("total", 0)
    print(f"Total matching issues: {total_issues}")
else:
    print(f"Failed to fetch JQL results: {response_jql_1.status_code}, {response_jql_1.text}")
    total_issues = "N/A"
message=jql_statement("JQL_query_1",total_issues)

payload = {
    "body": {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"FYI.\n {message} \n \n"
                    },
                    {
                        "type": "text",
                        "text": "Last Updated :",
                        "marks": [
                                {
                                    "type": "strong"  # Makes only this word bold
                                }
                        ]
                    },
                    {
                        "type": "text",
                        "text": f"{last_updated}",
                        
                    }

                ]
            },
            
            
        ]
    }
}



response = requests.post(
    url_comment,
    headers=headers,
    auth=(JIRA_EMAIL, JIRA_API_TOKEN),
    data=json.dumps(payload)
)

print(response.status_code)
if response.status_code == 201:
    print("SUCCESS")
else:
    print("FAILED")
