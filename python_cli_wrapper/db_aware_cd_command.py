# python_cli_wrapper/db_aware_cd_command.py
from .db_command_base import DbCommandBase
from .cli_helper import is_integer # Assuming is_integer is in cli_helper.py

class DbAwareCdCommand(DbCommandBase):
    def __init__(self, db_config: dict):
        super().__init__(db_config)

    def command(self, current_path: list, args: list) -> int:
        # current_path is passed by reference (it's a list) and modified directly.
        # args is the list of arguments from the command line, e.g., ["users"] or ["id=1"]
        
        if not self.connection:
            print("Error: No database connection for 'cd' command.")
            # Fallback to a simpler non-db cd? Or just fail?
            # For now, let's assume it shouldn't be called if no DB.
            return -1 # Indicate error or undefined state

        original_path = list(current_path) # Make a copy to revert if validation fails

        if not args: # 'cd' with no arguments
            # In PHP, 'cd' with no args wasn't explicitly handled by Pdo/CdCommand,
            # but Cli.php's default behavior for unknown cmd was 'cd' + args.
            # An empty 'cd' might mean 'go to root' or 'show current path info'.
            # Let's make it go to root.
            current_path.clear()
            return self.count(current_path) if current_path else 0 # Count for root might be 0 or special

        target_arg_str = " ".join(args) # e.g. "users", "id=1", "items/category='electronics'"
        
        if target_arg_str == ".":
            # No change, but we should still return the count of the current path
            return self.count(current_path)

        if target_arg_str == "..":
            if current_path:
                current_path.pop()
            return self.count(current_path)

        if target_arg_str == "/":
            current_path.clear()
            # What should count return for an empty path? PdoCliCommand.count returns 0 if path is empty.
            return 0 # Or self.count([]) which should be 0 based on DbCommandBase

        # Case: 'cd table_name' (and path is currently empty or at root)
        # The PHP version: case (in_array($c,$this->tables) && count(explode('/',$full))<2):
        #                    if(count($path) == 0) array_push($path,$c);
        is_simple_table_nav = len(target_arg_str.split('/')) < 2
        if is_simple_table_nav and target_arg_str in self.tables:
            if not current_path: # If at root
                current_path.append(target_arg_str)
                return self.count(current_path)
            else: # If already in a path, this might be more complex or an error
                  # PHP version didn't explicitly handle 'cd existing_table' when already in a path.
                  # Let's treat it as trying to switch to a root table.
                current_path.clear()
                current_path.append(target_arg_str)
                return self.count(current_path)


        # Default behavior for other arguments (e.g., conditions, multi-part paths)
        # PHP: $c = implode(' ',$cmds); $parts = explode('/',$c);
        #      if(\CliWrapper\CliHelper::isInteger($c)) $c = "id=$c";
        #      if(count($parts)>1) { foreach($parts as $part) $path[] = trim($part); }
        #      else if(count($path) > 0) array_push($path, $c);
        #      else echo "Table '$c' not found
";
        
        new_path_elements = [part.strip() for part in target_arg_str.split('/') if part.strip()]

        # If the target is an absolute path, clear current_path first
        # This was not explicitly in the original PHP for this part of logic, but good for robustness
        if target_arg_str.startswith('/'):
            current_path.clear()
            # new_path_elements will correctly contain the segments of the absolute path

        for i, element in enumerate(new_path_elements):
            # If we are in a table context (path is not empty) and element is an integer,
            # and it's the first new element being added to an existing path.
            if current_path and i == 0 and is_integer(element) and '=' not in element:
                current_path.append(f"id={element}")
            else:
                current_path.append(element)
        
        # Validate the new path by trying to count records
        # PHP: if($this->count($path) == -1) $path = $savedpath;
        # The count method in DbCommandBase returns -1 on error (e.g., bad query)
        path_validity_count = self.count(current_path)
        if path_validity_count == -1:
            # Invalid path, revert
            current_path[:] = original_path # Restore original path content
            print(f"Error: Path '/{' / '.join(current_path)}' is not valid or leads to an error.")
            # Return count of the original (still current) path
            return self.count(current_path) # Align with subtask: removed "if current_path else 0"
        
        return path_validity_count # Return the count of the new valid path

    def complete(self, current_path: list, args: list, current_word: str) -> list:
        # PHP: if(count($path) == 0){ return $this->tables; }
        #      else { return $this->colums[$path[0]]; }
        
        # args here are parts of the 'cd' argument itself, current_word is the part being typed
        # Example: cd users/em -> current_word is 'em'
        #          cd us -> current_word is 'us'
        
        line_buffer = " ".join(args) # Reconstruct what's been typed for 'cd' command so far
        if '/' not in line_buffer and not current_path : # Typing table name at root
             return [table for table in self.tables if table.startswith(current_word)]

        # If we have a table in path, or are typing a path segment for a table:
        table_context = ""
        if current_path:
            table_context = current_path[0]
        elif '/' in line_buffer:
            table_context = line_buffer.split('/')[0]
        
        if table_context and table_context in self.columns:
            # Suggest columns for conditions, e.g., "cd users/em" -> "email="
            # Or parts of conditions "cd users/status='ac" -> "active'" (more complex)
            # For now, just suggest column names if after a '/' or if completing a condition part
            
            parts = line_buffer.split('/')
            last_segment = parts[-1] # current_word is typically the last_segment if not empty

            if current_word == "" and line_buffer.endswith("/"): # After a slash, suggest columns
                 return [col + "=" for col in self.columns.get(table_context, [])]
            
            # User is typing a column name for a condition
            # current_word is what's being completed. last_segment is the whole segment.
            # e.g. line_buffer="users/emai", current_word="emai", last_segment="emai"
            if '=' not in last_segment: # Check last_segment for an existing '='
                return [col + "=" for col in self.columns.get(table_context, []) if col.startswith(current_word)]
            # else: User is typing a value, too complex for now.

        # Default: if no path, suggest tables
        if not current_path and '/' not in line_buffer:
            return [table for table in self.tables if table.startswith(current_word)]
            
        return []

```
