# ----------------------------------------------
# Define Addon info
# ----------------------------------------------

bl_info = {
    "name": "osrs_model_cleaner",
    "author": "Lucas Davey",
    "description": "",
    "blender": (3, 4, 0),
    "version": (0, 0, 1),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

# ----------------------------------------------
# Install packages if not yet installed
# ----------------------------------------------

functions.installPackage("scikit-learn")

# ----------------------------------------------
# Import modules
# ----------------------------------------------

# If bpy is in local, this is not the initial import
# and we need to reload submodules
if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(operator)
else:
    import bpy
    from bpy.props import PointerProperty
    from . import ui
    from . import operator
    from . import functions

# ----------------------------------------------
# Register panels, operators and properties
# ----------------------------------------------

classes = (
    ui.OSRSMC_PT_Panel_Load_Model,
    ui.OSRSMC_PT_Panel_Merge_Materials,
    operator.OSRSMC_OT_Load_Model,
    operator.OSRSMC_OT_Merge_Materials
)

props = [
    ("osrs_model",
     PointerProperty(name="OSRS Model", type=bpy.types.Object))
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    for (prop_name, prop_value) in props:
        setattr(bpy.types.Scene, prop_name, prop_value)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    for (prop_name, _) in props:
        delattr(bpy.types.Scene, prop_name)
