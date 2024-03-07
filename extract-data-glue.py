import time
import boto3
import psycopg2

# Initialize the Athena client
athena_client = boto3.client('athena', region_name='us-east-2')

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="smart-city",
    user="aditsvet",
    password="abcd1234"
)
cursor = conn.cursor()

# Fetch list of tables in smartcity-database
def get_table_list():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'smartcity-database';"
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'smartcity-database'},
        ResultConfiguration={'OutputLocation': 's3://smart-city-streaming-data-aditsvet/output/'}
    )
    execution_id = response['QueryExecutionId']
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        print("Status: ", status)
        time.sleep(5)


    if status != 'SUCCEEDED':
        print("Error fetching table list")
        return []

    results = athena_client.get_query_results(QueryExecutionId=execution_id)
    table_list = [row['Data'][0]['VarCharValue'] for row in results['ResultSet']['Rows'][1:]]
    print (table_list)
    return table_list

# Fetch data for each table and insert into PostgreSQL
def fetch_and_insert_data(table_name):
    print("Fetching data from",table_name)
    query = f"SELECT * FROM {table_name};"
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'smartcity-database'},
        ResultConfiguration={'OutputLocation': 's3://athena-output-aditsvet/ '}
    )
    execution_id = response['QueryExecutionId']
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        print("Status: ", status)
        time.sleep(5)
    print("Final Status: ", status)
    if status != 'SUCCEEDED':
        print(f"Error fetching data for table {table_name}")
        # Print more details about the error
        print("Error message:", response['QueryExecution']['Status']['StateChangeReason'])
        return

    results = athena_client.get_query_results(QueryExecutionId=execution_id)
    columns = [data['VarCharValue'] for data in results['ResultSet']['Rows'][0]['Data']]
    rows = results['ResultSet']['Rows'][1:]

    # Construct the CREATE TABLE statement
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for index, column_name in enumerate(columns):
        create_table_query += f"{column_name} VARCHAR(255)"
        if index < len(columns) - 1:
            create_table_query += ", "
    create_table_query += ")"
    cursor.execute(create_table_query)
    print(f"Table {table_name} created successfully")
    print(f"Columns: {columns}")

    # Construct the INSERT query with parameter placeholders
    insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(columns))})"

    # Iterate over each row of data and insert into the PostgreSQL table

    for row in rows:
        try:
            values = [data['VarCharValue'] for data in row['Data']]
            # Execute the parameterized query with the values for each row
            cursor.execute(insert_query, values)
        except Exception as e:
            print(f"Error inserting data into {table_name}: {e}")
            continue
    conn.commit()
    print(f"Data inserted successfully for table {table_name}")

# Fetch list of tables
tables = get_table_list()
for table in tables:
    fetch_and_insert_data(table)

# Close cursor and connection
cursor.close()
conn.close()
