echo "Waiting for postgres..."

# TODO: Use pg_isready instead? This is probably not installed here though...
while ! python test_connection.py; do
  sleep 0.5
done

echo "PostgreSQL started"
