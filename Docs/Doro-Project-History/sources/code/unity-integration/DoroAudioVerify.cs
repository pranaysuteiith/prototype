using System;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using Doro.PaintedCity;
public static class DoroAudioVerify
{
    public static async Task<string> Run()
    {
        var a=GameObject.Find("Doro Painted Cafe - Imported").GetComponent<DoroAmbientSound>();
        await Task.Delay(700); bool birds=a.BirdsPlaying;
        a.SetVolume("0.4");bool volume=Mathf.Approximately(a.masterVolume,.4f);
        int beforeBarks=a.BarkCount;a.PlayDistantBark();await Task.Delay(200);bool bark=a.BarkCount==beforeBarks+1;
        a.SetMuted("1");await Task.Delay(150); bool mute=Array.TrueForAll(a.GetComponents<AudioSource>(),s=>Mathf.Approximately(s.volume,0));
        a.SetMuted("0");a.SetVolume("0.65");await Task.Delay(400);
        float[] samples=new float[1024];a.parkBirds.GetData(samples,0);float power=0;foreach(float s in samples)power+=s*s;
        var json=Newtonsoft.Json.JsonConvert.SerializeObject(new {birdsLooping=birds,quietBarkPlays=bark,volumeControl=volume,muteStopsOutput=mute,decodedClipHasSignal=power>0,birdsSeconds=a.parkBirds.length,dogSeconds=a.distantDog.length,master=a.masterVolume,barkEvery=a.barkInterval.ToString()},Newtonsoft.Json.Formatting.Indented);
        System.IO.File.WriteAllText("DoroBackups/2026-10-26/audio-verification.json",json);return json;
    }
}
