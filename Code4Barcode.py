import cv2
from pyzbar.pyzbar import decode
import pandas as pd
import os
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
items_path = os.path.join(base_dir, "itemData.xlsx")

# To load the data
items = pd.read_excel(items_path)

#settings
last_scanned = ""
last_time = 0
COOLDOWN = 2  # seconds

display_text = ""
display_time = 0

# To search the item in the 
def find_item(item_id):
    try:
        item_id = int(item_id)
    except:
        pass

    result = items[items['id'] == item_id]
    if not result.empty:
        return result.iloc[0]['name']  # ONLY name
    return None

# To activate the camera
cap = cv2.VideoCapture(0)

print("Item Name Scanner Running (press 'q' to quit)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for obj in decode(frame):

        # Ignore QR codes
        if obj.type == 'QRCODE':
            continue

        item_id = obj.data.decode('utf-8').strip()

        # For cooldown
        current_time = time.time()
        if item_id == last_scanned and (current_time - last_time) < COOLDOWN:
            continue

        last_scanned = item_id
        last_time = current_time

        try:
            item_name = find_item(item_id)

            if item_name:
                display_text = f"{item_name}"
            else:
                display_text = f"Unknown Item"

            display_time = cv2.getTickCount()

        except Exception as e:
            print("Error:", e)

        # The box to detect the item in the camera
        x, y, w, h = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # To display text about the item in the camera
    if display_text:
        elapsed = (cv2.getTickCount() - display_time) / cv2.getTickFrequency()
        if elapsed < 3:
            cv2.putText(frame, display_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

    cv2.imshow("Item Scanner", frame)

    key = cv2.waitKey(10) & 0xFF
    if key == ord('q') or key == 27:
        break

    if cv2.getWindowProperty("Item Name Scanner", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()