using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using Doro.PaintedCity;
public static class DoroOrbitVerify
{
    static Task Frames(int n)
    {
        var t=new TaskCompletionSource<bool>(); int start=Time.frameCount; double deadline=EditorApplication.timeSinceStartup+15;
        EditorApplication.CallbackFunction tick=null; tick=()=> { if(Time.frameCount-start>=n) {EditorApplication.update-=tick;t.SetResult(true);} else if(EditorApplication.timeSinceStartup>deadline) {EditorApplication.update-=tick;t.SetException(new Exception("No advancing frames"));}}; EditorApplication.update+=tick;return t.Task;
    }
    public static async Task<string> Run()
    {
        var camera=GameObject.Find("Doro Game Camera").GetComponent<Camera>(); var nav=camera.GetComponent<DoroPanZoom>();
        var checks=new List<object>();var start=camera.transform.position;var pivot=nav.pivot; var field=typeof(DoroPanZoom).GetField("viewDirection",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic);var direction=(Vector3)field.GetValue(nav);
        async Task KeyHold(Key key,int frames) {InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState(key));await Frames(frames);InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState());await Frames(45);}
        var before=camera.transform.position-pivot;await KeyHold(Key.Q,30);var after=camera.transform.position-pivot;
        float q=Vector3.SignedAngle(Vector3.ProjectOnPlane(before,Vector3.up),Vector3.ProjectOnPlane(after,Vector3.up),Vector3.up);
        checks.Add(new {test="Q orbits left",pass=q < -1f,degrees=q});
        checks.Add(new {test="Orbit preserves pivot, distance and height",pass=Vector3.Distance(pivot,nav.pivot)<.001f && Mathf.Abs(before.magnitude-after.magnitude)<.1f && Mathf.Abs(before.y-after.y)<.01f});
        checks.Add(new {test="Camera remains aimed at pivot",pass=Vector3.Angle(camera.transform.forward,(pivot-camera.transform.position).normalized)<.01f});
        before=after;await KeyHold(Key.E,30);after=camera.transform.position-pivot;
        float e=Vector3.SignedAngle(Vector3.ProjectOnPlane(before,Vector3.up),Vector3.ProjectOnPlane(after,Vector3.up),Vector3.up);
        checks.Add(new {test="E orbits right",pass=e>1f,degrees=e});
        InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState(Key.Q,Key.E)); var simultaneous=camera.transform.position; await Frames(20);InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState());await Frames(10);
        checks.Add(new {test="Q+E cancel",pass=Vector3.Distance(simultaneous,camera.transform.position)<.1f});
        var p=nav.pivot;await KeyHold(Key.W,10);checks.Add(new {test="Pan works after orbit",pass=Vector3.Distance(p,nav.pivot)>.05f});
        float distance=Vector3.Distance(camera.transform.position,nav.pivot);InputSystem.QueueDeltaStateEvent(Mouse.current.scroll,new Vector2(0,120)); await Frames(60);checks.Add(new {test="Zoom works after orbit",pass=Vector3.Distance(camera.transform.position,nav.pivot)<distance-.1f});
        var focus=camera.GetComponent<DoroCenterFocus>();var ray=camera.ViewportPointToRay(new Vector3(.5f,.5f,0));bool hit=Physics.Raycast(ray,out var h,250,focus.focusLayers,QueryTriggerInteraction.Collide);checks.Add(new {test="Autofocus follows rotated view",pass=hit && Mathf.Abs(focus.CurrentDepth-Vector3.Dot(h.point-camera.transform.position,camera.transform.forward))<.3f,subject=focus.FocusSubject});
        InputSystem.QueueStateEvent(Keyboard.current,new KeyboardState()); nav.pivot=pivot;field.SetValue(nav,direction);typeof(DoroPanZoom).GetField("distance",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).SetValue(nav,(start-pivot).magnitude);camera.transform.position=start;camera.transform.LookAt(pivot);await Frames(30);
        var json=Newtonsoft.Json.JsonConvert.SerializeObject(checks,Newtonsoft.Json.Formatting.Indented);System.IO.File.WriteAllText("DoroBackups/2026-10-26/orbit-verification.json",json);return json;
    }
}
