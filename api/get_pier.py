import ifcopenshell
from ifcopenshell import entity_instance
import bridge.api

def get_pier(the_bridge:entity_instance,index:int)->entity_instance:
    substructure = bridge.api.get_substructure(the_bridge)
    count = 0
    for part in substructure.IsDecomposedBy[0].RelatedObjects:
        if part.PredefinedType == "ABUTMENT" or part.PredefinedType == "PIER":
           if count == index:
               return part
           else:
               count += 1
    
    return None 
