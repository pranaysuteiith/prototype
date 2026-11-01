using System;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
public static class DoroDancerGround
{
    public static async Task<string> Run()
    {
        var done=new TaskCompletionSource<string>();
        void Apply()
        {
            try
            {
                var child=GameObject.Find("Belly Dancing Girl");if(!child)throw new Exception("Dancer missing");
                Undo.RecordObject(child.transform,"Ground dancer feet on road");child.transform.position-=Vector3.up*.094f;
                PrefabUtility.RecordPrefabInstancePropertyModifications(child.transform);
                EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());AssetDatabase.SaveAssets();
                done.TrySetResult("Saved shoe-height correction at "+child.transform.position);
            }
            catch(Exception ex){done.TrySetException(ex);}
        }
        if(EditorApplication.isPlayingOrWillChangePlaymode)
        {
            Action<PlayModeStateChange> handler=null;
            handler=state=>{if(state==PlayModeStateChange.EnteredEditMode){EditorApplication.playModeStateChanged-=handler;Apply();}};
            EditorApplication.playModeStateChanged+=handler;EditorApplication.ExitPlaymode();
        }
        else Apply();
        return await done.Task;
    }
}
