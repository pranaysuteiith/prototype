"""Read-only Blender connection/version probe; run with Blender --python."""
import json
import bpy
print(json.dumps({"version": bpy.app.version_string, "file": bpy.data.filepath,
                  "scene": bpy.context.scene.name, "objects": len(bpy.data.objects)}, indent=2))
