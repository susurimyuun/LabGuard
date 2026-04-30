import cv2
from ultralytics import YOLO

# file hasil training
model = YOLO('yolov8n.pt') 
model3 = YOLO('Glasses.pt')
model4 = YOLO('Mask.pt')

# Buka Webcam
cap = cv2.VideoCapture(0)

print("Kamera menyala. Tekan 'q' untuk keluar.")

while cap.isOpened():
    # Baca frame (gambar) dari kamera satu per satu
    success, frame = cap.read()
    
    if success:
        results = model(frame, conf=0.5, imgsz = 640)
        results3 = model3(frame, conf=0.5, imgsz = 640)
        results4 = model4(frame, conf=0.1, imgsz = 640)

        # bounding box
        annotated_frame = results[0].plot()
        annotated_frame = results3[0].plot(img=annotated_frame)
        annotated_frame = results4[0].plot(img=annotated_frame)


        # tampilakn hasil
        cv2.imshow("Connected Worker - Safety Monitor", annotated_frame)

        # q untuk keluar dari web/program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Bersihkan dan tutup kamera jika program selesai
cap.release()
cv2.destroyAllWindows()