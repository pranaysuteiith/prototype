using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Doro.PaintedCity
{
    [DefaultExecutionOrder(200)]
    [RequireComponent(typeof(Camera))]
    public sealed class DoroCenterFocus : MonoBehaviour
    {
        [Tooltip("Assign the global URP Volume. Its profile is cloned by Volume.profile at runtime.")]
        public Volume volume;
        public Transform focusMarker;
        public LayerMask focusLayers = ~0;
        [Min(.01f)] public float focusResponse = 6f;
        [Min(.1f)] public float maxRayDistance = 250f;
        public float groundHeight = 0f;
        [Range(1f, 32f)] public float aperture = 1f;
        [Range(1f, 300f)] public float artisticFocalLength = 300f;
        public bool depthOfFieldEnabled = true;

        public string FocusSubject { get; private set; }
        public float CurrentDepth => currentDepth;
        Camera view;
        DepthOfField dof;
        float currentDepth;
        Vector3 lastPoint;

        void Start()
        {
            view = GetComponent<Camera>();
            view.GetUniversalAdditionalCameraData().renderPostProcessing = true;
            if (!volume || !volume.profile)
            {
                Debug.LogWarning("Doro: assign a URP Volume to enable autofocus blur.", this);
                enabled = false;
                return;
            }
            if (!volume.profile.TryGet(out dof))
                dof = volume.profile.Add<DepthOfField>(true);
            dof.mode.Override(DepthOfFieldMode.Bokeh);
            dof.aperture.Override(aperture);
            dof.focalLength.Override(artisticFocalLength);
            lastPoint = focusMarker ? focusMarker.position : transform.position + transform.forward * 45f;
            currentDepth = Mathf.Max(.1f, Vector3.Dot(lastPoint - transform.position, transform.forward));
            dof.focusDistance.Override(currentDepth);
        }

        void LateUpdate()
        {
            if (dof == null) return;
#if ENABLE_INPUT_SYSTEM
            if (UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.bKey.wasPressedThisFrame) depthOfFieldEnabled = !depthOfFieldEnabled;
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKeyDown(KeyCode.B)) depthOfFieldEnabled = !depthOfFieldEnabled;
#endif
            Ray ray = view.ViewportPointToRay(new Vector3(.5f, .5f, 0));
            if (Physics.Raycast(ray, out var hit, maxRayDistance, focusLayers, QueryTriggerInteraction.Collide))
                { lastPoint = hit.point; FocusSubject = hit.collider.name; }
            else
            {
                var ground = new Plane(Vector3.up, new Vector3(0, groundHeight, 0));
                if (ground.Raycast(ray, out float distance) && distance <= maxRayDistance)
                    { lastPoint = ray.GetPoint(distance); FocusSubject = "Ground plane fallback"; }
            }
            // DOF wants camera-forward depth, not hit.distance (ray starts on the near plane).
            float targetDepth = Mathf.Clamp(Vector3.Dot(lastPoint - transform.position, transform.forward), .1f, maxRayDistance);
            float response = 1f - Mathf.Exp(-focusResponse * Time.unscaledDeltaTime);
            currentDepth = Mathf.Lerp(currentDepth, targetDepth, response);
            dof.focusDistance.Override(currentDepth);
            dof.active = depthOfFieldEnabled;
            if (focusMarker) focusMarker.position = Vector3.Lerp(focusMarker.position, lastPoint, response);
        }
    }
}
