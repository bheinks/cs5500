DEBUG = False

class SymbolTable:
    def __init__(self):
        # Represented as a dictionary
        self.table = {}

    # Add a new entry to the symbol table
    def add(self, name, var_type, bounds, base_type, label, level):
        if DEBUG:
            print(f'\n+++ Adding {name} to symbol table with type {var_type}', end='')

            # If array
            if bounds and base_type:
                print(' {} .. {} OF {}'.format(*bounds, base_type))
            else:
                print()
            
        # If symbol is already defined in table
        if name in self.table:
            return None

        entry = Entry(name, var_type, bounds, base_type, label, level)
        self.table[name] = entry

        return entry

    def get(self, ident):
        return self.table.get(ident)

    def print_all(self):
        for ident, entry in self.table.items():
            print(entry.__dict__)


# Symbol table entry
class Entry:
    def __init__(self, name, var_type, bounds, base_type, label, level):
        self.name = name
        self.var_type = var_type
        self.bounds = bounds
        self.base_type = base_type
        self.label = label
        self.level = level
