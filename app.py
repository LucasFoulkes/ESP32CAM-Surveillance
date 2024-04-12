import cv2
import os
from datetime import datetime

def create_video_writer(filepath, frame_width, frame_height, codec='XVID', fps=20.0):
    fourcc = cv2.VideoWriter_fourcc(*codec)
    return cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))

def put_text_with_background(frame, text, position, font, font_scale, font_color, background_color, line_type):
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, line_type)
    x, y = position
    cv2.rectangle(frame, (x, y - text_height - baseline), (x + text_width, y + baseline), background_color, thickness=cv2.FILLED)
    cv2.putText(frame, text, position, font, font_scale, font_color, line_type)

def record_video_from_stream(stream_url, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            print(f"Error opening video stream at {stream_url}")
            attempts += 1
            continue

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        start_time = datetime.now()
        date_dir = start_time.strftime('%Y-%m-%d')
        filename = start_time.strftime('%Y-%m-%d_%H-%M-%S_continuous.avi')
        os.makedirs(date_dir, exist_ok=True)
        output_filepath = os.path.join(date_dir, filename)

        out = create_video_writer(output_filepath, frame_width, frame_height)

        print(f"Recording started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output file: {output_filepath}")

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_color = (0, 0, 255)  # Red color
        background_color = (0, 0, 0)  # Black background
        line_type = 2
        top_left_corner_of_text = (10, 30)  # Adjusted position to top left corner

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Frame read failed, attempting to reconnect...")
                    break

                current_time = datetime.now()
                datetime_text = current_time.strftime('%Y-%m-%d %H:%M:%S')
                put_text_with_background(frame, datetime_text, top_left_corner_of_text, font, font_scale, font_color, background_color, line_type)
                out.write(frame)
                print(f"Recording duration: {current_time - start_time}", end='\r')

        except KeyboardInterrupt:
            print("\nRecording stopped by user.")

        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            print(f"\nRecording finished. Total duration: {current_time - start_time}")
            print(f"Output file: {output_filepath}")

        attempts += 1

stream_url = 'http://camera.local:81/stream'
record_video_from_stream(stream_url)