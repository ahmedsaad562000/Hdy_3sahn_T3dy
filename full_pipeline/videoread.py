from libs import cv2 , os

def extract_frames(video_path, output_folder, fps=30):
    """
    Extract frames from a video at a given frame rate.

    Parameters:
    - video_path (str): Path to the input video.
    - output_folder (str): Path to the folder where frames will be saved.
    - fps (int): Frames per second to extract.

    Returns:
    - None
    """

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    print("A7a")
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return

    frame_count = 0
    frames = []
    while True:
        ret, frame = cap.read()

        print(ret)

        # Break the loop if no more frames available
        if not ret:
            break

        # Check if the current frame count is divisible by the desired FPS
        if frame_count % fps == 0:
            frame_path = f"{output_folder}/frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, frame)
            print(f"Frame {frame_count} saved to {frame_path}")
            frames.append(frame)

        frame_count += 1

    cap.release()
    
    return frames


def clear_folder(folder_path):
    """
    Clear all files from a folder.

    Parameters:
    - folder_path (str): Path to the folder.

    Returns:
    - None
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")    
