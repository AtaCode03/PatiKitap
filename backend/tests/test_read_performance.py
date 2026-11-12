from sqlalchemy import event, text
import main
from test_api import client, book


def capture_queries():
    queries = []
    def capture(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)
    event.listen(main.engine, 'before_cursor_execute', capture)
    return queries, capture


def test_readiness_checks_schema_in_one_query(client):
    queries, capture = capture_queries()
    try:
        assert client.get('/api/ready').status_code == 200
        assert len(queries) == 1
        for table in main.Base.metadata.sorted_tables:
            assert table.name in queries[0]
    finally:
        event.remove(main.engine, 'before_cursor_execute', capture)


def test_readiness_rejects_missing_table(client):
    with main.engine.begin() as connection:
        connection.execute(text('DROP TABLE audit_logs'))
    assert client.get('/api/ready').status_code == 503


def test_impact_aggregates_in_one_query_without_multiplying_counts(client):
    book(client)
    book(client)
    queries, capture = capture_queries()
    try:
        response = client.get('/api/impact')
        assert response.status_code == 200
        assert response.json() == {
            'mode':'simulation', 'support_rate':0.2, 'completed_transactions':0,
            'active_books':2, 'demo_books':0, 'simulated_support_cents':0,
            'real_support_cents':0, 'participants':1,
        }
        assert len(queries) == 1
    finally:
        event.remove(main.engine, 'before_cursor_execute', capture)
