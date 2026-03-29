def detect_domain(query):
    query = query.lower()

    if "hospital" in query or "patient" in query:
        return "Healthcare"
    elif "loan" in query or "bank" in query:
        return "Finance"
    elif "hiring" in query or "job" in query:
        return "Recruitment"
    else:
        return "General"