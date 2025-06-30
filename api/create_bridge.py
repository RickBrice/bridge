import ifcopenshell
from ifcopenshell import entity_instance

def create_bridge(file:ifcopenshell.file,nspans:int)->entity_instance:
    """
    bridge---agg-+-deck
                 +-superstructure---agg---girder
                 +-substructure---agg-+-pier
                                      +-foundation
    """
    bridge = file.createIfcBridge(GlobalId=ifcopenshell.guid.new(),Name="Bridge",PredefinedType="GIRDER")
    deck = file.createIfcBridgePart(GlobalId=ifcopenshell.guid.new(),Name="Deck",PredefinedType="DECK",CompositionType="COMPLEX",UsageType="LONGITUDINAL")
    superstructure = file.createIfcBridgePart(GlobalId=ifcopenshell.guid.new(),Name="Superstructure",PredefinedType="SUPERSTRUCTURE",CompositionType="PARTIAL",UsageType="LONGITUDINAL")
    substructure = file.createIfcBridgePart(GlobalId=ifcopenshell.guid.new(),Name="Substructure",PredefinedType="SUBSTRUCTURE",CompositionType="PARTIAL",UsageType="LONGITUDINAL")
    piers = []
    foundations = []
    for s in range(nspans+1):
        pier = file.createIfcBridgePart(GlobalId=ifcopenshell.guid.new(),Name=f"Pier {s+1}",PredefinedType="PIER",CompositionType="COMPLEX",UsageType="LONGITUDINAL")
        foundation = file.createIfcBridgePart(GlobalId=ifcopenshell.guid.new(),Name=f"Foundation {s+1}",PredefinedType="FOUNDATION",CompositionType="COMPLEX",UsageType="LONGITUDINAL")
        piers.append(pier)
        foundations.append(foundation)
        ifcopenshell.api.aggregate.assign_object(file,products=[foundation],relating_object=pier)

    piers[0].Name = "Abutment 1"
    piers[0].PredefinedType = "ABUTMENT"
    piers[-1].Name = f"Abutment {len(piers)}"
    piers[-1].PredefinedType = "ABUTMENT"

    ifcopenshell.api.aggregate.assign_object(file,products=piers,relating_object=substructure)
    ifcopenshell.api.aggregate.assign_object(file,products=[deck,superstructure,substructure],relating_object=bridge)
    return bridge
