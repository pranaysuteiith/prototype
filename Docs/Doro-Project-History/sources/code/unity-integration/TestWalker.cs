using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEditor;
using Doro.PaintedCity;
public static class TestWalker {
 public static async Task<string> Test(){
  if(!EditorApplication.isPlaying)throw new Exception("Play mode required");
  var walker=UnityEngine.Object.FindAnyObjectByType<DoroBoyWalker>();var t=walker.transform;var cc=walker.GetComponent<CharacterController>();var anim=walker.animator;var camera=walker.movementCamera;var keyboard=InputSystem.AddDevice<Keyboard>("DoroMovementVerification");keyboard.MakeCurrent();
  var errors=new List<string>();Application.LogCallback capture=(m,s,type)=>{if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(m);};Application.logMessageReceived+=capture;
  var results=new List<object>();Vector3 spawn=t.position;Quaternion startRotation=t.rotation;var pan=camera.GetComponent<DoroPanZoom>();Vector3 initialPivot=pan.pivot;Vector3 initialCamera=camera.transform.position;Vector3 cameraOffset=initialCamera-initialPivot;
  Func<Key[],int,Task> hold=async(keys,ms)=>{InputSystem.QueueStateEvent(keyboard,new KeyboardState(keys));await Task.Delay(ms);};
  Action<Vector3> teleport=p=>{cc.enabled=false;t.position=p;cc.enabled=true;pan.pivot=initialPivot+p-spawn;camera.transform.position=pan.pivot+cameraOffset;camera.transform.LookAt(pan.pivot);typeof(DoroPanZoom).GetField("previousFollowPosition",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).SetValue(pan,p);Physics.SyncTransforms();};
  try {
   await hold(new Key[0],450);float groundY=t.position.y;
   foreach(var key in new[]{Key.UpArrow,Key.DownArrow,Key.LeftArrow,Key.RightArrow}){
    teleport(spawn);await hold(new Key[0],300);Vector3 before=t.position;Vector3 pivot=pan.pivot;
    Vector3 expected=key==Key.UpArrow?camera.transform.forward:key==Key.DownArrow?-camera.transform.forward:key==Key.RightArrow?camera.transform.right:-camera.transform.right;expected=Vector3.ProjectOnPlane(expected,Vector3.up).normalized;
    await hold(new[]{key},750);Vector3 delta=Vector3.ProjectOnPlane(t.position-before,Vector3.up);bool walk=anim.GetCurrentAnimatorStateInfo(0).IsName("ARM_Boy_GreenSweater|ANIM_Walk");
    await hold(new Key[0],500);Vector3 cameraDelta=Vector3.ProjectOnPlane(pan.pivot-pivot,Vector3.up);Vector3 fullTravel=Vector3.ProjectOnPlane(t.position-before,Vector3.up);
    results.Add(new {key=key.ToString(),distance=delta.magnitude,directionDot=Vector3.Dot(delta.normalized,expected),walkingAnimation=walk,cameraFollowsOnlyPlayer=(cameraDelta-fullTravel).magnitude<.1f,grounded=cc.isGrounded,feetY=t.position.y});
    await hold(new Key[0],500);
   }
   bool idle=anim.GetCurrentAnimatorStateInfo(0).IsName("ARM_Boy_GreenSweater|ANIM_Idle");
   teleport(new Vector3(17.7f,.25f,6));await hold(new Key[0],350);walker.enabled=false;for(int step=0;step<110;step++){cc.Move(new Vector3(.025f,-.02f,0));await Task.Delay(10);}walker.enabled=true;bool boundary=t.position.x>18.0f && t.position.x<18.25f;float wallX=t.position.x;
   await hold(new Key[0],350);teleport(spawn);t.rotation=startRotation;pan.pivot=initialPivot;typeof(DoroPanZoom).GetField("previousFollowPosition",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).SetValue(pan,t.position);camera.transform.position=initialCamera;await hold(new Key[0],500);
   string file="Characters/Boy_GreenSweater/Previews/Unity_PlayableBoy.png";
   var rt=new RenderTexture(1200,900,24);var old=camera.targetTexture;var active=RenderTexture.active;camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;var tex=new Texture2D(1200,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1200,900),0,0);tex.Apply();File.WriteAllBytes(file,tex.EncodeToPNG());camera.targetTexture=old;RenderTexture.active=active;rt.Release();UnityEngine.Object.Destroy(rt);UnityEngine.Object.Destroy(tex);
   var report=new {playMode=true,renderersVisible=walker.GetComponentsInChildren<Renderer>().All(r=>(camera.cullingMask & (1<<r.gameObject.layer))!=0),spawnGroundY=groundY,arrowTests=results,idleAfterRelease=idle,boundaryBlocks=boundary,wallX,errors,screenshot=file};string json=Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented);File.WriteAllText("Characters/Boy_GreenSweater/UnityMap/play-test.json",json);return json;
  } finally {InputSystem.QueueStateEvent(keyboard,new KeyboardState());InputSystem.RemoveDevice(keyboard);Keyboard.current?.MakeCurrent();Application.logMessageReceived-=capture;}
 }
}
