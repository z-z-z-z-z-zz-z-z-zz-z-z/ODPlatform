import cv2
from ultralytics import YOLO

model = YOLO('./train3-20250704-165500-yolo11n-best.pt')

cap = cv2.VideoCapture(0)