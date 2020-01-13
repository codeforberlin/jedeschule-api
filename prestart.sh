echo "Waiting for postgres..."

until pg_isready -h db -p 5432
do
  sleep 2.5
done

echo "PostgreSQL started"
