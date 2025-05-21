import mysql.connector

class DbCommandBase:
    def __init__(self, db_config: dict):
        """
        Initializes the database connection and fetches metadata.
        db_config should be a dictionary with keys: 
        'host', 'user', 'password', 'database'
        """
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        self.tables = []
        self.columns = {}  # Dict: {table_name: [col1, col2]}

        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True) # dictionary=True for dict-like rows
                self._fetch_tables()
                self._fetch_columns()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            # Decide how to handle this: raise error, or leave connection as None
            # For now, print error and CLI can check self.connection
            self.connection = None 

    def _fetch_tables(self):
        if not self.cursor: return
        try:
            self.cursor.execute("SHOW TABLES")
            for row in self.cursor.fetchall():
                # row will be a dict, e.g., {'Tables_in_yourdb': 'table_name'}
                # The actual key depends on the database name.
                # It's safer to get the first value from the dict.
                self.tables.append(list(row.values())[0])
        except mysql.connector.Error as err:
            print(f"Error fetching tables: {err}")

    def _fetch_columns(self):
        if not self.cursor: return
        for table_name in self.tables:
            try:
                # Use backticks for table names in DESCRIBE, as they might be keywords
                self.cursor.execute(f"DESCRIBE `{table_name}`") 
                table_cols = []
                for row in self.cursor.fetchall():
                    table_cols.append(row['Field']) # 'Field' is the key for column name in DESCRIBE output
                self.columns[table_name] = table_cols
            except mysql.connector.Error as err:
                print(f"Error fetching columns for table {table_name}: {err}")

    def build_query(self, prefix: str, path: list) -> str:
        """
        Builds a SQL query.
        Example: prefix="SELECT *", path=["users", "status='active'"]
        Returns: "SELECT * FROM `users` WHERE status='active'"
        
        WARNING: This current simple implementation can be prone to SQL injection 
        if elements in 'path' after the table name are user-supplied directly 
        into SQL. For now, it mirrors the PHP version's structure.
        Proper parameterization should be used if path elements are dynamic values.
        """
        if not path:
            raise ValueError("Path cannot be empty for query building.")

        table_name = path[0]
        if table_name not in self.tables:
            # Or handle this more gracefully, maybe return None or raise specific error
            raise ValueError(f"Table '{table_name}' not found.")

        query = f"{prefix} FROM `{table_name}`"

        conditions = path[1:]
        if conditions:
            # Simple join for now. Assumes conditions are valid SQL.
            # This is the part that needs careful handling for SQL injection.
            query += " WHERE " + " AND ".join(conditions)
        
        return query

    def count(self, path: list) -> int:
        """
        Gets the row count for a given path (table and optional conditions).
        """
        if not self.connection or not path: # Check self.connection instead of self.cursor
            print("No database connection.")
            return -1
        
        table_name = path[0]
        if table_name not in self.tables:
            print(f"Table '{table_name}' not found for count.")
            return -1

        # Use a new cursor for count to avoid issues with shared cursor state, especially if dictionary=True causes issues for simple COUNT(*)
        count_cursor = None
        try:
            count_cursor = self.connection.cursor() # Default cursor (tuples)
            query = self.build_query("SELECT COUNT(*)", path)
            count_cursor.execute(query)
            result = count_cursor.fetchone()
            return result[0] if result else -1
        except mysql.connector.Error as err:
            print(f"Error counting rows for path {'/'.join(path)}: {err}")
            return -1
        except ValueError as ve: # From build_query if table not found
            print(ve)
            return -1
        finally:
            if count_cursor:
                count_cursor.close()


    def execute_query(self, query: str, params: tuple = None) -> list[dict] | None:
        """
        Executes a given query, preferably with parameters to prevent SQL injection.
        Returns list of rows (as dicts) or None on error.
        """
        if not self.cursor: # Main cursor for dictionary results
            print("No database connection or cursor.")
            return None
        try:
            self.cursor.execute(query, params)
            # Check the type of query to determine if we need to commit or fetch
            query_upper = query.strip().upper()
            if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE") or query_upper.startswith("EXPLAIN"):
                return self.cursor.fetchall()
            else: # For INSERT, UPDATE, DELETE, CREATE, ALTER, etc.
                self.connection.commit()
                # For operations like INSERT, it's common to return lastrowid or rowcount
                # For this generic method, returning rowcount is a reasonable default
                return [{"affected_rows": self.cursor.rowcount, "last_row_id": self.cursor.lastrowid}] 
        except mysql.connector.Error as err:
            print(f"Error executing query '{query[:100]}...': {err}")
            try:
                if self.connection and self.connection.is_connected(): # Check if connection exists before rollback
                    self.connection.rollback()
            except mysql.connector.Error as roll_err:
                print(f"Error during rollback: {roll_err}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None # Set to None after closing
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None # Set to None after closing
        print("Database connection closed.")

if __name__ == '__main__':
    # Example Usage (requires a MySQL server and 'test_db' database)
    # Create a dummy test_db and a user table for this to work
    # CREATE DATABASE test_db;
    # USE test_db;
    # CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), status VARCHAR(50));
    # INSERT INTO users (name, email, status) VALUES ('Test User', 'test@example.com', 'active');
    # INSERT INTO users (name, email, status) VALUES ('Another User', 'another@example.com', 'inactive');

    print("Attempting to connect to local MySQL database 'test_db'...")
    # IMPORTANT: Replace with your actual MySQL credentials and database name
    config = {
        'host': 'localhost',    # Or your MySQL host
        'user': 'your_user',    # Your MySQL username
        'password': 'your_password', # Your MySQL password
        'database': 'test_db'   # Your database name
    }
    
    # Check if the user has set up their environment, otherwise skip this test
    import os
    if config['user'] == 'your_user' or config['password'] == 'your_password' or config['database'] == 'test_db_placeholder':
        print("\nSkipping DbCommandBase example: Please update placeholder credentials and database name in db_command_base.py")
        print("Ensure 'test_db' exists and the user has permissions.")
        print("Example DDL for 'users' table:")
        print("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), status VARCHAR(50));")

    else:
        db_base = DbCommandBase(config)

        if db_base.connection and db_base.connection.is_connected(): # Check connection status
            print("\nSuccessfully connected to the database.")
            print("Tables found:", db_base.tables)
            if db_base.columns: # Only print if columns were fetched
                 print("Columns found:", db_base.columns)

            if 'users' in db_base.tables:
                print("\nQuerying all users:")
                # Using execute_query for fetching
                all_users = db_base.execute_query("SELECT id, name, status FROM `users`")
                if all_users is not None: # Check for None in case of query error
                    print(f"Generated Query: SELECT id, name, status FROM `users` (via execute_query)")
                    for user in all_users:
                        print(user)
                
                print("\nQuerying active users (example of path with condition using build_query and execute_query):")
                try:
                    active_users_query = db_base.build_query("SELECT id, name", ["users", "status='active'"])
                    print(f"Generated Query: {active_users_query}")
                    active_users = db_base.execute_query(active_users_query)
                    if active_users is not None:
                        for user in active_users:
                            print(user)
                except ValueError as e:
                    print(f"Error building query for active users: {e}")


                print("\nCounting active users:")
                num_active = db_base.count(["users", "status='active'"])
                print(f"Number of active users: {num_active}")

                print("\nCounting all users:")
                num_total = db_base.count(["users"])
                print(f"Total number of users: {num_total}")
                
                print("\nExample of an INSERT statement:")
                # Note: Column order matters if not specifying column names in INSERT
                insert_query = "INSERT INTO `users` (name, email, status) VALUES (%s, %s, %s)"
                insert_params = ("New User", "new@example.com", "pending")
                result = db_base.execute_query(insert_query, insert_params)
                if result and result[0].get("affected_rows", 0) > 0 :
                    print(f"User inserted successfully. Affected rows: {result[0]['affected_rows']}, Last ID: {result[0]['last_row_id']}")
                    # Verify by counting again
                    num_total_after_insert = db_base.count(["users"])
                    print(f"Total number of users after insert: {num_total_after_insert}")
                else:
                    print("Failed to insert user or no rows affected.")

            else:
                print("\n'users' table not found in the database. Skipping table-specific tests.")

            db_base.close()
        else:
            print("\nFailed to connect to the database. Please check your configuration, MySQL server status, and ensure 'test_db' exists.")
            if 'MYSQL_USER' not in os.environ or 'MYSQL_PASSWORD' not in os.environ or 'MYSQL_DATABASE' not in os.environ or 'MYSQL_HOST' not in os.environ:
                 print("Hint: Consider setting environment variables for DB credentials for automated testing (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST).")

    ```
