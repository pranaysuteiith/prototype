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
        public float groundHeight = .25f;
        [Range(1f, 32f)] public float aperture = 1f;
        [Range(1f, 300f)] public float artisticFocalLength = 220f;
        public bool depthOfFieldEnabled = true;

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
            Ray ray = view.ViewportPointToRay(new Vector3(.5f, .5f, 0));
            if (Physics.Raycast(ray, out var hit, maxRayDistance, focusLayers, QueryTriggerInteraction.Ignore))
                lastPoint = hit.point;
            else
            {
                var ground = new Plane(Vector3.up, new Vector3(0, groundHeight, 0));
                if (ground.Raycast(ray, out float distance) && distance <= maxRayDistance)
                    lastPoint = ray.GetPoint(distance);
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
