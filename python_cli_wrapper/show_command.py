# python_cli_wrapper/show_command.py
from .db_command_base import DbCommandBase
from .cli_helper import pretty_print

class ShowCommand(DbCommandBase):
    def __init__(self, db_config: dict):
        super().__init__(db_config)

    def command(self, current_path: list, args: list) -> int:
        if not self.connection:
            print("Error: No database connection.")
            return 1
        
        if not current_path:
            print("Error: No table selected. Use 'cd tablename'.")
            return 1

        table_name = current_path[0]
        if table_name not in self.tables:
            print(f"Error: Table '{table_name}' not found.")
            return 1

        # Option 1: Describe the table (most common for a 'show table' command)
        if len(current_path) == 1: 
            # This is equivalent to DESCRIBE table_name
            query = f"DESCRIBE `{table_name}`"
            results = self.execute_query(query)

            if results is None:
                print(f"Failed to describe table '{table_name}'.")
                return 1
            if not results:
                print(f"No information found for table '{table_name}'.")
                return 0
            
            # Convert all values in results to strings for pretty_print
            string_results = []
            for row_dict in results:
                str_row = {key: str(value) if value is not None else "" for key, value in row_dict.items()}
                string_results.append(str_row)
            
            print(f"Schema for table '{table_name}':")
            pretty_print(string_results)
            return 0

        # Option 2: Show specific row(s) if path is deeper (e.g., /table/id_value or /table/column=value)
        # This makes 'show' behave somewhat like 'list' but potentially for a specific record.
        # The original PHP ListCommand used current_path for table and args for columns.
        # The PHP PdoCliCommand.buildQuery used path for table AND conditions.
        # Let's assume 'show' with a path deeper than table name means "show rows matching path conditions".
        else:
            conditions = current_path[1:]
            # We need to select all columns for a 'show' command on specific rows
            # If self.columns[table_name] is available and accurate
            if table_name in self.columns and self.columns[table_name]:
                cols_str = ", ".join([f"`{col}`" for col in self.columns[table_name]])
            else: # Fallback if column list isn't populated for some reason
                cols_str = "*"
            
            query = self.build_query(f"SELECT {cols_str}", current_path) # build_query uses path for table and WHERE
            
            # print(f"Executing: {query}") # For debugging - Commented out for cleaner output
            results = self.execute_query(query)

            if results is None:
                # Error message already printed by execute_query
                return 1
            if not results:
                print(f"No records found in '{table_name}' matching path '/{' / '.join(conditions)}'.")
                return 0

            string_results = []
            for row_dict in results:
                str_row = {}
                for col_name in row_dict: # Iterate over actual keys in the result
                    val = row_dict.get(col_name)
                    if isinstance(val, bytes):
                        try:
                            str_row[col_name] = val.decode('utf-8')
                        except UnicodeDecodeError:
                            str_row[col_name] = '[blob]'
                    else:
                        str_row[col_name] = str(val) if val is not None else ""
                string_results.append(str_row)
            
            pretty_print(string_results)
            return 0

    def complete(self, current_path: list, args: list, current_word: str) -> list:
        # Completion for 'show' could suggest column names if path is 'table_name/column_condition_prefix'
        # Or table names if path is empty or just '/'
        # For now, let's keep it simple: if a table is selected, suggest its columns for further path elements.
        if len(current_path) == 1:
            table_name = current_path[0]
            if table_name in self.columns:
                # Suggest columns for path-based filtering, e.g., "show users/na" -> "users/name="
                # Adding '=' makes it easier for user to start typing value
                return [col + "=" for col in self.columns[table_name] if col.startswith(current_word)]
        # If path is deeper, could suggest values based on column type, but that's complex.
        return []
