from connectors.maximo_connector import MaximoConnector
from connectors.db_connector import PostgresConnector
from connectors.db_schemas.table_schema import TablesSchema
from connectors.vector_db_connector import MilvusConnector
from datetime import date


def test_get_maximo_data():
    connector = MaximoConnector()
    params = {
            "oslc.where": "wonum=5001",
            "oslc.select": "wonum,description,wopriority,createdby,workorderid,status,siteid",
            "lean": 1,
            "ignorecollectionref": 1
        }
    params = {'oslc.where': 'reportdate="1998-12-31T09:00:00+00:00"', 'oslc.select': 'description,wopriority,wonum', 'lean': '1', 'ignorecollectionref': '1'}
    params = {'oslc.where': 'wonum=5000', 'oslc.select': '*', 'lean': '1', 'ignorecollectionref': '1'}
    # params= {
	# 	"oslc.where": "reportdate>=\"1998-12-31T09:00:00\" and reportdate<=\"1998-12-31T17:00:00\"",
	# 	"oslc.select": "wonum,description,reportdate",
	# 	"lean": "1",
	# 	"ignorecollectionref": "1"
	# }
    data = connector.get_workorder_details(params)
    print(data)
    breakpoint()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0
    print("Test passed! Get request successfully returned data.")


def test_update_maximo_data():
    connector = MaximoConnector()
    params = {
            "oslc.where": "wonum=5001",
            "wopriority": "1",
            "siteid": "BEDFORD",
            "lean": 1
        }
    
    data = connector.post_workorder_details(params)
    print(data)
    breakpoint()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0
    print("Test passed! Get request successfully returned data.")


def test_postgres_create_table():
    """
    Test postgres create table
    """
    pg_connector = PostgresConnector()
    schema = TablesSchema.postgres_metadata_schema
    pg_connector.create_table(table_name="test2", schema=schema)


def test_postgres_insert_data():
    """
    Test postgres insert data
    """
    pg_connector = PostgresConnector()
    data= {
        "id": 999,
        "query": "Test query here",
        "issue": "Cannot install",
        "severity": 3,
        "createdate": date.today(),
        "status": "closed",
        "resolutiondate": date.today()
    }
    pg_connector.insert_data(table_name="test2", data=data)


def test_postgres_query_data():
    """
    Test postgres query data
    """
    pg_connector = PostgresConnector()
    query = 'SELECT * FROM "TEST"'
    query = "SELECT COUNT(*) FROM test2 WHERE status = 'closed';"
    data = pg_connector.query_data(query=query)
    return data


def test_milvus_search():
    """
    Test Milvus similarity search
    """
    query = "What technologies are supported for containerized deployment of FCC application?"
    milvus_conn = MilvusConnector()
    results = milvus_conn.search(query=query)

    print("\n🔍 Search Results:")
    for i, res in enumerate(results, 1):
        print(f"\nResult {i}:\n{res.page_content}\n")

    return results


def test_postgres_run_query():
    """
    Test postgres run query
    """
    pg_connector = PostgresConnector()
    queries = [
        'SELECT * FROM test2', 
        'INSERT INTO test2 (id, query, issue, severity, createdate, status, resolutiondate) VALUES (998, \'Test query here\', \'Cannot install\', 3, \'2025-01-03\', \'closed\', \'2023-02-01\')'
               ]
    
    results = []
    for query in queries:
        data = pg_connector.run_query(query=query)
        print(data)
        results.append(data)
    
    return results


def test_postgres_list_table_schemas():
    """
    Test postgres list table schemas
    """
    pg_connector = PostgresConnector()
    schemas = pg_connector.list_table_schemas()
    print(schemas)

    return schemas

def test_validate_with_pglast():
    """
    Test validate with pglast
    """
    pg_connector = PostgresConnector()
    sql = 'SELECT * FROM jira_data'
    is_valid = pg_connector.validate_with_pglast(sql=sql)
    if is_valid:
        print(f"{sql} is valid SQL.")
    else:
        print(f"{sql} is not valid SQL.")
    

    # What was the latest Jira ticket that was created?
    sql2 = """```sql
            SELECT * FROM jira_data ORDER BY "Created" DESC LIMIT 1;
            ```"""
    is_valid = pg_connector.validate_with_pglast(sql=sql2)
    if is_valid:
        print(f"{sql2} is valid SQL.")
    else:
        print(f"{sql2} is not valid SQL.")

    sql3 = 'SELECT * FROM jira_data WHERE id = 1 AND status = "open"'
    is_valid = pg_connector.validate_with_pglast(sql=sql3)
    if is_valid:
        print(f"{sql3} is valid SQL.")
    else:
        print(f"{sql3} is not valid SQL.")
    
    breakpoint()