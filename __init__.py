# ----------------------------------------------
# Define Addon info
# ----------------------------------------------

import site
from bpy.props import IntProperty, PointerProperty
import bpy

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
# Import packages
# ----------------------------------------------

# If bpy is imported, then it is not the first import,
# and ui and operator need to be reloaded
if "bpy" in locals():
    import importlib
    importlib.reload(constants)
    importlib.reload(operator)
    importlib.reload(ui)
else:
    from . import constants
    from . import operator
    from . import ui


# Add custom virtual environment
site.addsitedir(r'C:\Users\lucas\Desktop\New folder\venv\Lib\site-packages')

# ----------------------------------------------
# Register panels, operators and properties
# ----------------------------------------------

classes = (
    ui.OSRSMC_PT_Panel_Load_Model,
    ui.OSRSMC_PT_Panel_Merge_Materials,
    ui.OSRSMC_UL_Materials_List,
    operator.OSRSMC_OT_Load_Model,
    operator.OSRSMC_OT_Merge_Materials
)

props = [
    ("osrs_model", PointerProperty(name="Target", type=bpy.types.Object)),
    ('max_n_clusters', IntProperty(name='Max Clusters',
     min=constants.min_clusters, default=20))
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
