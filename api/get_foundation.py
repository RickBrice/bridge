import ifcopenshell
from ifcopenshell import entity_instance
import bridge.api

def get_foundation(the_bridge:entity_instance,index:int)->entity_instance:
    pier = bridge.api.get_pier(the_bridge,index)
    foundation = pier.IsDecomposedBy[0].RelatedObjects[0]
    return foundation


