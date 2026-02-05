import mediapipe as mp
import sys

print("--- Diagnostic Report ---")
print(f"Python Version: {sys.version}")
print(f"MediaPipe Location: {mp.__file__}")
print(f"Available in mp: {dir(mp)}")

try:
    pose = mp.solutions.pose.Pose()
    print("✅ Success: MediaPipe Pose initialized!")
except AttributeError as e:
    print(f"❌ Error: {e}")