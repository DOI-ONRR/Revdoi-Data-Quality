""" Mostly for naming the config files """
def get_data_type(name):
    type = ""
    lower = name.lower()
    if "cy" in lower:
        type += "cy"
    elif "fy" in lower:
        type += "fy"
    elif "month" in lower:
        type += "m"

    if "company" in lower:
        type += "com"
    if "fed" in lower:
        type += "fed"
    elif "native" in lower:
        type += "na"

    if "product" in lower:
        type += "p"
    elif "rev" in lower:
        type += "r"
    elif "disburse" in lower:
        type += "d"

    return type + "_"

""" Returns a list of the split string based on item and unit """
def split_unit(string):
    string = str(string)
    # For general purpose commodities
    if "(" in string:
        split = string.rsplit(" (",1)
        split[1] = split[1].rstrip(")")
        return split
    # The comma is for Geothermal
    elif "," in string:
        return string.split(", ",1)
    # In case no unit is found
    return [string,'']

""" Adds key to dictionary if not present. Else adds value to key set.
Keyword arguements:
key -- Key entry for the dict, e.g. A commodity
value -- Value entry corresponding to key, e.g. Unit or Value
dictionary -- Reference to dictionary
"""
def add_item(key, value, dictionary):
    # Adds Value to Set if Key exists
    if key in dictionary:
        dictionary[key].add(value)
    # Else adds new key with value
    else:
        dictionary[key] = {value}

# Being reworked
def get_com_pro(col):
    if not col.contains("Product") and not col.contains("Commodity"):
        return "n/a"
    if col.contains("Product"):
        if col.contains("Commodity"):
            return"n/a"
        else:
            return "Product"
    return "Commodity"
