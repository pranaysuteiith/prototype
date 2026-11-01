# Belly dancer — road performance

Source: `/Users/pranay/Downloads/Belly Dance.fbx` (source file preserved).

Added to the existing `Assets/Scenes/GetStarted_Scene.unity` beneath `Doro Painted Cafe - Imported / Belly Dancer - Road Performance`, at Unity position (-3.4, 0.08, 5.5): the road/crossing immediately beyond the curb, in front of the traffic signal near the TODAY / COFFEE & CAKE sandwich board.

The character uses the FBX's own Generic rig and `mixamo.com` dance (19.633 seconds), looping with root motion disabled. Idle, walk and wave clips remain available but do not play. Twelve URP materials preserve the supplied colors; the embedded face image is extracted and assigned. Character scale is matched to the café's existing pedestrians. A trigger-only capsule lets center-screen focus detect her.

The scene was backed up before editing under `DoroBackups/2026-10-28/before-belly-dancer`. Delete the single `Belly Dancer - Road Performance` root to remove her. `AgentScripts/DoroDancerSetup.cs` records the import/placement steps; `DoroDancerVerify.cs` records the Play-mode check. Verification results: `DoroBackups/2026-10-28/dancer-verification.json`.

This change is saved in the Unity scene. The previously deployed browser build is a separate snapshot and has not been rebuilt by this scene-edit operation.
