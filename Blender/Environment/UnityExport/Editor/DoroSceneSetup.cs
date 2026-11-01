using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Doro.PaintedCity.Editor
{
    public static class DoroSceneSetup
    {
        const string Root = "Assets/DoroPainted";

        [MenuItem("Doro/Create Painted Crossroads Scene")]
        public static void CreateScene()
        {
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) throw new InvalidOperationException("This scene requires a URP project.");
            string modelPath = Root + "/Models/DoroCrossroads.fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            if (model == null) throw new InvalidOperationException("Place this kit in Assets/DoroPainted first.");
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EnsureFolder(Root + "/Materials");
            EnsureFolder(Root + "/Settings");
            EnsureFolder(Root + "/Scenes");

            var world = (GameObject)PrefabUtility.InstantiatePrefab(model);
            world.name = "Doro Painted Crossroads";
            world.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            var materials = new Dictionary<string, Material>();
            foreach (var renderer in world.GetComponentsInChildren<MeshRenderer>())
            {
                var shared = renderer.sharedMaterials;
                for (int i = 0; i < shared.Length; i++)
                {
                    string name = shared[i] ? shared[i].name : "Doro_Painted_Atlas";
                    if (!materials.TryGetValue(name, out var material))
                    {
                        material = CreateMaterial(name, shader);
                        materials.Add(name, material);
                    }
                    shared[i] = material;
                }
                renderer.sharedMaterials = shared;
            }

            // Invisible simplified colliders serve autofocus, without collision on every leaf or chair slat.
            var proxies = new GameObject("Focus Colliders");
            foreach (var renderer in world.GetComponentsInChildren<MeshRenderer>())
            {
                string name = renderer.name;
                if (name.Contains("Roads_and_Street") || name.Contains("Terrace") || name.Contains("Ivy_and_Garden")) continue;
                Bounds b = renderer.bounds;
                if (b.size.sqrMagnitude > .01f) AddProxy(proxies.transform, name, b.center, b.size);
            }
            AddProxy(proxies.transform, "Ground", new Vector3(0, -.03f, 0), new Vector3(37f, .1f, 33f));
            AddProxy(proxies.transform, "Terrace floor", new Vector3(-2.6f, .22f, -3.9f), new Vector3(14.1f, .1f, 16.7f));
            AddProxy(proxies.transform, "Cafe table west", new Vector3(-6.1f, .7f, -1f), new Vector3(1.5f, .8f, 1.2f));
            AddProxy(proxies.transform, "Cafe table parasol", new Vector3(-6.5f, .7f, -3f), new Vector3(1.5f, .8f, 1.2f));
            AddProxy(proxies.transform, "Picnic table", new Vector3(-.8f, .8f, 2.1f), new Vector3(2.7f, .7f, 1.1f));

            var cameraObject = new GameObject("Doro Game Camera", typeof(Camera), typeof(AudioListener));
            cameraObject.tag = "MainCamera";
            var camera = cameraObject.GetComponent<Camera>();
            cameraObject.transform.position = new Vector3(26f, 29f, 34f);
            var target = new Vector3(-1.1f, 2.2f, -.2f);
            cameraObject.transform.LookAt(target);
            camera.fieldOfView = 19.157f;
            camera.nearClipPlane = .1f;
            camera.farClipPlane = 250f;
            camera.backgroundColor = new Color(.69f, .73f, .73f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            var additional = camera.GetUniversalAdditionalCameraData();
            additional.renderPostProcessing = true;
            additional.requiresDepthTexture = true;
            cameraObject.AddComponent<DoroPanZoom>().pivot = target;

            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(Root + "/Settings/DoroPaintedVolume.asset");
            if (!profile)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, Root + "/Settings/DoroPaintedVolume.asset");
            }
            if (!profile.TryGet(out DepthOfField depth)) depth = profile.Add<DepthOfField>(true);
            depth.mode.Override(DepthOfFieldMode.Bokeh);
            depth.focusDistance.Override(Vector3.Distance(camera.transform.position, target));
            depth.aperture.Override(1f);
            depth.focalLength.Override(220f);
            if (!profile.TryGet(out Tonemapping tone)) tone = profile.Add<Tonemapping>(true);
            tone.mode.Override(TonemappingMode.Neutral);
            if (!profile.TryGet(out ColorAdjustments color)) color = profile.Add<ColorAdjustments>(true);
            color.saturation.Override(6f);
            var volume = new GameObject("Doro Global Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = profile;
            var focusMarker = new GameObject("Focus Target - follows screen center");
            focusMarker.transform.position = target;
            var focus = cameraObject.AddComponent<DoroCenterFocus>();
            focus.volume = volume;
            focus.focusMarker = focusMarker.transform;

            var sun = new GameObject("Warm Afternoon Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.3f;
            sun.color = new Color(1f, .91f, .78f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(48f, -38f, 0);
            RenderSettings.sun = sun;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.65f, .72f, .78f);
            RenderSettings.ambientEquatorColor = new Color(.53f, .56f, .50f);
            RenderSettings.ambientGroundColor = new Color(.34f, .31f, .25f);
            AssetDatabase.SaveAssets();
            EditorSceneManager.SaveScene(scene, Root + "/Scenes/DoroCrossroads.unity");
            Selection.activeGameObject = world;
            Debug.Log("Doro painted crossroads created. Play: WASD/arrows, middle/right drag, wheel; mobile drag and pinch with Input System.");
        }

        static Material CreateMaterial(string name, Shader shader)
        {
            string path = Root + "/Materials/" + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!material) { material = new Material(shader) { name = name }; AssetDatabase.CreateAsset(material, path); }
            material.shader = shader;
            string texture = name.StartsWith("Doro_Leaf_") ? "Doro_Gouache_Leaf_" + name.Substring("Doro_Leaf_".Length) : "Doro_Painted_Atlas";
            var image = AssetDatabase.LoadAssetAtPath<Texture2D>(Root + "/Textures/" + texture + ".png");
            material.SetTexture("_BaseMap", image);
            material.SetColor("_BaseColor", Color.white);
            material.SetFloat("_Smoothness", .08f);
            material.SetFloat("_Metallic", 0f);
            if (name.StartsWith("Doro_Leaf_")) material.SetInt("_Cull", (int)CullMode.Off);
            if (name == "Doro_Warm_Window")
            {
                material.SetTexture("_BaseMap", null);
                material.SetColor("_BaseColor", new Color(.85f, .48f, .11f));
                material.EnableKeyword("_EMISSION");
                material.SetColor("_EmissionColor", new Color(.28f, .14f, .035f));
            }
            EditorUtility.SetDirty(material);
            return material;
        }

        static void AddProxy(Transform parent, string name, Vector3 center, Vector3 size)
        {
            var proxy = new GameObject("FocusProxy_" + name);
            proxy.transform.SetParent(parent, false);
            proxy.transform.position = center;
            proxy.AddComponent<BoxCollider>().size = size;
        }

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
