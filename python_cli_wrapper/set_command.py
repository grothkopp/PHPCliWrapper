# python_cli_wrapper/set_command.py
from .db_command_base import DbCommandBase
# We might not use pretty_print here, as output is usually minimal (affected rows).

class SetCommand(DbCommandBase):
    def __init__(self, db_config: dict):
        super().__init__(db_config)

    def command(self, current_path: list, args: list) -> int:
        if not self.connection:
            print("Error: No database connection.")
            return 1 # Error status
        
        if not current_path:
            print("Error: No table selected. Use 'cd tablename'.")
            return 1

        table_name = current_path[0]
        if table_name not in self.tables:
            print(f"Error: Table '{table_name}' not found.")
            return 1

        if not args:
            print("Error: No assignments provided for set command. Usage: set column1=value1 column2='value 2' ...")
            return 1

        # Construct SET clause
        set_clauses = []
        # Basic parsing for "column=value" or "column='string value'"
        # This is a simplified parser and has limitations.
        for arg in args:
            if '=' not in arg:
                print(f"Warning: Malformed argument '{arg}'. Expected format 'column=value'. Skipping.")
                continue
            # Split only on the first '=', allowing '=' in the value if it's quoted.
            parts = arg.split('=', 1)
            column = parts[0].strip()
            value_str = parts[1].strip()

            # Validate column - simple check, could be more robust
            if column not in self.columns.get(table_name, []):
                print(f"Warning: Column '{column}' not found in table '{table_name}'. Skipping.")
                continue
            
            # For now, we'll pass value_str directly.
            # IMPORTANT: This is a significant SQL injection vulnerability if value_str is not sanitized
            # or if prepared statements are not used by the execute_query method.
            # The DbCommandBase.execute_query should ideally handle parameterization.
            # Let's assume for now it does, or this needs to be a focus for hardening.
            # For build_query, we're building the SET part, not the WHERE part.
            set_clauses.append(f"`{column}` = {value_str}") # Value needs to be SQL-literal-formatted by user

        if not set_clauses:
            print("Error: No valid column assignments for set command.")
            return 1
        
        set_statement = ", ".join(set_clauses)

        # Construct WHERE clause from path (if any conditions are present)
        # build_query in DbCommandBase takes (prefix, path)
        # Here, prefix is just the table name for the UPDATE statement.
        # The actual WHERE clause is built from path[1:].
        
        where_conditions = current_path[1:]
        where_clause = ""
        if where_conditions:
            # Assuming conditions in path are valid SQL (e.g., "id=1", "name='test'")
            # This also carries an SQL injection risk if path elements are not controlled.
            where_clause = " WHERE " + " AND ".join(where_conditions)
        else:
            # Safety: Do not allow UPDATE without a WHERE clause by default through this command.
            # The user must 'cd' to a specific record or provide conditions in the path.
            print("Error: SET command requires conditions in the path (e.g., cd table/id=1) to specify rows.")
            print("Aborting to prevent accidental update of all rows.")
            return 1

        query = f"UPDATE `{table_name}` SET {set_statement}{where_clause}"
        
        print(f"Executing: {query}") # For debugging and user confirmation
        # Confirmation step (optional but recommended for destructive operations)
        # confirm = input("Proceed with this update? (yes/no): ")
        # if confirm.lower() != 'yes':
        #     print("Update cancelled.")
        #     return 0

        # Assuming execute_query handles DML and returns a list with a dict like [{'affected_rows': N}]
        # or None on error.
        results = self.execute_query(query) 

        if results is None:
            # Error message should have been printed by execute_query
            return 1 
        
        affected_rows = results[0].get('affected_rows', 0)
        print(f"Update successful. {affected_rows} row(s) affected.")
        return 0 # Success status

    def complete(self, current_path: list, args: list, current_word: str) -> list:
        suggestions = []
        if not current_path:
            return suggestions

        table_name = current_path[0]
        if table_name not in self.columns:
            return suggestions

        # Suggest column names for assignment if table is selected
        # e.g., "set na" -> "set name="
        #      "set name=John ag" -> "set name=John age="
        
        # Check if current_word is the start of a new assignment or part of a value
        # This basic completion won't handle complex value suggestions.
        
        # If current_word is empty or contains '=', we are likely starting a new column or finishing one.
        # We should suggest columns not yet in args.
        
        # Get columns already used in args
        used_columns = set()
        for arg in args:
            if '=' in arg:
                used_columns.add(arg.split('=', 1)[0].strip())

        if '=' not in current_word: # User is typing a column name
            for col in self.columns[table_name]:
                if col.startswith(current_word) and col not in used_columns:
                    suggestions.append(col + "=")
        # else: User is typing a value after '=', could suggest column values, but that's complex.
        
        return suggestions
