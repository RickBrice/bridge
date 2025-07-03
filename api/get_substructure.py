import ifcopenshell
from ifcopenshell import entity_instance
import bridge.api

def get_substructure(the_bridge:entity_instance)->entity_instance:
    substructure=None
    for part in the_bridge.IsDecomposedBy[0].RelatedObjects:
        if part.PredefinedType == "SUBSTRUCTURE":
            substructure = part
            break

    return substructure