import cv2
import time

def capture_frames_from_camera(camera_id=0, output_path='../dataset/camera_frames', fps=2, max_frames=10):
    '''
    If you have only one camera connected, the default camera_id is usually 0. 
    This means the code will try to access the first camera available.

    If you have multiple cameras connected, you can determine the appropriate camera_id by trial and error or by 
    checking the documentation or specifications of the device.
    
    camera_id = 0: This would typically access the first available camera.
    camera_id = 1: This would attempt to access the second camera, if available.
    
    '''
    # Create the video capture object
    cap = cv2.VideoCapture(camera_id)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Calculate the delay based on desired fps
    delay = int(1000 / fps)

    frame_count = 0
    while frame_count < max_frames:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the frame
        cv2.imshow('Frame', frame)

        # Save frame to the specified output path
        filename = f"{output_path}frame_{frame_count}.jpg"
        cv2.imwrite(filename, frame)

        frame_count += 1

        # Break the loop if 'q' is pressed
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    # Release the capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
