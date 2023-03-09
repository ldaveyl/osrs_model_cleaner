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

# If bpy is already imported it is not the first import
# and modules need to be reloaded
if "bpy" in locals():
    import importlib
    importlib.reload(constants)
    importlib.reload(functions)
    importlib.reload(operator)
    importlib.reload(ui)
else:
    from . import constants
    from . import functions
    from . import operator
    from . import ui


# Add custom virtual environment
import site
site.addsitedir(r'C:\Users\lucas\Desktop\New folder\venv\Lib\site-packages')

import bpy

from bpy.props import IntProperty, PointerProperty, BoolProperty

classes = (
    ui.OSRSMC_PT_Panel_Load_Model,
    ui.OSRSMC_PT_Panel_Merge_Materials,
    operator.OSRSMC_OT_Load_Model,
    operator.OSRSMC_OT_Merge_Materials
)

props = [
    ("osrs_model", 
     PointerProperty(name="target", 
                     type=bpy.types.Object)),
    ("freq_weight",
     BoolProperty(name="frequency weight", 
                  default=True)),
    ("find_optimal_k",
     BoolProperty(name="find optimal k", 
                  default=True)),
    ("k",
     IntProperty(name="k", 
                 min=constants.min_k,
                 max=constants.max_k,
                 default=5))
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
