"""Example module used in the README to demonstrate EmbedM."""


# md.start:connect
def connect(host, port=5432, timeout=30):
    """Establish a database connection."""
    conn = Database.connect(
        host=host,
        port=port,
        timeout=timeout,
    )
    return conn
# md.end:connect


# md.start:query
def query(conn, sql, params=None):
    """Execute a parameterized query safely."""
    cursor = conn.cursor()
    cursor.execute(sql, params or [])
    return cursor.fetchall()
# md.end:query
