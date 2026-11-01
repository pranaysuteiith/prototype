using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ImportBlenderBalls
{
    const string Folder = "Assets/BlenderBalls";

    [MenuItem("Doro/Import Blender Balls")]
    public static void Import()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode)
            throw new InvalidOperationException("Stop Play mode before importing.");
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null) throw new InvalidOperationException("URP Lit shader is unavailable.");
        var yellow = Material("Yellow Ball Material", new Color(1f, .72f, .005f, 1f), shader);
        var red = Material("Red Ball Material", new Color(.8f, .012f, .018f, 1f), shader);
        string modelPath = Folder + "/BlenderBalls.fbx";
        var importer = AssetImporter.GetAtPath(modelPath) as ModelImporter;
        if (importer == null) throw new InvalidOperationException("Blender FBX has not imported.");
        foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(modelPath))
        {
            if (asset is Material source)
                importer.AddRemap(new AssetImporter.SourceAssetIdentifier(source),
                    source.name.IndexOf("Yellow", StringComparison.OrdinalIgnoreCase) >= 0 ? yellow : red);
        }
        importer.SaveAndReimport();
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
        if (model == null) throw new InvalidOperationException("Blender model could not be loaded.");
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
        instance.name = "Blender Balls";
        Undo.RegisterCreatedObjectUndo(instance, "Import Blender balls");
        foreach (var renderer in instance.GetComponentsInChildren<MeshRenderer>())
            renderer.sharedMaterial = renderer.name.IndexOf("Yellow", StringComparison.OrdinalIgnoreCase) >= 0 ? yellow : red;
        string prefabPath = Folder + "/Blender Balls.prefab";
        PrefabUtility.SaveAsPrefabAssetAndConnect(instance, prefabPath, InteractionMode.AutomatedAction);
        AssetDatabase.SaveAssets();
        var scene = instance.scene;
        EditorSceneManager.MarkSceneDirty(scene);
        if (string.IsNullOrEmpty(scene.path))
        {
            if (!AssetDatabase.IsValidFolder("Assets/Scenes")) AssetDatabase.CreateFolder("Assets", "Scenes");
            EditorSceneManager.SaveScene(scene, AssetDatabase.GenerateUniqueAssetPath("Assets/Scenes/BlenderBalls.unity"));
        }
        else EditorSceneManager.SaveScene(scene);
        Selection.activeGameObject = instance;
        if (SceneView.lastActiveSceneView != null) SceneView.lastActiveSceneView.FrameSelected();
        Debug.Log("BLENDER_BALLS_IMPORT_OK: " + scene.path + " | meshes=" + instance.GetComponentsInChildren<MeshRenderer>().Length);
    }

    static Material Material(string name, Color color, Shader shader)
    {
        string path = Folder + "/" + name + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            material = new Material(shader) { name = name };
            AssetDatabase.CreateAsset(material, path);
        }
        material.shader = shader;
        material.SetColor("_BaseColor", color);
        material.SetFloat("_Smoothness", .35f);
        EditorUtility.SetDirty(material);
        return material;
    }
}
