import cv2
from pyzbar.pyzbar import decode
import pandas as pd
from datetime import datetime
import os
import time

#  To choose whether to check in or no
mode = input("Select mode (1 = Check-in, 2 = Check-out): ").strip()

if mode == "1":
    MODE = "IN"
elif mode == "2":
    MODE = "OUT"
else:
    print("Invalid input. Defaulting to Check-in.")
    MODE = "IN"

base_dir = os.path.dirname(os.path.abspath(__file__))
employees_path = os.path.join(base_dir, "employees.xlsx")
attendance_path = os.path.join(base_dir, "attendance.xlsx")

employees = pd.read_excel(employees_path)

if os.path.exists(attendance_path):
    attendance = pd.read_excel(attendance_path, dtype=str)
else:
    attendance = pd.DataFrame({
        "id": [],
        "name": [],
        "date": [],
        "entry_time": [],
        "exit_time": []
    }).astype(str)

# Settings
last_scanned_time = {}
COOLDOWN = 3

display_text = ""
display_time = 0

# To search the employees
def find_employee(emp_id):
    try:
        emp_id = int(emp_id)
    except:
        pass

    result = employees[employees['id'] == emp_id]
    if not result.empty:
        return result.iloc[0]
    return None

# To activate the camera
cap = cv2.VideoCapture(0)

print(f"QR Attendance System Running [{MODE}] (press 'q' to quit)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for obj in decode(frame):

        # ONLY QR
        if obj.type != 'QRCODE':
            continue

        emp_id = obj.data.decode('utf-8').strip()

        # Cooldown
        current_time = time.time()
        if emp_id in last_scanned_time:
            if current_time - last_scanned_time[emp_id] < COOLDOWN:
                continue
        last_scanned_time[emp_id] = current_time

        try:
            emp = find_employee(emp_id)

            if emp is not None:
                name = str(emp['name'])
                task = str(emp['task'])

                today = datetime.now().strftime("%Y-%m-%d")
                now_time = datetime.now().strftime("%H:%M:%S")

                today_record = attendance[
                    (attendance['id'] == str(emp['id'])) &
                    (attendance['date'] == today)
                ]

                # To pick wwhether to check in or check out frrom the lab
                if MODE == "IN":

                    if today_record.empty:
                        attendance.loc[len(attendance)] = {
                            "id": str(emp['id']),
                            "name": name,
                            "date": today,
                            "entry_time": now_time,
                            "exit_time": ""
                        }
                        display_text = f"ID:{emp_id} | {name} | {task} | Check-in"

                    else:
                        display_text = f"ID:{emp_id} | {name} | Already checked in"

                elif MODE == "OUT":

                    if today_record.empty:
                        display_text = f"ID:{emp_id} | {name} | No check-in found"

                    else:
                        idx = today_record.index[0]
                        attendance.loc[idx, "exit_time"] = now_time
                        display_text = f"ID:{emp_id} | {name} | Check-out"

                # Saves the data
                attendance = attendance.astype(str)
                attendance.to_excel(attendance_path, index=False)

            else:
                display_text = f"Unknown ID: {emp_id}"

            display_time = cv2.getTickCount()

        except Exception as e:
            print("Error:", e)

        # draw box
        x, y, w, h = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Displpay text
    if display_text:
        elapsed = (cv2.getTickCount() - display_time) / cv2.getTickFrequency()
        if elapsed < 3:
            cv2.putText(frame, display_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2)

    cv2.imshow("QR Attendance Scanner", frame)

    key = cv2.waitKey(10) & 0xFF
    if key == ord('q') or key == 27:
        break

    if cv2.getWindowProperty("QR Attendance Scanner", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()