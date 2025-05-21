# python_cli_wrapper/cli_helper.py
import shutil

def pretty_print(values: list[dict], delim: str = ' ', min_col_width: int = 0, 
                 column_options: dict = None, legend_interval: int = 50,
                 max_col_width: int = 60):
    if not values:
        return

    if column_options is None:
        column_options = {}

    if not values or not isinstance(values[0], dict):
        # print("Error: pretty_print expects a non-empty list of dictionaries.")
        return 
    
    headers = list(values[0].keys())

    data_to_print = []
    legend_row_content = {key: key for key in headers} 

    if legend_interval > 0 and len(values) >= legend_interval: # Only add legends if there's enough data
        current_data_idx = 0
        for row in values:
            if current_data_idx > 0 and current_data_idx % legend_interval == 0:
                data_to_print.append(legend_row_content)
            data_to_print.append(row)
            current_data_idx += 1
    else:
        data_to_print = list(values)

    col_widths = {key: max(min_col_width, len(str(key))) for key in headers}

    for row in data_to_print:
        for key in headers:
            col_widths[key] = max(col_widths[key], len(str(row.get(key, ''))))
            if max_col_width > 0:
                col_widths[key] = min(col_widths[key], max_col_width)
    
    for row in data_to_print:
        line_parts = []
        for key in headers:
            val = str(row.get(key, ''))
            width = col_widths[key]
            
            if len(val) > width: # Truncate if value exceeds calculated width
                val = val[:width-3] + "..." if width > 3 else val[:width]
            
            pad_type = 'ljust' 
            if column_options.get(key) == 'rjust': # Explicit option
                pad_type = 'rjust'
            elif not val.isalpha() and val.replace('.', '', 1).strip().replace('-', '', 1).isdigit(): # Numeric check
                pad_type = 'rjust'
            
            line_parts.append(getattr(val, pad_type)(width))

        line = delim.join(line_parts)
        
        is_legend_display_row = (legend_interval > 0 and row == legend_row_content)
        
        if is_legend_display_row : 
             print(f"\033[40m\033[1;37m{line}\033[0m") 
        else:
             print(line)

def is_integer(input_val):
    return str(input_val).isdigit()
