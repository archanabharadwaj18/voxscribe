from jira import JIRA

def create_jira_tasks(action_items, jira_url, username, api_token, project_key):
    jira = JIRA(server=jira_url, basic_auth=(username, api_token))
    created_keys = []
    
    for item in action_items:
        
        new_issue = jira.create_issue(
            project=project_key,
            summary=item[:255],
            description=item,
            issuetype={'name': 'Task'} 
        )
        created_keys.append(new_issue.key)
        print(f"Sent to Jira: {new_issue.key}")

    return created_keys