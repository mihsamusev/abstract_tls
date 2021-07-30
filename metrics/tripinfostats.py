
from xml.etree.ElementTree import Element


def personinfo_to_dict(child: Element) -> dict:
    """
    Convers <personinfo> to dict only including walk tag
    """
    ped_data = child.attrib
    walk_element = child.find("walk")
    walk_data = {} if walk_element is None else walk_element.attrib
    ped_data.update(walk_data)
    return ped_data

def tripinfo_to_dict(child: Element) -> dict:
    """
    Convers <tripinfo> to dict info, includes emissions
    """
    trip_data = child.attrib
    emit_element = child.find("emissions")
    emit_data = {} if emit_element is None else emit_element.attrib 
    trip_data["emissions"] = emit_data
    return trip_data

def get_all_personinfos(root: Element) -> dict:
    """
    Converts tripinfo xml ElementTree list of person info dicts
    """
    result = []
    for child in root:
        if child.tag == "personinfo":
            d = personinfo_to_dict(child)
            result.append(d)
    return result


def get_all_tripinfos(root: Element) -> dict:
    """
    Converts tripinfo xml ElementTree list of trip info dicts
    """
    result = []
    for child in root:
        if child.tag == "tripinfo":
            d = tripinfo_to_dict(child)
            result.append(d)
    return result
