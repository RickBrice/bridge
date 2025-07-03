import ifcopenshell
from ifcopenshell import entity_instance

def _extruded_solid(file:ifcopenshell.file,length:float,width:float,height:float,dx:float=0.,dy:float=0.,dz:float=0.)->entity_instance:
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        XDim = width,
        YDim = length
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        Position=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint((dx,dy,dz))
            ),
        ExtrudedDirection=file.createIfcDirection((0.,0.,1.)),
        Depth=height
    )
    return solid

def _polygon_solid(file:ifcopenshell.file,length:float,width:float,height:float,dx:float=0.,dy:float=0.,dz:float=0.)->entity_instance:
    point_list = file.createIfcCartesianPointList3D(CoordList=[
        (dx-width/2,dy+length/2,dz+0),
        (dx-width/2,dy-length/2,dz+0),
        (dx+width/2,dy-length/2,dz+0),
        (dx+width/2,dy+length/2,dz+0),
        (dx-width/2,dy+length/2,dz+height),
        (dx-width/2,dy-length/2,dz+height),
        (dx+width/2,dy-length/2,dz+height),
        (dx+width/2,dy+length/2,dz+height)
        ]
    )
    faces = [
        file.createIfcIndexedPolygonalFace(CoordIndex=[1,2,6,5]),
        file.createIfcIndexedPolygonalFace(CoordIndex=[6,2,3,7]),
        file.createIfcIndexedPolygonalFace(CoordIndex=[7,3,4,8]),
        file.createIfcIndexedPolygonalFace(CoordIndex=[8,4,1,5]),
        file.createIfcIndexedPolygonalFace(CoordIndex=[1,4,3,2]),
        file.createIfcIndexedPolygonalFace(CoordIndex=[6,7,8,5]),
    ]
    solid = file.createIfcPolygonalFaceSet(
        Coordinates=point_list,
        Closed=True,
        Faces=faces
    )
    return solid


def _sectioned_solid_horizontal(file:ifcopenshell.file,length:float,width:float,height:float,dx:float=0.,dy:float=0.,dz:float=0.)->entity_instance:
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        Position=file.createIfcAxis2Placement2D(Location=file.createIfcCartesianPoint((0.,height/2))),
        XDim = width,
        YDim = height
    )
    directrix = file.createIfcPolyline(
        Points=[file.createIfcCartesianPoint((0.,-length/2,0.)),file.createIfcCartesianPoint((0.,length/2,0.))]
    )
    solid = file.createIfcSectionedSolidHorizontal(
        Directrix=directrix,
        CrossSections=[profile,profile],
        CrossSectionPositions=[
            file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(0.),
                OffsetLateral=-dx, # positive is to the left of the directrix, we mean positive dx to be ahead on station, which means it is to the right of the directrix
                OffsetVertical=dz,
                #OffsetLongitudinal=dy,
                BasisCurve=directrix)),
            file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(length),
                OffsetLateral=-dx,
                OffsetVertical=dz,
                #OffsetLongitudinal=dy,
                BasisCurve=directrix))
        ]
    )
    return solid

def _extruded_area_solid(file:ifcopenshell.file,pier:entity_instance,footing_length:float,footing_width:float,footing_height:float,wall_length:float,wall_width:float,wall_height:float,wall_offset:float,placement:entity_instance)->list[entity_instance]:
    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    # Build Footing
    footing_rep = _extruded_solid(file,footing_length,footing_width,footing_height)
    footing = file.createIfcFooting(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Axis",
                RepresentationType="SweptSolid",
                Items=[footing_rep]
            )]
        ),
        PredefinedType="STRIP_FOOTING"
        )

    # Build Wall
    wall_rep = _extruded_solid(file,wall_length,wall_width,wall_height,dx=wall_offset,dz=footing_height)

    wall = file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Axis",
                RepresentationType="SweptSolid",
                Items=[wall_rep]
            )]
            ),
        PredefinedType = "SOLIDWALL"
        )
    
    return footing, wall

