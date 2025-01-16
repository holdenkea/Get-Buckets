import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt

# function to detect poses
'''
Args:
    image: input image with a person whose pose landmarks need to be detected
    pose: the pose setup function required to perform the pose detection
    imageInput: a boolean value that is if set to true the function displays the original input image, the resultant image,
             and the pose landmarks in 3D plot and returns nothing.

Returns:
    output_image: The input image with the detected pose landmarks drawn.
    landmarks: A list of detected landmarks converted to their original scale

'''
def detectPose(media_selection, testFile, pose):

    # if the input is an image
    if media_selection == 1 and testFile != None:

        # read image from the specified path
        output_image = cv2.imread(testFile)

        # create a copy of the original image for display
        original_image = output_image.copy()

        # convert the image from BGR into RGB
        imageRGB = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

        # perform pose detection
        results = pose.process(imageRGB)

        # initialize list to store landmarks
        landmarks = []

        # check if landmarks are detected
        if results.pose_landmarks:

            # draw pose landmarks on output_image
            mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                    connections=mp_pose.POSE_CONNECTIONS)

            normalizeLandmarks(results.pose_landmarks.landmark)
        
        # set to true "1" when you want to display the images
        display_images = 1

        # check if the original input image and the resultant image are specified to be displayed
        if display_images: # set to true if using this method with images

            # display the original input image and the resultant image
            plt.figure(figsize=[22,22])
            plt.subplot(121);plt.imshow(original_image[:,:,::-1]);plt.title("Original Image");plt.axis('off')
            plt.subplot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off')

            # also plot the pose landmarks in 3D
            mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
        
        else:  
            # return the output image and the found landmarks
            return output_image, landmarks

    # if requested input is a video or a webcam
    if (media_selection == 2 and testFile != None) or (media_selection == 3 and testFile == None):       
        
        # requested media selection is an input video
        if media_selection == 2:

            #initialize videoCapture to read from video stored on computer
            cap = cv2.VideoCapture(testFile)

        # requested media selection is the webcam
        elif media_selection == 3:

            # initialize videoCapture to read from webcam
            cap = cv2.VideoCapture(0)

        # create named window for resizing purposes
        cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
        
        # set the video camera size
        cap.set(3,1280)
        cap.set(4,960)

        if not cap.isOpened():
            ValueError("Capture could not be opened")

        while cap.isOpened():
            # read a frame
            ret, frame = cap.read()

            # check if frame is read properly or not
            if not ret:
                break

            imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # recoloring frame to RGB to pass to mediapipe
            imageRGB.flags.writeable = False   # flags set to false for better performace

            # detection made here
            results = pose.process(imageRGB)

            imageRGB.flags.writeable = True    # setting flags back to true after detection
            imageBGR = cv2.cvtColor(imageRGB, cv2.COLOR_RGB2BGR)  # recoloring image back to BGR for cv2
  
            landmarks = results.pose_landmarks

            if landmarks:
                normalizedLandmarks = normalizeLandmarks(landmarks.landmark)

                # pose = classifyPose(normalizedLandmarks, poses)

                mp_drawing.draw_landmarks(imageBGR, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            combined_frame = np.hstack((frame, imageBGR))

            cv2.imshow('Pose Detection', combined_frame)

            # quit camera feed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Video stream closed")

    else:
        raise ValueError(f"No logic path for media selection {media_selection} and test file {testFile}")

# function to normalize landmarks so subject's position and size doesn't affect pose recognition
# use the hip centered normalization to handle variations in subject size and distance
def normalizeLandmarks(landmarks):
    
    # extract landmarks to a numpy array
    landmarksArray = np.array([[landmark.x, landmark.y, landmark.z] for landmark in landmarks])

    # calculate center of hips (midpoint of left and right hip)
    hipCenter = (landmarksArray[mp_pose.PoseLandmark.LEFT_HIP.value] +
                 landmarksArray[mp_pose.PoseLandmark.RIGHT_HIP.value]) / 2
    
    # makes it so hip center is essentially [0,0,0]
    normalizedLandmarks = landmarksArray - hipCenter

    # calculate euclidean distance between hips to use as a scale factor so that poses closer or father are comparable
    leftHip = landmarksArray[mp_pose.PoseLandmark.LEFT_HIP.value]
    rightHip = landmarksArray[mp_pose.PoseLandmark.RIGHT_HIP.value]
    hipDistance = np.linalg.norm(leftHip - rightHip)

    # logic to avoid division by zero
    if hipDistance == 0:
        raise ValueError("Hip distance is zero. Normalization failed.")

    # scale normalization, making pose independent of subject's size or distance from camera
    normalizedLandmarks /= hipDistance
    

    return normalizedLandmarks

# function to retrieve test files
def getTestFile(mediaSelection, fileNum):
    images = [
        "media/images/Malik-Monk-Image1.jpg",
        "media/images/De'Aaron-Fox-Image2.jpg"
    ]

    videos = [
        "media/videos/Slow-Dribbling-Video1.mp4"
    ]

    if mediaSelection == 1:
        return images[int(fileNum) - 1]

    if mediaSelection == 2:
        return videos[int(fileNum) - 1]

# initializing mediapipe drawing and pose class
mp_drawing = mp.solutions.drawing_utils     # drawing utilities
mp_pose = mp.solutions.pose                 # importing pose estimation model

# pose function
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)

media_selection = 0
fileNum = 0
testFile = None

media_selection = input(f"\nSelect a media type to detect poses\n"
      "1 - Pictures\n" 
      "2 - Videos\n" 
      "3 - Real time using Webcam\n" 
      "Selection: ")

# converting the input string to an integer for comparison
media_selection = int(media_selection)

if media_selection < 1 or media_selection > 3:
    raise ValueError("Invalid selection value")

if media_selection == 1:
    print("\nImages Selected\n")

    fileNum = input(f"\nSelect the image you would like to test\n"
    "1\n"
    "2\n"
    "Selection: ")

    testFile = getTestFile(media_selection, fileNum)
    detectPose(media_selection, testFile, pose)

if media_selection == 2:
    print("\nVideos Selected\n")
    
    fileNum = input(f"\nSelect the video you would like to test\n"
    "1\n"
    "Selection: ")

    testFile = getTestFile(media_selection, fileNum)
    detectPose(media_selection, testFile, pose)

if media_selection == 3:
    print("\nWebcam Selected\n")
    detectPose(media_selection, testFile, pose)

"""
OLD LOGIC FOR VIDEO 

# setting up Pose function
# mp_pose.Pose(False means detector is invoked as needed, min detection, min tracking, complexity of pose landmark model, default 1)
with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:   # detection and tracking confidence can be changed
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

            normalizedLandmarks = normalizeLandmarks(landmarks)

            pose = classifyPose(normalizedLandmarks, poses)
            
            # x and y coordinates for left shoulder, elbow, and wrist
            # L_shoulder = [normalizedLandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
            #              normalizedLandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        
            #L_elbow = [normalizedLandmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
            #           normalizedLandmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            # L_wrist = [normalizedLandmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
            #           normalizedLandmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # calculate angle
            #angle = calculateAngle(L_shoulder, L_elbow, L_wrist)
            
            # Using putText to pass the image from webcam, calculated angle, and location of elbow coodinates
            cv2.putText(image, str(angle),
                            tuple(np.multiply(L_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA
                        )

            # Pass Counter logic
            # if angle >

        except:
            pass

        # render detections on the screen
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
        # the above allows you to plot the Pose landmarks in 3D semi-accurately

        cv2.imshow('MediaPipe Feed', image)

        # quit camera feed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



"""

