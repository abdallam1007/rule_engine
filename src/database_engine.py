import json
import psycopg2

table = "drivers_order_response" # ! hardcoded for now

# * Note: using a smartEnum when supporting multiple database types, this function will be different
def connect_database(rule):
    # establishing the connection
    db_connection_str = rule["db_connection_str"]
    conn = psycopg2.connect(db_connection_str)
    conn.autocommit = True

    return conn

def close_database(conn, user_db):
    user_db.close()
    conn.close()


# deletes all rows from the PostgresSQL table
def delete_all_rows(rule):
    conn = connect_database(rule)
    user_db = conn.cursor()

    sql = f"DELETE FROM {table}"
    user_db.execute(sql)

    close_database(conn, user_db)

# creates a sql query based on json data structure for a row
def construct_query(update):
    columns = ", ".join(update.keys())
    value_placeholders = ", ".join(["%s"] * len(update))

    query = f"INSERT INTO {table} ({columns}) VALUES ({value_placeholders})"
    return query

# given the round number, read the list of new updatees and create postgresSQL rows
def insert_new_updates(rule):
    conn = connect_database(rule)
    user_db = conn.cursor()

    updates_fp = rule["updates_fp"]
    f = open(updates_fp, 'r')
    data = json.load(f)
    f.close()

    # Get the updates for current round number
    round = rule["round"]
    updates = data[str(round)]

    # for every update, insert a corresponding database row
    for update in updates:
        # construct sql query to insert row in postgres db
        query = construct_query(update)
        row_data = tuple(update.values())
        user_db.execute(query, row_data)

    close_database(conn, user_db)


def update_database(rule):
    rule["round"] += 1
    delete_all_rows(rule)
    insert_new_updates(rule)