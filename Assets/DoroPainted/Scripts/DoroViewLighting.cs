using UnityEngine;
using UnityEngine.Rendering;
namespace Doro.PaintedCity
{
    // Apply studio illumination only while this camera renders, then restore the scene.
    [ExecuteAlways, RequireComponent(typeof(Camera))]
    public sealed class DoroViewLighting : MonoBehaviour
    {
        public Light cafeSun;
        Light previousSun;
        UnityEngine.Rendering.SphericalHarmonicsL2 previousAmbient;
        bool applied;
        bool previousEnabled;
        void OnEnable() { RenderPipelineManager.beginCameraRendering += Begin; RenderPipelineManager.endCameraRendering += End; }
        void OnDisable() { RenderPipelineManager.beginCameraRendering -= Begin; RenderPipelineManager.endCameraRendering -= End; Restore(); }
        void Begin(ScriptableRenderContext context, Camera camera)
        {
            if (camera != GetComponent<Camera>() || !cafeSun) return;
            previousSun = RenderSettings.sun;
            previousEnabled = cafeSun.enabled;
            cafeSun.enabled = true;
            previousAmbient = RenderSettings.ambientProbe;
            RenderSettings.sun = cafeSun;
            var ambient = new SphericalHarmonicsL2();
            ambient.AddAmbientLight(new Color(.38f, .36f, .30f));
            RenderSettings.ambientProbe = ambient;
            applied = true;
        }
        void End(ScriptableRenderContext context, Camera camera) { if (camera == GetComponent<Camera>()) Restore(); }
        void Restore() { if (!applied) return; RenderSettings.sun = previousSun; RenderSettings.ambientProbe = previousAmbient; if (cafeSun) cafeSun.enabled = previousEnabled; applied = false; }
    }
}
