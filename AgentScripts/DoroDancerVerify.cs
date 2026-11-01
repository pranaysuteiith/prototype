using System;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
public static class DoroDancerVerify
{
    public static async Task<string> Run()
    {
        var root=GameObject.Find("Belly Dancer - Road Performance");var animator=root.GetComponentInChildren<Animator>();
        var bone=root.GetComponentsInChildren<Transform>().First(t=>t.name=="Hand.L");
        var start=bone.position;int frame=Time.frameCount;await Task.Delay(900);var after=bone.position;
        var state=animator.GetCurrentAnimatorStateInfo(0);bool advancing=Time.frameCount>frame&&Vector3.Distance(start,after)>.001f;
        var clip=animator.runtimeAnimatorController.animationClips.First(c=>c.name=="mixamo.com");
        var shoes=root.GetComponentsInChildren<SkinnedMeshRenderer>().First(r=>r.name=="CH_Shoes");var baked=new Mesh();
        float low=float.PositiveInfinity,high=float.NegativeInfinity,maxDrift=0;var anchor=root.transform.position;
        animator.Play("Belly Dance - Loop",0,0);animator.Update(0);
        for(int i=0;i<200;i++)
        {
            animator.Update(clip.length/190f);shoes.BakeMesh(baked);
            float bottom=float.PositiveInfinity;foreach(var v in baked.vertices)bottom=Mathf.Min(bottom,shoes.transform.TransformPoint(v).y);
            low=Mathf.Min(low,bottom);high=Mathf.Max(high,bottom);maxDrift=Mathf.Max(maxDrift,Vector3.Distance(anchor,root.transform.position));
        }
        var normalized=animator.GetCurrentAnimatorStateInfo(0).normalizedTime;
        animator.Play("Belly Dance - Loop",0,.35f);animator.Update(0);
        UnityEngine.Object.Destroy(baked);
        var materials=root.GetComponentsInChildren<SkinnedMeshRenderer>().SelectMany(r=>r.sharedMaterials).Distinct().ToArray();
        var json=Newtonsoft.Json.JsonConvert.SerializeObject(new {animationAdvances=advancing,clip=clip.name,clip.length,loop=clip.isLooping,loopCrossed=normalized>1,position=root.transform.position.ToString(),rootDrift=maxDrift,footFloorMin=low,footFloorMax=high,materialsValid=materials.All(m=>m&&m.shader.isSupported&&m.shader.name=="Universal Render Pipeline/Lit"),materials=materials.Length,meshCount=root.GetComponentsInChildren<SkinnedMeshRenderer>().Length},Newtonsoft.Json.Formatting.Indented);
        System.IO.File.WriteAllText("DoroBackups/2026-10-28/dancer-verification.json",json);return json;
    }
}
