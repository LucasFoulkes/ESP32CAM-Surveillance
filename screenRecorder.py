import os
import datetime
import time
from PIL import ImageGrab, Image

# Create the recordings folder if it doesn't exist
if not os.path.exists("recordings"):
    os.makedirs("recordings")

# Set the JPEG quality
jpeg_quality = 20  # Reduce this value to lower quality and size
scale_factor = 0.5  # Reduce the image size to 50% of its original dimensions

while True:
    # Get the current date and time
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the date folder if it doesn't exist
    date_folder = os.path.join("recordings", date_str)
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    # Capture the screenshot
    screenshot = ImageGrab.grab()

    # Convert the screenshot to grayscale
    grayscale_screenshot = screenshot.convert('L')

    # Resize the image using the scale factor
    if scale_factor != 1:
        new_size = (int(grayscale_screenshot.width * scale_factor), int(grayscale_screenshot.height * scale_factor))
        grayscale_screenshot = grayscale_screenshot.resize(new_size, Image.LANCZOS)  # Changed from ANTIALIAS to LANCZOS

    # Save the screenshot with the current date and time as the file name
    file_name = f"{time_str}.jpg"
    file_path = os.path.join(date_folder, file_name)
    # Save as JPEG and set the quality
    grayscale_screenshot.save(file_path, 'JPEG', quality=jpeg_quality)

    # Wait for 1 second before capturing the next screenshot
    time.sleep(10)
