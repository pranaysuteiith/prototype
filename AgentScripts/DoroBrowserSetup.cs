using System;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Doro.PaintedCity;
public static class DoroBrowserSetup
{
    public static string Run()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Exit Play mode before saving browser setup");
        var root=GameObject.Find("Doro Painted Cafe - Imported");var audio=root.GetComponent<DoroAmbientSound>() ?? root.AddComponent<DoroAmbientSound>();
        audio.parkBirds=AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/DoroPainted/Audio/ParkBirds.wav");
        audio.distantDog=AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/DoroPainted/Audio/DistantDog.wav");
        foreach(var path in new[]{"Assets/DoroPainted/Audio/ParkBirds.wav","Assets/DoroPainted/Audio/DistantDog.wav"})
        {
            var importer=(AudioImporter)AssetImporter.GetAtPath(path);var settings=importer.defaultSampleSettings;
            settings.compressionFormat=AudioCompressionFormat.Vorbis;settings.quality=.55f;settings.loadType=AudioClipLoadType.DecompressOnLoad;
            importer.defaultSampleSettings=settings;importer.forceToMono=true;importer.SaveAndReimport();
        }
        EditorUtility.SetDirty(audio);EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;PlayerSettings.WebGL.decompressionFallback=true;
        PlayerSettings.WebGL.initialMemorySize=256;PlayerSettings.WebGL.maximumMemorySize=1024;PlayerSettings.WebGL.dataCaching=true;
        AssetDatabase.SaveAssets();return "Saved browser audio and WebGL settings";
    }
}
