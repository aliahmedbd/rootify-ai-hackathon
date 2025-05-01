"""
Store schemas for tables to help with construction of queries
"""

class TablesSchema:

    postgres_metadata_schema = """(
        id SERIAL PRIMARY KEY,
        query TEXT,
        issue TEXT,
        severity INTEGER,
        createdate DATE,
        status TEXT,
        resolutiondate Date
    )"""