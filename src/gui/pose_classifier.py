import tensorflow as tf
import cv2
import mediapipe as mp
import numpy as np


class Pose_Classifier:
    def __init__(self, app_instance, data_reader, position_action_queue):
        # action
        self.action = "None"

        # define mediapipe utils
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose_videos = mp.solutions.pose.Pose(static_image_mode=False, min_detection_confidence=0.50, min_tracking_confidence=0.50)

        # using the best models from the google colab research 
        self.final_shooting_model = tf.keras.models.load_model("src/models/new_FINAL_best_shooting_model.h5")
        self.final_movement_model = tf.keras.models.load_model("src/models/new_FINAL_best_movement_model.h5")

        # predicts every window_size frames with an overlap of overlap frames
        self.window_size = 60
        self.overlap = 20
        self.stride = self.window_size - self.overlap

        # app instance for checking stop_requested
        self.app_instance = app_instance

        # refrence ot the data reader thread
        self.data_reader = data_reader

        self.position_action_queue = position_action_queue

    # this function pads or truncates a video to 150 frames
    # the structure of the data is hard coded into the params of this function
    def pad_or_truncate_video(self, video, target_length=150, num_landmarks=33, num_values=4):
      if len(video) > target_length:
        return video[:target_length]

      padded_video = video.copy()
      frames_to_add = target_length - len(video)

      for _ in range(frames_to_add):
        padded_frame = [np.zeros(num_values) for _ in range(num_landmarks)]  # Padding with 4 zeros for each landmark
        padded_video.append(padded_frame)

      return padded_video

    # function to normalize the landmarks about the hips
    def normalize_hip_center(self, video_landmarks):
      normalized_video = []

      for frame_landmarks in video_landmarks:
        left_hip = frame_landmarks[23]
        right_hip = frame_landmarks[24]

        # the array is sliced with :2 because we want to select only the x and y value
        # from left hip's four values
        hip_center = np.mean([left_hip[:2], right_hip[:2]], axis=0)

        # normalize all landmarks relative to hip center
        normalized_frame = []
        for landmark in frame_landmarks:

          # return landmark minus the hip center
          normalized_landmark = landmark[:2] - hip_center

          # add the values for z and visibility to normalized landmark
          normalized_landmark = np.concatenate((normalized_landmark, landmark[2:]))

          # append the normalized landmark to the list of landmarks for a given frame
          normalized_frame.append(normalized_landmark)

        normalized_video.append(normalized_frame)

      print("Returning normalized video landmarks")
      return normalized_video

    
    # Function to apply sliding window over given frames and given overlap for predictions
    def sliding_window_predictions(self, normalized_video_landmarks):
        predictions = []

        # pads video to 150 frames just so we can predict on it
        padded_video_landmarks = self.pad_or_truncate_video(normalized_video_landmarks)

        # Sliding window logic
        for start_idx in range(0, len(normalized_video_landmarks) - self.window_size + 1, self.stride):
            #window = video[start_idx : start_idx + window_size]

            X_test_input = np.array(padded_video_landmarks)
            X_test_input_reshaped = X_test_input.reshape(X_test_input.shape[0], -1)  # Flatten (frames, landmarks * features)
            X_test_input_reshaped = np.expand_dims(X_test_input_reshaped, axis=0)  # Add batch dimension

            # Make prediction
            shooting_prediction = self.final_shooting_model.predict(X_test_input_reshaped)
            print(f"Shooting model prediction: {shooting_prediction}")

            predicted_shooting_label = (shooting_prediction > 0.5).astype(int)
            if predicted_shooting_label == 1:
              action = "shooting"
            elif predicted_shooting_label == 0:
              print("NOT SHOOTING PREDICTED")
              movement_prediction = self.final_movement_model.predict(X_test_input_reshaped)

              predicted_movement_label = (movement_prediction > 0.5).astype(int)
              print(f"Movement model prediction: {movement_prediction}")

              if predicted_movement_label == 1:
                action = "dribbling"
              elif predicted_movement_label == 0:
                action = "idling"

            predictions.append(action)
        return predictions

    # Function to extract landmarks from a video
    def save_video_landmarks(self, video):
        cap = cv2.VideoCapture(video)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return []

        video_landmarks = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.pose_videos.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert to RGB

            if results.pose_landmarks:
                frame_landmarks = [[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]
                video_landmarks.append(frame_landmarks)

        cap.release()
        print("Returning list of video landmarks")

        return video_landmarks


    # Function to overlay predictions on video in real-time
    def output_video_with_prediction(self):
        cap = cv2.VideoCapture(0)
        print("in outputvideowithprediction")
        if not cap.isOpened():
            print("Error: Could not open video.")
            return []

        action = "None"  # Default action if no prediction is made
        frame_buffer = []  # Buffer to store recent frames' landmarks
        # actions = ['shooting', 'dribbling', 'idling']  # Define class labels
        frame_count = 0

        last_predicted_frame = 0

        while cap.isOpened():
            ret, frame = cap.read()
            frame_count += 1

            if not ret:
                break

            results = self.pose_videos.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert to RGB

            if results.pose_landmarks:

                #print("Extracting landmarks...")
                # Extract landmarks for the current frame
                frame_landmarks = [[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]

                # Add current frame landmarks to the buffer
                frame_buffer.append(frame_landmarks)

                # If buffer exceeds the required sequence length (90 frames), remove the oldest frame
                if len(frame_buffer) > self.window_size:
                    frame_buffer.pop(0)

                # If buffer has enough frames (sequence), make prediction
                if len(frame_buffer) >= self.window_size and (frame_count - last_predicted_frame) >= self.stride:
                    # normalize the landmarks in the buffer
                    normalized_video_landmarks = self.normalize_hip_center(frame_buffer)

                    # pass the normalized landmarks to make the predictions
                    predictions = self.sliding_window_predictions(normalized_video_landmarks)
                    last_predicted_frame = frame_count

                    if predictions:
                      self.action = predictions[-1]  # Most recent prediction
                      print(f"Action from latest window: {self.action}")

                      # method to get tag's current coordinates
                      position = self.data_reader.get_current_position()
                      self.position_action_queue.put((self.action, position))
                      print(f"Putting action {self.action} and position {position} into the queue")

            # Overlay the prediction on the frame
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, f"Action: {self.action}", (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Frame: {frame_count}", (50, 100), font, 1, (255, 255, 0), 2, cv2.LINE_AA)

            if results.pose_landmarks:
                # Optionally draw landmarks on the frame (for debugging or visualization)
                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # make frame smaller for visual purposes
            #frame = cv2.resize(frame, None, fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA)

            # Show the frame with the prediction overlay in real-time
            cv2.imshow("Video", frame)
            #print(f"Prediction for this window: {self.action}")

            # Check for key press to exit video playback early
            if cv2.waitKey(1) & 0xFF == ord('q') or self.app_instance.stop_requested:  # Press 'q' to quit
                break

        cap.release()
        cv2.destroyAllWindows()
