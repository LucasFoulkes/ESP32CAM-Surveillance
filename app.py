import cv2
import os
from datetime import datetime, timedelta

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

        if not os.path.exists(current_date):
            os.makedirs(current_date)

        output_filepath = os.path.join(current_date, f'{current_datetime}_continuous.avi')
        out = create_video_writer(output_filepath, frame_width, frame_height, fourcc)

        print(f"Recording started at {current_datetime}")
        print(f"Output file: {output_filepath}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Frame read failed, attempting to reconnect...")
                    break

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
print("v1")
record_video_from_stream(stream_url)
