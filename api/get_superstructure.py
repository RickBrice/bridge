import ifcopenshell
from ifcopenshell import entity_instance
import bridge.api

def get_superstructure(the_bridge:entity_instance)->entity_instance:
    superstructure=None
    for part in the_bridge.IsDecomposedBy[0].RelatedObjects:
        if part.PredefinedType == "SUPERSTRUCTURE":
            superstructure = part
            break

    return superstructure