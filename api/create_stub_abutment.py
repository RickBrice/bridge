import ifcopenshell
from ifcopenshell import entity_instance

def create_stub_abutment(file:ifcopenshell.file,pier:entity_instance,footing_length:float,footing_width:float,footing_height:float,wall_length:float,wall_width:float,wall_height:float,wall_offset:float,placement:entity_instance):
    """
    Creates a simply stub abutment.
    """
    # Build Footing
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        XDim = footing_width,
        YDim = footing_length
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        ExtrudedDirection=file.createIfcDirection((0.0,0.0,1.0)),
        Depth=footing_height
    )

    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    footing = file.createIfcFooting(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Axis",
                RepresentationType="SweptSolid",
                Items=[solid]
            )]
        ),
        PredefinedType="STRIP_FOOTING"
        )

    # Build Wall
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        XDim = wall_width,
        YDim = wall_length
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        Position=file.createIfcAxis2Placement3D( # this positions the rectangle to be extruded "wall_offset" from CL Footing and at the top of the footing
            Location=file.createIfcCartesianPoint((wall_offset,0.0,footing_height))
            ),
        ExtrudedDirection=file.createIfcDirection((0.0,0.0,1.0)),
        Depth=wall_height
    )

    wall = file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Axis",
                RepresentationType="SweptSolid",
                Items=[solid]
            )]
            ),
        PredefinedType = "SOLIDWALL"
        )
    
    foundation = pier.IsDecomposedBy[0].RelatedObjects[0]

    ifcopenshell.api.spatial.assign_container(file,products=[wall],relating_structure=pier)
    ifcopenshell.api.spatial.assign_container(file,products=[footing],relating_structure=foundation)
