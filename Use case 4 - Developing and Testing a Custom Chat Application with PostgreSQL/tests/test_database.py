import pytest

from database import validate_read_only_sql


@pytest.mark.parametrize(
    "query",
    [
        "SELECT id, name FROM customers",
        "SELECT status, COUNT(*) FROM orders GROUP BY status;",
        "WITH totals AS (SELECT customer_id, SUM(amount) AS value FROM orders "
        "GROUP BY customer_id) SELECT * FROM totals",
    ],
)
def test_accepts_read_only_queries(query):
    assert validate_read_only_sql(query)


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM customers",
        "UPDATE orders SET status = 'paid'",
        "DROP TABLE orders",
        "SELECT 1; SELECT 2",
        "",
    ],
)
def test_rejects_unsafe_queries(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)