def _polygon_face_set(file:ifcopenshell.file,pier:entity_instance,footing_length:float,footing_width:float,footing_height:float,wall_length:float,wall_width:float,wall_height:float,wall_offset:float,placement:entity_instance):
    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    # Build Footing
    footing_rep = _polygon_solid(file,footing_length,footing_width,footing_height)
    footing = file.createIfcFooting(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Body",
                RepresentationType="Tessellation",
                Items=[footing_rep]
            )]
        ),
        PredefinedType="STRIP_FOOTING"
        )

    # Build Wall
    wall_rep = _polygon_solid(file,wall_length,wall_width,wall_height,dx=wall_offset,dz=footing_height)

    wall = file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Body",
                RepresentationType="Tessellation",
                Items=[wall_rep]
            )]
            ),
        PredefinedType = "SOLIDWALL"
        )
    
    return footing, wall


def _sectioned_solid(file:ifcopenshell.file,pier:entity_instance,footing_length:float,footing_width:float,footing_height:float,wall_length:float,wall_width:float,wall_height:float,wall_offset:float,placement:entity_instance)->list[entity_instance]:
    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    # Build Footing
    footing_rep = _sectioned_solid_horizontal(file,footing_length,footing_width,footing_height)
    footing = file.createIfcFooting(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Body",
                RepresentationType="AdvancedSweptSolid",
                Items=[footing_rep]
            )]
        ),
        PredefinedType="STRIP_FOOTING"
        )

    # Build Wall
    wall_rep = _sectioned_solid_horizontal(file,wall_length,wall_width,wall_height,dx=wall_offset,dz=footing_height)

    wall = file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Body",
                RepresentationType="AdvancedSweptSolid",
                Items=[wall_rep]
            )]
            ),
        PredefinedType = "SOLIDWALL"
        )
    
    return footing, wall


def create_stub_abutment(file:ifcopenshell.file,pier:entity_instance,foundation:entity_instance,footing_length:float,footing_width:float,footing_height:float,wall_length:float,wall_width:float,wall_height:float,wall_offset:float,placement:entity_instance):
    """
    Creates a simple stub abutment consisting of a rectangular footing and stem wall.
    The abutment is positions based on the bottom center point of the footing.
    The resulting IfcWall is assigned to the spatial structure of the pier.
    The resulting IfcFooting is assigned to the spatial structure of the foundation.

    :param pier: The IfcBridgePart.PIER where the abutment occurs
    :param foundation: The IfcBridgePart.FOUNDATION where the footing occurs
    :param footing_length: Length of the footing measured transversely to the bridge
    :param footing_width: Width of the footing measured longitudinally to the bridge
    :param footing_height: Height (or depth) of the footing
    :param wall_length: Length of the stem wall
    :param wall_width:  Width (or thickness) of the stem wall
    :param wall_height: Height of the stem wall above the top of the footing
    :param wall_offset: Offset of the centerline of the wall from the centerline of the footing. Positive values places the wall ahead on station relative to the centerline of the footing.
    :param placement: Placement of the bottom centerline point of the footing
    """

    # Implementation note: There are three methods implemented for creating the geometric representation of the abutment.
    # IfcExtrudedAreaSolid is (currently) not in the Alignment-based View, so it should not be used
    #footing,wall = _extruded_area_solid(file,pier,footing_length,footing_width,footing_height,wall_length,wall_width,wall_height,wall_offset,placement)
    footing,wall = _polygon_face_set(file,pier,footing_length,footing_width,footing_height,wall_length,wall_width,wall_height,wall_offset,placement)
    #footing,wall = _sectioned_solid(file,pier,footing_length,footing_width,footing_height,wall_length,wall_width,wall_height,wall_offset,placement)

    ifcopenshell.api.spatial.assign_container(file,products=[wall],relating_structure=pier)
    ifcopenshell.api.spatial.assign_container(file,products=[footing],relating_structure=foundation)
