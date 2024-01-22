#!/usr/bin/env python
import fileinput
import csv
import sys
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)
csv.field_size_limit(sys.maxsize)

def is_insert(line):
    return line.startswith('INSERT INTO')

def get_columns_and_values(line):
    # Extracting the columns and values from the INSERT statement
    columns_start = line.index('(') + 1
    columns_end = line.index(') VALUES')
    columns = line[columns_start:columns_end].strip().split(', ')
    
    values_start = line.index('VALUES (') + len('VALUES (')
    values_end = line.rindex(');')
    values = line[values_start:values_end].split(', ')
    
    return columns, values

def values_sanity_check(values):
    assert values
    # Add additional checks if needed
    return True

def parse_values(line, outfile):
    columns, values = get_columns_and_values(line)
    
    if not values_sanity_check(values):
        raise Exception("Sanity check for SQL INSERT values failed!")

    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    
    if not hasattr(parse_values, 'header_written') or not parse_values.header_written:
        # Write header only if it hasn't been written before
        writer.writerow(columns)
        parse_values.header_written = True
    
    # Remove single quotes from values before writing
    values = [v.strip("'") for v in values]
    
    writer.writerow(values)   # Write values

def main():
    try:
        lines = []
        for line in fileinput.input():
            if is_insert(line):
                # If it's an INSERT statement, process it
                parse_values(line.strip(), sys.stdout)
            else:
                # If it's a continuation of a multi-line statement, accumulate the lines
                lines.append(line.strip())
                if lines[-1].endswith(';'):
                    # If the current line ends with a semicolon, process the accumulated lines
                    parse_values(' '.join(lines), sys.stdout)
                    lines = []
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
