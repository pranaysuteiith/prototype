using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif
namespace Doro.PaintedCity
{
    public sealed class DoroAmbientSound : MonoBehaviour
    {
        public AudioClip parkBirds;
        public AudioClip distantDog;
        [Range(0,1)] public float masterVolume = .65f;
        [Range(0,1)] public float birdsVolume = .5f;
        [Range(0,1)] public float dogVolume = .12f;
        public Vector2 barkInterval = new Vector2(35f,65f);
        public bool muted;
        AudioSource birds, dog;
        float nextBark;
        float fade;
        public bool BirdsPlaying => birds && birds.isPlaying;
        public int BarkCount { get; private set; }
        void Start()
        {
            birds = gameObject.AddComponent<AudioSource>();
            birds.clip = parkBirds; birds.loop = true; birds.spatialBlend = 0; birds.playOnAwake = false; birds.volume = 0;
            dog = gameObject.AddComponent<AudioSource>(); dog.clip = distantDog; dog.spatialBlend = 0; dog.playOnAwake = false;
            if (parkBirds) birds.Play();
            nextBark = Time.unscaledTime + Random.Range(18f,28f);
        }
        void Update()
        {
#if ENABLE_INPUT_SYSTEM
            if (Keyboard.current != null && Keyboard.current.mKey.wasPressedThisFrame) muted = !muted;
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKeyDown(KeyCode.M)) muted = !muted;
#endif
            fade = Mathf.MoveTowards(fade, 1f, Time.unscaledDeltaTime / 4f);
            float level = muted ? 0 : masterVolume * fade;
            birds.volume = birdsVolume * level;
            dog.volume = dogVolume * level;
            if (Time.unscaledTime >= nextBark)
            {
                if (!muted && distantDog) PlayDistantBark();
                nextBark = Time.unscaledTime + Random.Range(barkInterval.x,barkInterval.y);
            }
        }
        public void SetVolume(string value) { if (float.TryParse(value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float v)) masterVolume = Mathf.Clamp01(v); }
        public void SetMuted(string value) { muted = value == "1" || value == "true"; }
        public void SetBlur(string value) { var focus = GetComponentInChildren<DoroCenterFocus>(); if (focus) focus.depthOfFieldEnabled = value == "1" || value == "true"; }
        public void PlayDistantBark() { if (!dog || !distantDog || muted) return; dog.pitch = Random.Range(.92f,1.04f); dog.PlayOneShot(distantDog); BarkCount++; }
        void OnDisable() { if (birds) birds.Stop(); if (dog) dog.Stop(); }
    }
}
