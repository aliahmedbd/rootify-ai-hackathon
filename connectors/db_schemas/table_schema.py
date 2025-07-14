"""
Store schemas for tables to help with construction of queries
"""

class TablesSchema:

    patterns_lookup_schema = """(
        id SERIAL PRIMARY KEY,
        pattern_tag TEXT,
        solution TEXT,
        example TEXT
    )"""

    postgres_metadata_schema = """(
        id SERIAL PRIMARY KEY,
        query TEXT,
        issue TEXT,
        severity INTEGER,
        createdate DATE,
        status TEXT,
        resolutiondate Date
    )"""

    jira_data_schema = """(
        Issue Type TEXT,
        Key TEXT,
        Summary TEXT,
        Summary TEXT,
        Assignee TEXT,
        Status TEXT,
        Resolution TEXT,
        Created TEXT,
        Resolution Details TEXT,
        Updated Date
    )"""

    user_feedback_schema = """(
        id SERIAL PRIMARY KEY,
        username TEXT,
        feedback TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""