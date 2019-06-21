def get_data_type(name):
    type = ""
    if "federal" in name:
        type += "f"
    if "production" in name:
        type += "p"
    elif "revenue" in name:
        type += "r"
    return type

# Returns Split String based on Commodity and Unit
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


def add_item(key, value, dictionary):
    # Adds Value to Set if Key exists
    if key in dictionary:
        dictionary[key].add(value)
    # Else adds new key with value
    else:
        dictionary[key] = {value}

# Returns Product if present else returns Commodity
def get_com_pro(col):
    if col.contains("Product"):
        return "Product"
    return "Commodity"
