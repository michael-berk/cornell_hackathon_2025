import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk

# Initialize MediaPipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Setup Tkinter window
window = tk.Tk()
window.title("Eye Tracker")
window.attributes('-topmost', True)
window.geometry("800x600")
canvas = tk.Canvas(window, width=800, height=600, bg="black")
canvas.pack()

# Open webcam
cap = cv2.VideoCapture(0)

def get_eye_center(landmarks, indices):
    """Get the average position of eye landmarks."""
    points = np.array([(landmarks[i].x, landmarks[i].y) for i in indices])
    return np.mean(points, axis=0)

def update():
    """Capture frame, detect eyes, and update red dot position."""
    ret, frame = cap.read()
    if not ret:
        return
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # Eye landmark indices (MediaPipe reference)
        left_eye = [362, 385, 387, 263]
        right_eye = [33, 160, 158, 133]

        left_center = get_eye_center(landmarks, left_eye)
        right_center = get_eye_center(landmarks, right_eye)

        # Average both eyes for gaze estimation
        gaze_x = (left_center[0] + right_center[0]) / 2
        gaze_y = (left_center[1] + right_center[1]) / 2

        # Convert to screen coordinates
        screen_x = int(gaze_x * 800)
        screen_y = int(gaze_y * 600)

        canvas.delete("all")
        canvas.create_oval(screen_x - 10, screen_y - 10, screen_x + 10, screen_y + 10, fill="red")

    window.after(10, update)

# Start tracking
window.after(10, update)
window.mainloop()

cap.release()
cv2.destroyAllWindows()
