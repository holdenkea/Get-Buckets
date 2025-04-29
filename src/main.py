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
            print("Initializing video capture")

            #initialize videoCapture to read from video stored on computer
            cap = cv2.VideoCapture(testFile)

        # requested media selection is the webcam
        elif media_selection == 3:

            # initialize videoCapture to read from webcam
            cap = cv2.VideoCapture(0)
            # set the video camera size
            cap.set(3,1280)
            cap.set(4,960)

        # create named window for resizing purposes
        cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
        
        if not cap.isOpened():
            ValueError("Capture could not be opened")

        while cap.isOpened():

            # read a frame
            ret, frame = cap.read()

            # check if frame is read properly or not
            if not ret:
                break

            #frame = cv2.resize(frame, (854, 480))


            imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # recoloring frame to RGB to pass to mediapipe
            imageRGB.flags.writeable = False   # flags set to false for better performace

            # detection made here
            results = pose.process(imageRGB)

            imageRGB.flags.writeable = True    # setting flags back to true after detection
            imageBGR = cv2.cvtColor(imageRGB, cv2.COLOR_RGB2BGR)  # recoloring image back to BGR for cv2
  
            landmarks = results.pose_landmarks

            if landmarks:
                # normalizedLandmarks = normalizeLandmarks(landmarks.landmark)

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
def getTestFile(media_selection, pose_class, file_num):
    media = [
        "raw_images",
        "mp4_videos"
    ]

    media_path = media[media_selection - 1]

    pose_classes = [
        "call",
        "dribbling",
        "moving",
        "shooting"
    ]

    pose_path = pose_classes[int(pose_class) - 1]

    return f"./media/{media_path}/{pose_path}/{pose_path}_{int(file_num):04d}.MP4"

# initializing mediapipe drawing and pose class
mp_drawing = mp.solutions.drawing_utils     # drawing utilities
mp_pose = mp.solutions.pose                 # importing pose estimation model

# pose function
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)

media_selection = 0
fileNum = 0
testFile = None

media_selection = input(f"\nSelect a media folder to detect poses\n"
      "1 - Raw Images\n" 
      "2 - MP4 Videos\n" 
      "3 - Real time using Webcam\n" 
      "Selection: ")

# converting the input string to an integer for comparison
media_selection = int(media_selection)

if media_selection < 1 or media_selection > 3:
    raise ValueError("Invalid selection value")

if media_selection == 1:
    """
    
    print("\nImages Selected\n")

    fileNum = input(f"\nSelect the image you would like to test\n"
    "1\n"
    "2\n"
    "Selection: ")

    testFile = getTestFile(media_selection, fileNum)
    detectPose(media_selection, testFile, pose)
    """
if media_selection == 2:
    print("\nVideos Selected\n")
    
    pose_class = input(f"\nSelect the number corresponding to the class you would like\n"
    "1 - Call for pass\n"
    "2 - Dribbling\n"
    "3 - Moving without the ball\n"
    "4 - Shooting\n"
    "Selection: ")

    file_num = input(f"Select the file number you want to test")

    test_file = getTestFile(media_selection, pose_class, file_num)

    print(f"File path: {test_file}")

    detectPose(media_selection, test_file, pose)

if media_selection == 3:
    print("\nWebcam Selected\n")
    detectPose(media_selection, testFile, pose)