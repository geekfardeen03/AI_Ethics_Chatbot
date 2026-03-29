def build_prompt(user_query, context, domain):
    return f"""
You are an AI Ethics Assistant.

User Query: {user_query}
Domain: {domain}

Relevant Knowledge:
{context}

Give response in this format:

Answer:
Explanation:
Ethical Principle:
"""