using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Doro.PaintedCity
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class DoroBoyWalker : MonoBehaviour
    {
        public Camera movementCamera;
        public Animator animator;
        public float walkSpeed = 1.25f;
        public float acceleration = 10f;
        public float turnSpeed = 540f;
        public float gravity = -18f;
        CharacterController controller;
        Vector3 planarVelocity;
        float verticalVelocity;
        bool walking;
        const string Idle = "ARM_Boy_GreenSweater|ANIM_Idle";
        const string Walk = "ARM_Boy_GreenSweater|ANIM_Walk";

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            if (!animator) animator = GetComponentInChildren<Animator>();
            if (!movementCamera) movementCamera = Camera.main;
            if (animator) { animator.applyRootMotion = false; animator.Play(Idle); }
        }

        void Update()
        {
            Vector2 input = Vector2.zero;
#if ENABLE_INPUT_SYSTEM
            var k = Keyboard.current;
            if (k != null)
                input = new Vector2((k.rightArrowKey.isPressed ? 1 : 0) - (k.leftArrowKey.isPressed ? 1 : 0),
                                    (k.upArrowKey.isPressed ? 1 : 0) - (k.downArrowKey.isPressed ? 1 : 0));
#elif ENABLE_LEGACY_INPUT_MANAGER
            input = new Vector2((Input.GetKey(KeyCode.RightArrow) ? 1 : 0) - (Input.GetKey(KeyCode.LeftArrow) ? 1 : 0),
                                (Input.GetKey(KeyCode.UpArrow) ? 1 : 0) - (Input.GetKey(KeyCode.DownArrow) ? 1 : 0));
#endif
            Vector3 right = movementCamera ? Vector3.ProjectOnPlane(movementCamera.transform.right, Vector3.up).normalized : Vector3.right;
            Vector3 forward = movementCamera ? Vector3.ProjectOnPlane(movementCamera.transform.forward, Vector3.up).normalized : Vector3.forward;
            Vector3 desired = (right * input.x + forward * input.y).normalized * (input.sqrMagnitude > 0 ? walkSpeed : 0);
            planarVelocity = Vector3.MoveTowards(planarVelocity, desired, acceleration * Time.deltaTime);
            if (controller.isGrounded && verticalVelocity < 0) verticalVelocity = -2f;
            verticalVelocity += gravity * Time.deltaTime;
            Vector3 before = transform.position;
            controller.Move((planarVelocity + Vector3.up * verticalVelocity) * Time.deltaTime);
            Vector3 travelled = Vector3.ProjectOnPlane(transform.position - before, Vector3.up);
            if (desired.sqrMagnitude > .01f)
                transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(desired), turnSpeed * Time.deltaTime);
            bool moving = travelled.sqrMagnitude > .000001f;
            if (animator) animator.speed = moving ? Mathf.Clamp(travelled.magnitude / Mathf.Max(Time.deltaTime, .0001f) / .6f, .8f, 2.2f) : 1f;
            if (animator && moving != walking)
            {
                animator.CrossFadeInFixedTime(moving ? Walk : Idle, .12f);
                walking = moving;
            }
        }
    }
}
