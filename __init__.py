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
# Import packages
# ----------------------------------------------

# If bpy is imported, then it is not the first import, 
# and ui and operator need to be reloaded
if "bpy" in locals():
    import importlib
    importlib.reload(functions)
    importlib.reload(ui)
    importlib.reload(operator)
else:
    from . import functions
    from . import ui
    from . import operator


import bpy
import numpy as np

from bpy.props import IntProperty, PointerProperty




import importlib
import os
import subprocess
import sys

# Create dictionary "install_name" -> import_name
dependencies = {
    "scikit-learn": "sklearn"
}

# Define path to python executable
python_exe = os.path.join(sys.prefix, "bin", "python.exe")
target = os.path.join(sys.prefix, 'lib', 'site-packages')

for install_name in dependencies.keys():
    subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "scikit-learn"])

import sklearn


# # print("bpy", importlib.util.find_spec("bpy"))
# print("-------- sklearn", importlib.util.find_spec("sklearn"))
# print("-------- scikit-learn", importlib.util.find_spec("scikit-learn"))


# python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')


# from . import functions
# from bpy.props import PointerProperty


# # Install packages if not yet installed
# for install_name, import_name in dependencies.items():


# from . import ui
# from . import operator

# # Reload ui and operator
# importlib.reload(ui)
# importlib.reload(operator)
   

# if "bpy" in locals():
#     import importlib
#     importlib.reload(ui)
#     importlib.reload(operators)
#     if "mesh_helpers" in locals():
#         importlib.reload(mesh_helpers)
#     if "export" in locals():
#         importlib.reload(export)



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
    ('max_n_clusters', IntProperty(name='Max Clusters', min=1, default=20))
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
