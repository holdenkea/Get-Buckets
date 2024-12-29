import cv2
import mediapipe as mp
import numpy as np

# fucntion to calculate an angle for any 3 points
def calculateAngle(a,b,c):
    # convert points to numpy arrays
    a = np.array(a) # First
    b = np.array(b) # Middle
    c = np.array(c) # End

    # calculates radians for a particular joint
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi) 

    # converts to an angle between 0 and 180 degrees
    if angle > 180.0:
        angle = 360-angle

    return angle


# main logic starts here
mp_drawing = mp.solutions.drawing_utils     # drawing utilities
mp_pose = mp.solutions.pose                 # importing pose estimation model

# video feed
cap = cv2.VideoCapture(0)

# setting up mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:   # detection and tracking confidence can be changed
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # recoloring frame to RGB to pass to mediapipe
        image.flags.writeable = False   # flags set to false for better performace

        # detection made here
        results = pose.process(image)

        image.flags.writeable = True    # setting flags back to true after detection
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # recoloring image back to BGR for cv2
  
        # extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # x and y coordinates for left shoulder, elbow, and wrist
            L_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        
            L_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            L_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # calculate angle
            angle = calculateAngle(L_shoulder, L_elbow, L_wrist)
            
            # Using putText to pass the image from webcam, calculated angle, and location of elbow coodinates
            cv2.putText(image, str(angle),
                            tuple(np.multiply(L_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA
                        )

            # print(landmarks)

        except:
            pass

        # render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('MediaPipe Feed', image)

        # quit camera feed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()





