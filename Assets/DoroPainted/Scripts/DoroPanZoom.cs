using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Doro.PaintedCity
{
    [DefaultExecutionOrder(100)]
    [RequireComponent(typeof(Camera))]
    public sealed class DoroPanZoom : MonoBehaviour
    {
        public Vector3 pivot = new Vector3(-1.1f, 2.2f, -.2f);
        public Vector2 panXBounds = new Vector2(-12f, 13f);
        public Vector2 panZBounds = new Vector2(-12f, 12f);
        public float minDistance = 18f;
        public float maxDistance = 68f;
        public float keyboardSpeed = 7f;
        [Tooltip("Disable when arrow keys control the playable character. WASD still pans.")]
        public bool useArrowKeys = true;
        public Transform followTarget;
        Vector3 previousFollowPosition;
        [Tooltip("Q/E orbit speed in degrees per second.")]
        public float rotationSpeed = 60f;
        public float response = 12f;
        Vector3 viewDirection;
        float distance;
        float previousPinch;
        bool wasTwoFinger;

        void Start()
        {
            Vector3 offset = transform.position - pivot;
            distance = Mathf.Clamp(offset.magnitude, minDistance, maxDistance);
            viewDirection = offset.normalized;
            if (followTarget) previousFollowPosition = followTarget.position;
        }

        void LateUpdate()
        {
            Vector2 keys = Vector2.zero;
            Vector2 drag = Vector2.zero;
            float scroll = 0f;
            float orbit = 0f;
            bool twoFinger = false;
#if ENABLE_INPUT_SYSTEM
            if (Keyboard.current != null)
            {
                var k = Keyboard.current;
                orbit = (k.eKey.isPressed ? 1f : 0f) - (k.qKey.isPressed ? 1f : 0f);
                keys.x = ((k.dKey.isPressed || (useArrowKeys && k.rightArrowKey.isPressed)) ? 1 : 0) - ((k.aKey.isPressed || (useArrowKeys && k.leftArrowKey.isPressed)) ? 1 : 0);
                keys.y = ((k.wKey.isPressed || (useArrowKeys && k.upArrowKey.isPressed)) ? 1 : 0) - ((k.sKey.isPressed || (useArrowKeys && k.downArrowKey.isPressed)) ? 1 : 0);
            }
            if (Mouse.current != null)
            {
                var m = Mouse.current;
                if (m.middleButton.isPressed || m.rightButton.isPressed) drag = m.delta.ReadValue();
                scroll = m.scroll.ReadValue().y / 120f;
            }
            if (Touchscreen.current != null)
            {
                var touches = Touchscreen.current.touches;
                int a = -1, b = -1;
                for (int i = 0; i < touches.Count; i++)
                    if (touches[i].press.isPressed) { if (a < 0) a = i; else { b = i; break; } }
                if (a >= 0 && b >= 0)
                {
                    twoFinger = true;
                    float pinch = Vector2.Distance(touches[a].position.ReadValue(), touches[b].position.ReadValue());
                    if (wasTwoFinger) distance *= Mathf.Exp(-(pinch - previousPinch) * .003f);
                    previousPinch = pinch;
                    drag = (touches[a].delta.ReadValue() + touches[b].delta.ReadValue()) * .5f;
                }
                else if (a >= 0) drag = touches[a].delta.ReadValue();
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            keys = new Vector2(((Input.GetKey(KeyCode.D) || (useArrowKeys && Input.GetKey(KeyCode.RightArrow))) ? 1 : 0) - ((Input.GetKey(KeyCode.A) || (useArrowKeys && Input.GetKey(KeyCode.LeftArrow))) ? 1 : 0),
                               ((Input.GetKey(KeyCode.W) || (useArrowKeys && Input.GetKey(KeyCode.UpArrow))) ? 1 : 0) - ((Input.GetKey(KeyCode.S) || (useArrowKeys && Input.GetKey(KeyCode.DownArrow))) ? 1 : 0));
            orbit = (Input.GetKey(KeyCode.E) ? 1f : 0f) - (Input.GetKey(KeyCode.Q) ? 1f : 0f);
            if (Input.GetMouseButton(2) || Input.GetMouseButton(1)) drag = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y")) * 12f;
            scroll = Input.mouseScrollDelta.y;
#endif
            wasTwoFinger = twoFinger;
            if (followTarget)
            {
                Vector3 movement = followTarget.position - previousFollowPosition;
                pivot += Vector3.ProjectOnPlane(movement, Vector3.up);
                previousFollowPosition = followTarget.position;
            }
            viewDirection = Quaternion.AngleAxis(orbit * rotationSpeed * Time.unscaledDeltaTime, Vector3.up) * viewDirection;
            distance = Mathf.Clamp(distance * Mathf.Exp(-scroll * .12f), minDistance, maxDistance);
            Vector3 right = Vector3.ProjectOnPlane(transform.right, Vector3.up).normalized;
            Vector3 forward = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            pivot += (right * keys.x + forward * keys.y) * keyboardSpeed * Time.unscaledDeltaTime;
            pivot -= (right * drag.x + forward * drag.y) * distance * .00085f;
            pivot.x = Mathf.Clamp(pivot.x, panXBounds.x, panXBounds.y);
            pivot.z = Mathf.Clamp(pivot.z, panZBounds.x, panZBounds.y);
            Vector3 target = pivot + viewDirection * distance;
            transform.position = Vector3.Lerp(transform.position, target, 1f - Mathf.Exp(-response * Time.unscaledDeltaTime));
            // Look at the pivot throughout the smoothed orbit, keeping autofocus centered.
            transform.rotation = Quaternion.LookRotation(pivot - transform.position, Vector3.up);
        }
    }
}
