import cv2
import os
from datetime import datetime

cap = cv2.VideoCapture('https://foxeyes.loca.lt/stream')

def capture_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from the stream.")
            break
        
        current_datetime = datetime.now()
        captures_folder = 'captures'
        os.makedirs(captures_folder, exist_ok=True)
        filename = f"{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        
        # Write current datetime on the frame
        cv2.putText(frame, current_datetime.strftime('%Y-%m-%d %H:%M:%S'), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imwrite(os.path.join(captures_folder, filename), frame)
        print(f'Saved frame as: {filename}')

if __name__ == '__main__':
    capture_frames()