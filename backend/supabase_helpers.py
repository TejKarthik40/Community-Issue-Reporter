from supabase_client import supabase

def insert_issue(issue_type, location, description, reporter_name, phone_number):
    data = {
        "issue_type": issue_type,
        "location": location,
        "description": description,
        "reporter_name": reporter_name,
        "phone_number": phone_number,
        "status": "new"
    }
    res = supabase.table("community_issues").insert(data).execute()
    return res.data
