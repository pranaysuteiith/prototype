using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Doro.PaintedCity;
public static class SetupWalker
{
 const string Folder="Characters/Boy_GreenSweater/UnityMap";
 public static string Setup()
 {
  if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Edit mode required");
  var scene=UnityEngine.SceneManagement.SceneManager.GetActiveScene();
  string backup=Folder+"/GetStarted_BeforePlayableBoy.unity";
  Directory.CreateDirectory(Folder);
  if(!File.Exists(backup))EditorSceneManager.SaveScene(scene,backup,true);
  string snapshotPath=Folder+"/original-scene-objects.json";
  if(!File.Exists(snapshotPath))File.WriteAllText(snapshotPath,Newtonsoft.Json.JsonConvert.SerializeObject(scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).Select(t=>new{id=t.GetEntityId().ToString(),t.name,position=new[]{t.position.x,t.position.y,t.position.z},scale=new[]{t.localScale.x,t.localScale.y,t.localScale.z},active=t.gameObject.activeSelf}).ToArray(),Newtonsoft.Json.Formatting.Indented));
  var tags=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);var layers=tags.FindProperty("layers");
  int layer=LayerMask.NameToLayer("DoroWalking");
  if(layer<0){layer=28;if(!string.IsNullOrEmpty(layers.GetArrayElementAtIndex(layer).stringValue))throw new Exception("Layer 28 occupied");layers.GetArrayElementAtIndex(layer).stringValue="DoroWalking";tags.ApplyModifiedProperties();}
  var group=GameObject.Find("Doro Playable Boy");if(group)return "Playable boy already exists";
  Undo.IncrementCurrentGroup();int undo=Undo.GetCurrentGroup();Undo.SetCurrentGroupName("Add arrow-key boy and walking collisions");
  group=new GameObject("Doro Playable Boy");Undo.RegisterCreatedObjectUndo(group,"Add playable boy");
  var physics=new GameObject("Walking surfaces and obstacles");physics.transform.parent=group.transform;
  var environment=GameObject.Find("Doro Painted Cafe - Imported");
  int triangles=0;
  foreach(var f in environment.GetComponentsInChildren<MeshFilter>())
   if(f.name=="GEO_Roads_and_Street"||f.name=="GEO_Terrace"||f.name=="GEO_Cafe"){
    var g=new GameObject("WalkMesh_"+f.name);g.transform.parent=physics.transform;g.layer=layer;g.transform.SetPositionAndRotation(f.transform.position,f.transform.rotation);g.transform.localScale=f.transform.lossyScale;
    g.AddComponent<MeshCollider>().sharedMesh=f.sharedMesh;triangles+=f.sharedMesh.triangles.Length/3;
   }
  foreach(var c in environment.GetComponentsInChildren<BoxCollider>()){
   string n=c.name;
   bool obstacle=n.EndsWith(" trunk")||n.Contains("hatchback")||n.Contains("Bookshop")||n.Contains("Bakery")||n.Contains("atelier")||n.Contains("Townhouse")||n.Contains("South_east_shop")||n.Contains("Pedestrian")||n.Contains("Customer")||n.Contains("visitor");
   if(!obstacle||!c.isTrigger)continue;
   var g=new GameObject("WalkObstacle_"+n);g.transform.parent=physics.transform;g.layer=layer;g.transform.SetPositionAndRotation(c.transform.position,c.transform.rotation);g.transform.localScale=c.transform.lossyScale;var box=g.AddComponent<BoxCollider>();box.center=c.center;box.size=c.size;
  }
  Action<string,Vector3,Vector3> wall=(name,p,size)=>{var g=new GameObject(name);g.transform.parent=physics.transform;g.layer=layer;g.transform.position=p;g.AddComponent<BoxCollider>().size=size;};
  wall("Map boundary east",new Vector3(18.5f,2,0),new Vector3(.3f,5,34));wall("Map boundary west",new Vector3(-18.5f,2,0),new Vector3(.3f,5,34));wall("Map boundary north",new Vector3(0,2,16.5f),new Vector3(37,5,.3f));wall("Map boundary south",new Vector3(0,2,-16.5f),new Vector3(37,5,.3f));
  var player=new GameObject("Boy Green Sweater - Arrow Keys");player.transform.parent=group.transform;player.layer=layer;player.transform.position=new Vector3(2.5f,.3f,5.2f);player.transform.rotation=Quaternion.Euler(0,25,0);
  var visual=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/DoroPainted/Characters/BoyGreenSweater/Boy_GreenSweater.prefab"));visual.name="Boy Green Sweater Visual";visual.transform.SetParent(player.transform,false);visual.transform.localScale=Vector3.one*1.5f;
  foreach(var t in visual.GetComponentsInChildren<Transform>(true))t.gameObject.layer=31;
  var cc=player.AddComponent<CharacterController>();cc.height=1.8f;cc.radius=.23f;cc.center=Vector3.up*.91f;cc.stepOffset=.3f;cc.slopeLimit=50;cc.skinWidth=.015f;cc.minMoveDistance=0;cc.excludeLayers=~(1<<layer);cc.includeLayers=1<<layer;
  var camera=environment.GetComponentInChildren<Camera>();var walker=player.AddComponent<DoroBoyWalker>();walker.movementCamera=camera;walker.animator=visual.GetComponent<Animator>();
  var focus=new GameObject("FocusProxy_PlayableBoy");focus.transform.SetParent(player.transform,false);focus.layer=31;var cap=focus.AddComponent<CapsuleCollider>();cap.center=Vector3.up*.94f;cap.height=1.85f;cap.radius=.32f;cap.isTrigger=true;
  Undo.RecordObject(camera.transform,"Frame playable boy");var pan=camera.GetComponent<DoroPanZoom>();Undo.RecordObject(pan,"Follow playable boy");Vector3 target=player.transform.position+Vector3.up;camera.transform.position+=target-pan.pivot;pan.pivot=target;pan.useArrowKeys=false;pan.followTarget=player.transform;pan.panXBounds=new Vector2(-18,18);pan.panZBounds=new Vector2(-16,16);
  Physics.SyncTransforms();
  if(Physics.Raycast(player.transform.position+Vector3.up*3,Vector3.down,out var hit,10,1<<layer,QueryTriggerInteraction.Ignore)){cc.enabled=false;player.transform.position=hit.point+Vector3.up*.025f;cc.enabled=true;}
  Undo.CollapseUndoOperations(undo);EditorSceneManager.MarkSceneDirty(scene);EditorSceneManager.SaveScene(scene);AssetDatabase.SaveAssets();Selection.activeGameObject=player;
  var result=new{scene=scene.path,backup,player=player.name,spawn=new[]{player.transform.position.x,player.transform.position.y,player.transform.position.z},layer,staticCollisionTriangles=triangles,colliders=physics.GetComponentsInChildren<Collider>().Length};
  string json=Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Folder+"/setup-report.json",json);return json;
 }
}
