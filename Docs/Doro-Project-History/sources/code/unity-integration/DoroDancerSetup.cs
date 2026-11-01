using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
public static class DoroDancerSetup
{
    const string Folder="Assets/DoroPainted/Characters/BellyDancer";
    const string ModelPath=Folder+"/Models/Belly Dance.fbx";
    public static string Run()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Exit Play mode first.");
        var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
        if(scene.path!="Assets/Scenes/GetStarted_Scene.unity") throw new Exception("Unexpected active scene: "+scene.path);
        Directory.CreateDirectory("DoroBackups/2026-10-28/before-belly-dancer");
        string backup="DoroBackups/2026-10-28/before-belly-dancer/LiveScene.unity";
        if(!File.Exists(backup)) EditorSceneManager.SaveScene(scene,backup,true);
        if(GameObject.Find("Belly Dancer - Road Performance")) throw new Exception("Dancer already exists; inspect instead of duplicating.");
        Directory.CreateDirectory(Folder+"/Textures");Directory.CreateDirectory(Folder+"/Materials");Directory.CreateDirectory(Folder+"/Animation");AssetDatabase.Refresh();
        var importer=(ModelImporter)AssetImporter.GetAtPath(ModelPath);
        importer.importAnimation=true;importer.animationType=ModelImporterAnimationType.Generic;
        importer.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
        var clips=importer.defaultClipAnimations;
        foreach(var clip in clips) if(clip.name=="mixamo.com")
        {
            clip.loopTime=true;clip.loopPose=false;clip.lockRootRotation=true;clip.lockRootPositionXZ=true;
            clip.keepOriginalOrientation=true;clip.keepOriginalPositionXZ=true;
        }
        importer.clipAnimations=clips;
        importer.ExtractTextures(Folder+"/Textures");importer.SaveAndReimport();
        var shader=Shader.Find("Universal Render Pipeline/Lit");
        var textures=AssetDatabase.FindAssets("t:Texture2D",new[]{Folder+"/Textures"}).Select(g=>AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath(g))).ToArray();
        foreach(var raw in AssetDatabase.LoadAllAssetsAtPath(ModelPath).OfType<Material>())
        {
            var mat=new Material(raw){name=raw.name,shader=shader};
            if(raw.HasProperty("_BaseColor")) mat.SetColor("_BaseColor",raw.GetColor("_BaseColor"));
            var texture=raw.mainTexture;
            if(raw.name=="CH_Face_PeachBlush") texture=textures.FirstOrDefault(t=>t.name.Contains("Face")) ?? texture;
            if(texture) {mat.SetTexture("_BaseMap",texture);if(raw.name=="CH_Face_PeachBlush")mat.SetColor("_BaseColor",Color.white);}
            mat.SetFloat("_Metallic",0);mat.SetFloat("_Smoothness",raw.name.Contains("Eye")?.25f:.12f);
            AssetDatabase.CreateAsset(mat,Folder+"/Materials/"+raw.name+".mat");
            importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),raw.name),mat);
        }
        importer.SaveAndReimport();
        var model=AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        var dance=AssetDatabase.LoadAllAssetsAtPath(ModelPath).OfType<AnimationClip>().First(c=>c.name=="mixamo.com");
        var controller=AnimatorController.CreateAnimatorControllerAtPath(Folder+"/Animation/BellyDance.controller");
        var state=controller.layers[0].stateMachine.AddState("Belly Dance - Loop");state.motion=dance;state.speed=1;controller.layers[0].stateMachine.defaultState=state;
        Undo.IncrementCurrentGroup();int undo=Undo.GetCurrentGroup();Undo.SetCurrentGroupName("Add belly dancer on café road");
        var root=new GameObject("Belly Dancer - Road Performance");Undo.RegisterCreatedObjectUndo(root,"Add belly dancer");
        root.transform.SetParent(GameObject.Find("Doro Painted Cafe - Imported").transform,false);
        root.transform.position=new Vector3(-3.4f,.08f,5.5f);
        // Front of the traffic signal and the café's Today / Coffee & Cake sandwich board.
        root.transform.rotation=Quaternion.Euler(0,35,0);
        var character=(GameObject)PrefabUtility.InstantiatePrefab(model);character.name="Belly Dancing Girl";character.transform.SetParent(root.transform,false);
        var renderers=character.GetComponentsInChildren<SkinnedMeshRenderer>();var bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);
        float scale=1.85f/bounds.size.y;root.transform.localScale=Vector3.one*scale;
        bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);
        character.transform.position+=Vector3.up*(.08f-bounds.min.y-.094f); // Calibrated against baked shoe vertices over the dance loop.
        foreach(var t in root.GetComponentsInChildren<Transform>(true))t.gameObject.layer=31;
        foreach(var r in renderers){r.updateWhenOffscreen=true;PrefabUtility.RecordPrefabInstancePropertyModifications(r);}
        var animator=character.GetComponent<Animator>() ?? character.AddComponent<Animator>();animator.runtimeAnimatorController=controller;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
        PrefabUtility.RecordPrefabInstancePropertyModifications(animator);PrefabUtility.RecordPrefabInstancePropertyModifications(character.transform);
        var focus=new GameObject("FocusProxy_Belly Dancer");focus.transform.SetParent(root.transform,false);focus.layer=31;focus.transform.localScale=Vector3.one/scale;
        focus.transform.position=root.transform.position+Vector3.up*.95f;var collider=focus.AddComponent<CapsuleCollider>();collider.height=1.9f;collider.radius=.35f;collider.isTrigger=true;
        Undo.CollapseUndoOperations(undo);EditorSceneManager.MarkSceneDirty(scene);AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(scene);Selection.activeGameObject=root;
        return Newtonsoft.Json.JsonConvert.SerializeObject(new {root=root.name,position=root.transform.position.ToString(),scale,clip=dance.name,dance.length,loop=dance.isLooping,textures=textures.Select(t=>t.name).ToArray(),avatarValid=animator.avatar&&animator.avatar.isValid},Newtonsoft.Json.Formatting.Indented);
    }
}
