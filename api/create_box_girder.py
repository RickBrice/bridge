import ifcopenshell
import ifcopenshell.api.aggregate
from ifcopenshell import entity_instance


def create_box_girder(file:ifcopenshell.file,superstructure:entity_instance,directrix:entity_instance,start:float,length:float,w1:float,w2:float,w3:float,h1:float,h2:float,h3:float,placement:entity_instance)->entity_instance:
    """
    """

    points = [
        file.createIfcCartesianPoint((w1/2,0.)),
        file.createIfcCartesianPoint((w1/2,-h1)),
        file.createIfcCartesianPoint((w1/2 - w2,-h1 - h2)),
        file.createIfcCartesianPoint((w1/2 - w2 - w3, -h1 - h2 - h3)),

        file.createIfcCartesianPoint((-w1/2 + w2 + w3, -h1 - h2 - h3)),
        file.createIfcCartesianPoint((-w1/2 + w2,-h1 - h2)),
        file.createIfcCartesianPoint((-w1/2,-h1)),
        file.createIfcCartesianPoint((-w1/2,0.)),
    ]

    profile = file.createIfcArbitraryClosedProfileDef(
        ProfileType="AREA",
        OuterCurve=file.createIfcPolyline(points)
    )

    lp_start = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(start),
                BasisCurve=directrix))

    lp_end = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(length),
                BasisCurve=directrix))
    
    solid = file.createIfcSectionedSolidHorizontal(
        Directrix=directrix,
        CrossSections=[profile,profile],
        CrossSectionPositions=[lp_start, lp_end]
    )

    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    girder = file.createIfcBeam(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
        Representations=[file.createIfcShapeRepresentation(
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="AdvancedSweptSolid",
            Items=[solid]
            )]
        ),
        PredefinedType = "BEAM"
        )

    #ifcopenshell.api.aggregate.assign_object(file,products=[girder],relating_object=superstructure)
    ifcopenshell.api.spatial.assign_container(file,products=[girder],relating_structure=superstructure)