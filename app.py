from . import cv2
import os
import uuid
from datetime import datetime
import time

# Video recording settings
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
segment_duration = 60  # Record video in 60-second segments
recordings_dir = 'recordings'

# Initialize the video capture object
camera = cv2.VideoCapture("http://127.0.0.1:5000/video_feed")

def is_stream_connected():
    return camera.isOpened()

def wait_for_stream(max_retries=5, retry_delay=5):
    retries = 0
    while not is_stream_connected() and retries < max_retries:
        print(f"Connection failed. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        retries += 1
    return is_stream_connected()

def get_day_folder():
    current_date = datetime.now().strftime("%Y-%m-%d")
    day_folder = os.path.join(recordings_dir, current_date)
    os.makedirs(day_folder, exist_ok=True)
    return day_folder

def concatenate_segments(segment_file, day_folder):
    output_file = os.path.join(day_folder, 'continuous_recording.mp4')
    # Create a temporary file for the concatenated output
    temp_output_file = os.path.join(day_folder, f'temp_output_{uuid.uuid4()}.mp4')
    # Concatenate the segment with the existing output file (if it exists)
    if os.path.exists(output_file):
        cmd = f'ffmpeg -y -loglevel error -i "{output_file}" -i "{segment_file}" -filter_complex "[0:v][1:v]concat=n=2:v=1[out]" -map "[out]" "{temp_output_file}"'
    else:
        cmd = f'ffmpeg -y -loglevel error -i "{segment_file}" -c copy "{temp_output_file}"'
    os.system(cmd)
    # Replace the output file with the temporary output file
    os.replace(temp_output_file, output_file)
    # Remove the segment file
    os.remove(segment_file)

video_writer = None
start_time = cv2.getTickCount()

# Main recording loop
while True:
    if not wait_for_stream():
        print("Failed to establish a connection to the video stream.")
        break

    success, frame = camera.read()
    if not success:
        print("Failed to read frame from camera.")
        break

    if video_writer is None:
        # Get the frame size
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        print(f"Frame size: {frame_width}x{frame_height}")

        # Create a new video writer for the current segment
        day_folder = get_day_folder()
        temp_segment_path = os.path.join(day_folder, f'temp_segment_{uuid.uuid4()}.mp4')
        video_writer = cv2.VideoWriter(temp_segment_path, fourcc, 30, (frame_width, frame_height))

    # Write the frame to the video writer
    video_writer.write(frame)

    if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() >= segment_duration:
        # Close the current video writer and concatenate the new segment
        video_writer.release()
        video_writer = None
        concatenate_segments(temp_segment_path, day_folder)
        start_time = cv2.getTickCount()

# Close the camera and perform final concatenation if needed
camera.release()
if video_writer is not None:
    video_writer.release()
    day_folder = get_day_folder()
    concatenate_segments(temp_segment_path, day_folder)