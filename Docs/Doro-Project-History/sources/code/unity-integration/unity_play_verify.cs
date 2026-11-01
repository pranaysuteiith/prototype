using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
public static class BoyPlayValidation {
 public static async Task<string> Test(){
 if(!EditorApplication.isPlaying)throw new Exception("Play mode required");
 string folder="Characters/Boy_GreenSweater";var errors=new List<string>();Application.LogCallback log=(m,s,t)=>{if(t==LogType.Error||t==LogType.Exception||t==LogType.Assert)errors.Add(m);};Application.logMessageReceived+=log;
 var root=new GameObject("Temporary Boy Play Validation");var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/DoroPainted/Characters/BoyGreenSweater/Boy_GreenSweater.prefab");var boy=UnityEngine.Object.Instantiate(prefab,root.transform);boy.transform.position=new Vector3(100,0,100);
 foreach(var tr in boy.GetComponentsInChildren<Transform>(true))tr.gameObject.layer=31;
 var anim=boy.GetComponent<Animator>();anim.cullingMode=AnimatorCullingMode.AlwaysAnimate;anim.applyRootMotion=false;
 var reports=new List<object>();var camObj=new GameObject("Validation Camera");camObj.transform.parent=root.transform;var cam=camObj.AddComponent<Camera>();cam.cullingMask=1<<31;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.22f,.24f,.26f);cam.orthographic=true;cam.orthographicSize=.78f;cam.nearClipPlane=.01f;cam.farClipPlane=20;cam.transform.position=boy.transform.position+new Vector3(1.7f,1.15f,3);cam.transform.LookAt(boy.transform.position+Vector3.up*.62f);
 var lightObj=new GameObject("Validation Softbox");lightObj.transform.parent=root.transform;var light=lightObj.AddComponent<Light>();light.type=LightType.Directional;light.intensity=2;light.cullingMask=1<<31;lightObj.transform.rotation=Quaternion.Euler(35,210,0);
 var rt=new RenderTexture(768,768,24);cam.targetTexture=rt;
 try{
 foreach(var name in new[]{"Idle","Walk","Run","Wave","Sit"}){
  string state="ARM_Boy_GreenSweater|ANIM_"+name;anim.Play(state,0,0);anim.Update(0);var head=anim.GetBoneTransform(HumanBodyBones.Head);var hand=anim.GetBoneTransform(HumanBodyBones.RightHand);var foot=anim.GetBoneTransform(HumanBodyBones.LeftFoot);var q=hand.rotation;var f=foot.position;await Task.Delay(name=="Sit"?3000:name=="Wave"?1400:550);
  var info=anim.GetCurrentAnimatorStateInfo(0);var bounds=boy.GetComponentsInChildren<Renderer>().Aggregate(new Bounds(boy.transform.position+Vector3.up*.6f,Vector3.zero),(b,r)=>{b.Encapsulate(r.bounds);return b;});
  reports.Add(new {action=name,stateMatched=info.IsName(state),normalizedTime=info.normalizedTime,handRotationDegrees=Quaternion.Angle(q,hand.rotation),footMovement=Vector3.Distance(f,foot.position),height=bounds.size.y,headFinite=!float.IsNaN(head.position.y),animatorHuman=anim.isHuman});
  if(name=="Idle"||name=="Walk"||name=="Wave"||name=="Sit"){
   cam.Render();var prev=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(768,768,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,768,768),0,0);tex.Apply();File.WriteAllBytes(folder+"/Previews/Unity_"+name+".png",tex.EncodeToPNG());UnityEngine.Object.Destroy(tex);RenderTexture.active=prev;
  }
 }
 var result=Newtonsoft.Json.JsonConvert.SerializeObject(new {playMode=EditorApplication.isPlaying,animatorHuman=anim.isHuman,actions=reports,errors=errors},Newtonsoft.Json.Formatting.Indented);File.WriteAllText(folder+"/unity-play-validation.json",result);return result;
 }finally{Application.logMessageReceived-=log;cam.targetTexture=null;rt.Release();UnityEngine.Object.Destroy(rt);UnityEngine.Object.Destroy(root);}
 }
}
