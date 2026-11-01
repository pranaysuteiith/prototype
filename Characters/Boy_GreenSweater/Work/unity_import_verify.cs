using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
public static class BoyUnityValidation
{
 const string Asset="Assets/DoroPainted/Characters/BoyGreenSweater";
 const string Source="Characters/Boy_GreenSweater";
 public static string Import()
 {
  if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Exit Play mode before importing character");
  Directory.CreateDirectory(Asset+"/Models");Directory.CreateDirectory(Asset+"/Textures");Directory.CreateDirectory(Asset+"/Materials");Directory.CreateDirectory(Asset+"/Animation");
  File.Copy(Source+"/Models/Boy_GreenSweater_Rigged.fbx",Asset+"/Models/Boy_GreenSweater_Rigged.fbx",true);
  foreach(var p in Directory.GetFiles(Source+"/Textures","*.png"))File.Copy(p,Asset+"/Textures/"+Path.GetFileName(p),true);
  AssetDatabase.Refresh();string path=Asset+"/Models/Boy_GreenSweater_Rigged.fbx";var importer=(ModelImporter)AssetImporter.GetAtPath(path);
  importer.animationType=ModelImporterAnimationType.Human;importer.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;importer.importAnimation=true;
  importer.SaveAndReimport();var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
  var pairs=new[]{("Hips","Hips"),("Spine","Spine"),("Chest","Chest"),("Neck","Neck"),("Head","Head"),("Shoulder.L","LeftShoulder"),("UpperArm.L","LeftUpperArm"),("LowerArm.L","LeftLowerArm"),("Hand.L","LeftHand"),("Shoulder.R","RightShoulder"),("UpperArm.R","RightUpperArm"),("LowerArm.R","RightLowerArm"),("Hand.R","RightHand"),("UpperLeg.L","LeftUpperLeg"),("LowerLeg.L","LeftLowerLeg"),("Foot.L","LeftFoot"),("Toes.L","LeftToes"),("UpperLeg.R","RightUpperLeg"),("LowerLeg.R","RightLowerLeg"),("Foot.R","RightFoot"),("Toes.R","RightToes")};
  var human=importer.humanDescription;human.human=pairs.Select(p=>new HumanBone{boneName=p.Item1,humanName=p.Item2,limit=new HumanLimit{useDefaultValues=true}}).ToArray();
  human.skeleton=model.GetComponentsInChildren<Transform>(true).Select(t=>new SkeletonBone{name=t.name,position=t.localPosition,rotation=t.localRotation,scale=t.localScale}).ToArray();
  human.armStretch=.05f;human.legStretch=.05f;human.upperArmTwist=.5f;human.lowerArmTwist=.5f;human.upperLegTwist=.5f;human.lowerLegTwist=.5f;
  importer.humanDescription=human;
  var clips=importer.defaultClipAnimations;foreach(var clip in clips){clip.loopTime=clip.name.Contains("Idle")||clip.name.Contains("Walk")||clip.name.Contains("Run");clip.lockRootPositionXZ=true;clip.lockRootRotation=true;}importer.clipAnimations=clips;importer.SaveAndReimport();
  foreach(var raw in AssetDatabase.LoadAllAssetsAtPath(path).OfType<Material>())
  {
   string mp=Asset+"/Materials/"+raw.name+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=raw.name};AssetDatabase.CreateAsset(mat,mp);}
   mat.SetColor("_BaseColor",raw.color);mat.SetFloat("_Smoothness",raw.name.Contains("Sunglasses")?.45f:.1f);
   string texture=raw.name=="MAT_Head_Skin"?"Skin_Face_Blush":raw.name=="MAT_Skin_Blush"?"Skin_Blush_Gradient":raw.name+"_BaseColor";var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"/Textures/"+texture+".png");
   if(tex){mat.SetTexture("_BaseMap",tex);mat.SetColor("_BaseColor",Color.white);}
   importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),raw.name),mat);EditorUtility.SetDirty(mat);
  }
  foreach(var mp in Directory.GetFiles(Asset+"/Materials","*.mat"))
  {
   var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!mat)continue;
   var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"/Textures/"+(mat.name=="MAT_Head_Skin"?"Skin_Face_Blush":mat.name+"_BaseColor")+".png");if(tex){mat.SetTexture("_BaseMap",tex);mat.SetColor("_BaseColor",Color.white);}
   string np=Asset+"/Textures/"+mat.name+"_Normal.png";
   if(File.Exists(np)){var ti=(TextureImporter)AssetImporter.GetAtPath(np);if(ti.textureType!=TextureImporterType.NormalMap){ti.textureType=TextureImporterType.NormalMap;ti.SaveAndReimport();}mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(np));mat.SetFloat("_BumpScale",.65f);mat.EnableKeyword("_NORMALMAP");}EditorUtility.SetDirty(mat);
  }
  importer.SaveAndReimport();model=AssetDatabase.LoadAssetAtPath<GameObject>(path);var avatar=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().FirstOrDefault();
  var animations=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();
  string controllerPath=Asset+"/Animation/Boy.controller";var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
  if(!controller){controller=AnimatorController.CreateAnimatorControllerAtPath(controllerPath);foreach(var clip in animations){var state=controller.layers[0].stateMachine.AddState(clip.name);state.motion=clip;}}
  var instance=(GameObject)PrefabUtility.InstantiatePrefab(model);instance.name="Boy Green Sweater Validation";var animator=instance.GetComponent<Animator>()??instance.AddComponent<Animator>();animator.avatar=avatar;animator.runtimeAnimatorController=controller;animator.applyRootMotion=false;
  var missing=new List<string>();foreach(HumanBodyBones b in new[]{HumanBodyBones.Hips,HumanBodyBones.Spine,HumanBodyBones.Chest,HumanBodyBones.Neck,HumanBodyBones.Head,HumanBodyBones.LeftUpperArm,HumanBodyBones.LeftLowerArm,HumanBodyBones.LeftHand,HumanBodyBones.RightUpperArm,HumanBodyBones.RightLowerArm,HumanBodyBones.RightHand,HumanBodyBones.LeftUpperLeg,HumanBodyBones.LeftLowerLeg,HumanBodyBones.LeftFoot,HumanBodyBones.RightUpperLeg,HumanBodyBones.RightLowerLeg,HumanBodyBones.RightFoot})if(!animator.GetBoneTransform(b))missing.Add(b.ToString());
  PrefabUtility.SaveAsPrefabAsset(instance,Asset+"/Boy_GreenSweater.prefab");UnityEngine.Object.DestroyImmediate(instance);AssetDatabase.SaveAssets();
  var result=new {avatarValid=avatar&&avatar.isValid,avatarHuman=avatar&&avatar.isHuman,missingMappings=missing,clips=animations.Select(c=>new {c.name,c.length,c.isHumanMotion,c.isLooping}).ToArray(),prefab=Asset+"/Boy_GreenSweater.prefab"};
  string json=Newtonsoft.Json.JsonConvert.SerializeObject(result,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Source+"/unity-validation.json",json);return json;
 }
}
