import cv2
import os
from datetime import datetime

def create_video_writer(filepath, frame_width, frame_height, fourcc):
    return cv2.VideoWriter(filepath, fourcc, 20.0, (frame_width, frame_height))

def record_video_from_stream(stream_url, max_attempts=5):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    attempts = 0

    while attempts < max_attempts:
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            print(f"Error opening video stream at {stream_url}")
            attempts += 1
            continue

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        start_time = datetime.now()
        current_date = start_time.strftime('%Y-%m-%d')
        current_datetime = start_time.strftime('%Y-%m-%d_%H-%M-%S')

        recordings_path = 'recordings'
        date_folder_path = os.path.join(recordings_path, current_date)
        if not os.path.exists(date_folder_path):
            os.makedirs(date_folder_path)

        output_filepath = os.path.join(date_folder_path, f'{current_datetime}_continuous.avi')
        out = create_video_writer(output_filepath, frame_width, frame_height, fourcc)

        print(f"Recording started at {current_datetime}")
        print(f"Output file: {output_filepath}")

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 0, 255)  # Red color
        background_color = (0, 0, 0)  # Black background
        thickness = 2
        line_type = cv2.LINE_AA

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Frame read failed, attempting to reconnect...")
                    break

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
                cv2.rectangle(frame, (0, 0), (text_width + 10, text_height + 10), background_color, -1)
                cv2.putText(frame, timestamp, (5, text_height + 5), font, font_scale, font_color, thickness, line_type)

                out.write(frame)
                current_time = datetime.now()
                elapsed_time = current_time - start_time
                print(f"Recording duration: {elapsed_time}", end='\r')

        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
            break

        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            print(f"\nRecording finished. Total duration: {elapsed_time}")
            print(f"Output file: {output_filepath}")

        attempts += 1

stream_url = 'http://camera.local:81/stream'
print("v3")
record_video_from_stream(stream_url)
