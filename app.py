import os
import subprocess
import threading
import time
from datetime import datetime
from queue import Queue

import cv2
import requests
from flask import Flask, Response, render_template, send_file
from waitress import serve

app = Flask(__name__)
lock = threading.Lock()
frame_queue = Queue()

def send_request_to_camera():
    url = 'httpcamera.local/control?var=framesize&val=9'
    try:
        response = requests.get(url, timeout=10)
        app.logger.info('Request sent successfully to the camera.' if response.status_code == 200 else f'Failed to send request to the camera. Status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        app.logger.error(f'Error occurred while sending request to the camera: {e}')

def capture_frames():
    cap = cv2.VideoCapture('http://camera.local:81/stream')
    # cap = cv2.VideoCapture('http://127.0.0.1:5000/video_feed')
    while True:
        ret, frame = cap.read()
        if not ret:
            app.logger.error("Error reading frame from the stream.")
            break
        frame_queue.put(frame)

def record_video():
    start_time = time.time()
    video_count = 1
    out = None
    tmp_filename = None

    while True:
        frame = frame_queue.get()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if out is None:
            current_datetime = datetime.now()
            log_folder = os.path.join(app.static_folder, 'logs', current_datetime.strftime('%Y-%m-%d'))
            os.makedirs(log_folder, exist_ok=True)
            tmp_filename = f"{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}_{video_count}_tmp.mp4"
            final_filename = f"{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}_{video_count}.mp4"
            out = cv2.VideoWriter(os.path.join(log_folder, tmp_filename), cv2.VideoWriter_fourcc(*'mp4v'), 30, (frame.shape[1], frame.shape[0]))
            app.logger.info(f'Created new VideoWriter object for file: {tmp_filename}')

        out.write(frame)

        if time.time() - start_time >= 60:
            out.release()
            app.logger.info(f'Released VideoWriter object for file: {tmp_filename}')
            os.rename(os.path.join(log_folder, tmp_filename), os.path.join(log_folder, final_filename))
            app.logger.info(f'Renamed temporary file to: {final_filename}')
            video_count += 1
            start_time = time.time()
            out = None
            tmp_filename = None

        frame_queue.task_done()

def generate_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            frame_queue.task_done()

def get_logs_folder():
    logs_folder = os.path.join(app.static_folder, 'logs')
    if not os.path.exists(logs_folder):
        app.logger.warning("No logs folder found.")
    return logs_folder

def concatenate_files(logs_folder):
    for file in os.listdir(logs_folder):
        if file.startswith('output_'):
            os.remove(os.path.join(logs_folder, file))

    files = sorted([f for f in os.listdir(logs_folder) if not f.startswith('output_')])[:-1]

    if not files:
        return None

    last_file_name_parts = files[-1].split('_')
    last_file_datetime_str = '_'.join(last_file_name_parts[:-1])
    last_file_datetime = datetime.strptime(last_file_datetime_str, '%Y-%m-%d_%H-%M-%S')
    output_file_name = f'output_{last_file_datetime.strftime("%Y%m%d%H%M%S")}.mp4'
    list_file_path = os.path.join(logs_folder, 'concat_list.txt')

    with open(list_file_path, 'w') as list_file:
        list_file.write('\n'.join([f"file '{file}'" for file in files]))

    output_path = os.path.join(logs_folder, output_file_name)
    command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file_path, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-y', output_path]
    subprocess.run(command, check=True)
    os.remove(list_file_path)

    # Delete the individual video files after successful merge
    for file in files:
        os.remove(os.path.join(logs_folder, file))

    return output_file_name

def cleanup_tmp_files():
    logs_folder = os.path.join(app.static_folder, 'logs')
    if not os.path.exists(logs_folder):
        return

    for root, dirs, files in os.walk(logs_folder):
        for file in files:
            if file.endswith('_tmp.mp4'):
                tmp_file_path = os.path.join(root, file)
                try:
                    os.remove(tmp_file_path)
                    app.logger.info(f'Deleted temporary file: {tmp_file_path}')
                except Exception as e:
                    app.logger.warning(f'Failed to delete temporary file: {tmp_file_path}. Error: {str(e)}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def folders():
    logs_folder = get_logs_folder()
    folders = os.listdir(logs_folder) if os.path.exists(logs_folder) else []
    return render_template('logs.html', folders=folders) if folders else ("No logs folder found", 404)

@app.route('/play/<folder>')
def play(folder):
    logs_folder = os.path.join(get_logs_folder(), folder)
    if not os.path.exists(logs_folder):
        app.logger.warning(f"No folder named {folder} found.")
        return (f"No folder named {folder} found.", 404)

    try:
        output_file_name = concatenate_files(logs_folder)
        if output_file_name:
            output_file_path = os.path.join(logs_folder, output_file_name)
            return render_template('play.html', video_path=output_file_path)
        else:
            return ("No files to concatenate.", 404)
    except Exception as e:
        app.logger.error(f"Error occurred during concatenation: {str(e)}")
        return ("An error occurred during concatenation.", 500)

@app.route('/video/<path:video_path>')
def serve_video(video_path):
    return send_file(video_path, mimetype='video/mp4')

if __name__ == '__main__':
    os.makedirs(os.path.join(app.static_folder, 'logs'), exist_ok=True)
    send_request_to_camera()
    cleanup_tmp_files()  # Call the cleanup function at the start of the script
    capture_thread = threading.Thread(target=capture_frames)
    record_thread = threading.Thread(target=record_video)
    capture_thread.start()
    record_thread.start()
    serve(app, host='0.0.0.0', port=3000)