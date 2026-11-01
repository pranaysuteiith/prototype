using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Unity.Profiling;
using Doro.PaintedCity;
public static class DoroVerify
{
    static Task Frames(int n)
    {
        var done=new TaskCompletionSource<bool>(); int start=Time.frameCount; double deadline=EditorApplication.timeSinceStartup+25;
        EditorApplication.CallbackFunction tick=null;
        tick=()=> { if(Time.frameCount-start>=n) { EditorApplication.update-=tick; done.TrySetResult(true); } else if(EditorApplication.timeSinceStartup>deadline) { EditorApplication.update-=tick; done.TrySetException(new Exception("Player loop stalled")); } };
        EditorApplication.update+=tick; return done.Task;
    }
    static async Task<object> Profile(bool blur,DoroCenterFocus focus)
    {
        focus.depthOfFieldEnabled=blur; await Frames(30);
        var names=new[]{"Main Thread","Render Thread","Triangles Count","Vertices Count","Draw Calls Count","Batches Count","SetPass Calls Count","GC Allocated In Frame","System Used Memory"};
        var recorders=new List<ProfilerRecorder>();
        foreach(var name in names) recorders.Add(ProfilerRecorder.StartNew((name=="Main Thread" || name=="Render Thread" ? ProfilerCategory.Internal : name.Contains("Memory") || name.Contains("Allocated") ? ProfilerCategory.Memory : ProfilerCategory.Render),name,180));
        int start=Time.frameCount; double time=Time.realtimeSinceStartupAsDouble; await Frames(180);
        double elapsed=Time.realtimeSinceStartupAsDouble-time;
        var result=new Dictionary<string,object>();
        result["blur"]=blur; result["frames"]=Time.frameCount-start; result["elapsedSeconds"]=elapsed; result["observedFPS"]=(Time.frameCount-start)/elapsed;
        for(int i=0;i<recorders.Count;i++) { var r=recorders[i]; var samples=new List<ProfilerRecorderSample>(); if(r.Valid) r.CopyTo(samples); result[names[i]]=new { valid=r.Valid, samples=samples.Count, mean=samples.Count==0?0:samples.Average(s=>(double)s.Value), unit=r.Valid?r.UnitType.ToString():"unavailable" }; r.Dispose(); }
        return result;
    }
    public static async Task<string> Run()
    {
        if(!Application.isPlaying) throw new Exception("Play mode required");
        var cam=GameObject.Find("Doro Game Camera").GetComponent<Camera>(); var nav=cam.GetComponent<DoroPanZoom>(); var focus=cam.GetComponent<DoroCenterFocus>();
        var initial=cam.transform.position; var pivot=nav.pivot; var direction=(initial-pivot).normalized;
        var distanceField=typeof(DoroPanZoom).GetField("distance",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic);
        float distance=(float)distanceField.GetValue(nav);
        var tests=new List<object>(); var failures=new List<string>();
        void Record(string name,bool pass,object detail) { tests.Add(new {name,pass,detail}); if(!pass) failures.Add(name); }
        var pickups=UnityEngine.Object.FindObjectsByType<Pickup>(); var rotations=pickups.Select(p=>p.transform.rotation).ToArray();
        int initialFrame=Time.frameCount; await Frames(10);
        Record("Existing pickup animations",pickups.Length>0 && pickups.Select((p,i)=>Quaternion.Angle(rotations[i],p.transform.rotation)).All(a=>a>1f),new {count=pickups.Length}); Record("Player loop advances",Time.frameCount>initialFrame,new {initialFrame,frame=Time.frameCount});
        foreach(var key in new[]{Key.W,Key.A,Key.S,Key.D,Key.UpArrow,Key.LeftArrow,Key.DownArrow,Key.RightArrow})
        {
            var before=nav.pivot; InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState(key)); await Frames(12); InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState()); await Frames(2);
            Record("Pan "+key,Vector3.Distance(before,nav.pivot)>.03f,new {before=before.ToString(),after=nav.pivot.ToString()});
        }
        foreach(var button in new[]{MouseButton.Right,MouseButton.Middle})
        {
            var before=nav.pivot; InputSystem.QueueStateEvent(Mouse.current,new MouseState().WithButton(button)); await Frames(2);
            InputSystem.QueueDeltaStateEvent(Mouse.current.delta,new Vector2(120,30)); await Frames(2);
            InputSystem.QueueStateEvent(Mouse.current,new MouseState()); await Frames(2);
            Record("Drag "+button,Vector3.Distance(before,nav.pivot)>.03f,new {before=before.ToString(),after=nav.pivot.ToString()});
        }
        float beforeDistance=(float)distanceField.GetValue(nav);
        InputSystem.QueueDeltaStateEvent(Mouse.current.scroll,new Vector2(0,120)); await Frames(15);
        float afterDistance=(float)distanceField.GetValue(nav);
        Record("Wheel dolly zoom",afterDistance<beforeDistance-.1f,new {beforeDistance,afterDistance});
        // Pan without changing tilt or pivot height; place each subject on the center ray.
        foreach(var name in new[]{"FocusProxy_GEO_Cafe","FocusProxy_GEO_Lime_tree_terrace","FocusProxy_Picnic table","FocusProxy_Ground"})
        {
            var col=GameObject.Find(name).GetComponent<BoxCollider>(); var target=col.bounds.center;
            if(name.EndsWith("Ground")) target=new Vector3(-10,0,9);
            if(name.Contains("tree")) target.y=3.8f;
            nav.pivot=target+direction*((pivot.y-target.y)/direction.y);
            await Frames(75);
            var ray=cam.ViewportPointToRay(new Vector3(.5f,.5f,0)); bool hit=Physics.Raycast(ray,out var h,250,focus.focusLayers,QueryTriggerInteraction.Collide);
            float expected=hit?Vector3.Dot(h.point-cam.transform.position,cam.transform.forward):0;
            Record("Focus "+name,hit && h.collider.name==name && Mathf.Abs(focus.CurrentDepth-expected)<.3f,new {subject=focus.FocusSubject,depth=focus.CurrentDepth,expected,error=Mathf.Abs(focus.CurrentDepth-expected),pivot=nav.pivot.ToString()});
        }
        // Force no proxy hit to exercise the mathematical ground fallback.
        var mask=focus.focusLayers; focus.focusLayers=0; nav.pivot=new Vector3(0,2.2f,0); await Frames(60);
        Record("Ground-plane fallback",focus.FocusSubject=="Ground plane fallback",new {focus.FocusSubject,focus.CurrentDepth}); focus.focusLayers=mask;
        bool beforeBlur=focus.depthOfFieldEnabled;
        InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState(Key.B)); await Frames(2); InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState()); await Frames(2);
        Record("B toggles blur",focus.depthOfFieldEnabled!=beforeBlur,new {beforeBlur,after=focus.depthOfFieldEnabled});
        nav.pivot=pivot; distanceField.SetValue(nav,distance); cam.transform.position=initial; await Frames(90);
        var profiles=new List<object>(); profiles.Add(await Profile(true,focus)); profiles.Add(await Profile(false,focus)); focus.depthOfFieldEnabled=true; await Frames(30);
        var pickup = UnityEngine.Object.FindObjectsByType<Pickup>().First();
        var pickupName=pickup.name;
        var probe=new GameObject("Temporary pickup verification player"); probe.tag="Player"; probe.transform.position=pickup.transform.position;
        probe.AddComponent<SphereCollider>().radius=.35f; probe.AddComponent<Rigidbody>().isKinematic=true; await Frames(20);
        Record("Existing pickup collection trigger",!pickup,new {pickupName,collected=!pickup}); UnityEngine.Object.Destroy(probe);
        var root=GameObject.Find("Doro Painted Crossroads"); var renderers=root.GetComponentsInChildren<MeshRenderer>();
        Record("No missing or unsupported materials",renderers.All(r=>r.sharedMaterials.All(m=>m && m.shader && m.shader.isSupported && m.shader.name!="Hidden/InternalErrorShader")),renderers.SelectMany(r=>r.sharedMaterials).Distinct().Select(m=>new {m.name,shader=m.shader.name,path=AssetDatabase.GetAssetPath(m)}).ToArray());
        Record("Simplified trigger focus colliders",GameObject.Find("Focus Colliders").GetComponentsInChildren<Collider>().All(c=>c is BoxCollider && c.isTrigger),new {count=GameObject.Find("Focus Colliders").GetComponentsInChildren<Collider>().Length});
        string json=Newtonsoft.Json.JsonConvert.SerializeObject(new {tests,failures,profiles, geometry=new {meshes=renderers.Length,triangles=root.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.triangles.Length/3),vertices=root.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.vertexCount)}, camera=new {position=cam.transform.position.ToString(),cam.fieldOfView},environment=new { UnityEngine.SystemInfo.deviceModel,UnityEngine.SystemInfo.graphicsDeviceName, width=Screen.width,height=Screen.height,quality=QualitySettings.names[QualitySettings.GetQualityLevel()]},finalFrame=Time.frameCount},Newtonsoft.Json.Formatting.Indented);
        System.IO.File.WriteAllText("DoroBackups/2026-10-26/play-verification.json",json);
        return json;
    }
}
