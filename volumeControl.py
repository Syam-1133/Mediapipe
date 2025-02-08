import cv2
import mediapipe as mp
import math
import os

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

# Function to draw volume bar
def draw_volume_bar(frame, volume_level):
    # Volume bar dimensions
    bar_width = 400
    bar_height = 30
    bar_x = 50
    bar_y = 50

    # Draw a red background for the volume bar
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (0, 0, 255), -1)

    # Draw the volume bar with gradient effect (pink to red)
    volume_width = int((volume_level / 100) * bar_width)
    bar_color_start = (255, 105, 180)  # Pink
    bar_color_end = (0, 0, 255)        # Red

    # Interpolate the color from pink to red based on the volume level
    bar_color = tuple(
        [int(bar_color_start[i] + (bar_color_end[i] - bar_color_start[i]) * (volume_level / 100)) for i in range(3)]
    )

    # Draw the volume progress
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + volume_width, bar_y + bar_height), bar_color, -1)

    # Display volume percentage inside the bar
    cv2.putText(frame, f"{int(volume_level)}%", (bar_x + bar_width + 10, bar_y + bar_height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Use MediaPipe Hands
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the image horizontally for a mirrored view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get landmark positions for thumb tip and index tip
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Convert normalized coordinates to pixel values
                h, w, _ = frame.shape
                thumb_tip_coords = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                index_tip_coords = (int(index_tip.x * w), int(index_tip.y * h))

                # Draw a line between the thumb and index tip
                cv2.line(frame, thumb_tip_coords, index_tip_coords, (0, 255, 0), 3)  # Green line

                # Calculate the Euclidean distance between thumb tip and index tip
                distance = math.sqrt(
                    (thumb_tip.x - index_tip.x) ** 2 +
                    (thumb_tip.y - index_tip.y) ** 2 +
                    (thumb_tip.z - index_tip.z) ** 2
                )

                # Map the distance to volume level (0 to 100)
                volume_level = int(min(max(distance * 500, 0), 100))  # Maps distance to volume (0-100)

                # Use osascript to change the system volume on macOS
                os.system(f"osascript -e 'set volume output volume {volume_level}'")

                # Draw the volume bar on the screen
                draw_volume_bar(frame, volume_level)

        # Show the frame
        cv2.imshow("Hand Gesture Volume Control", frame)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()



