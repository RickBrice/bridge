import ifcopenshell
from ifcopenshell import entity_instance

def _column(file:ifcopenshell.file,length:float,diameter:float,bottom:float,offset:float)->entity_instance:
    profile = file.createIfcCircleProfileDef(
        ProfileType="AREA",
        Radius = diameter/2.
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        Position=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint((0.,offset,bottom))
        ),
        ExtrudedDirection=file.createIfcDirection((0.,0.,1.)),
        Depth=length
    )
    return solid


def _footing(file:ifcopenshell.file,length:float,width:float,height:float,offset:float)->entity_instance:
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        XDim = width,
        YDim = length
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        Position=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint((0.,offset,0.))
        ),
        ExtrudedDirection=file.createIfcDirection((0.,0.,1.)),
        Depth=height
    )
    return solid


def _cap(file:ifcopenshell.file,length:float,width:float,height:float,bottom:float)->entity_instance:
    profile = file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        XDim = width,
        YDim = length
    )
    solid = file.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        Position=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint((0.,0.,bottom))
        ),
        ExtrudedDirection=file.createIfcDirection((0.,0.,1.)),
        Depth=height
    )
    return solid

def create_pier(file:ifcopenshell.file,pier:entity_instance,foundation:entity_instance,cap_length:float,cap_width:float,cap_height:float,nColumns:int,column_height:float,column_diameter:float,column_spacing:float,footing_length:float,footing_width:float,footing_height:float,placement:entity_instance):
    """
    Creates a simple pier
    """

    context = ifcopenshell.util.representation.get_context(file, context="Model", subcontext="Axis", target_view="MODEL_VIEW")

    columns=[]
    footings=[]
    for i in range(nColumns):
        offset = i*column_spacing - (nColumns - 1)*column_spacing/2

        column_rep = _column(file,column_height,column_diameter,footing_height,offset)
        column = file.createIfcColumn(
            GlobalId=ifcopenshell.guid.new(),
            ObjectPlacement=placement,
            Representation=file.createIfcProductDefinitionShape(
                Representations=[file.createIfcShapeRepresentation(
                    ContextOfItems=context,
                    RepresentationIdentifier="Axis",
                    RepresentationType="SweptSolid",
                    Items=[column_rep]
                )]
            ),
            PredefinedType="PIERSTEM"
            )
        columns.append(column)

        footing_rep = _footing(file,footing_length,footing_width,footing_height,offset)
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
            PredefinedType="PAD_FOOTING"
            )
        footings.append(footing)

    cap_rep = _cap(file,cap_length,cap_width,cap_height,footing_height+column_height)
    cap = file.createIfcBeam(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=file.createIfcProductDefinitionShape(
            Representations=[file.createIfcShapeRepresentation(
                ContextOfItems=context,
                RepresentationIdentifier="Axis",
                RepresentationType="SweptSolid",
                Items=[cap_rep]
            )]
        ),
        PredefinedType="PIERCAP"
        )

    ifcopenshell.api.spatial.assign_container(file,products=[cap],relating_structure=pier)
    ifcopenshell.api.spatial.assign_container(file,products=columns,relating_structure=pier)
    ifcopenshell.api.spatial.assign_container(file,products=footings,relating_structure=foundation)
