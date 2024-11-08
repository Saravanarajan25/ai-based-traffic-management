import cv2
import numpy as np
from time import sleep

# Parameters
largura_min = 80  # Minimum width of the rectangle
altura_min = 80  # Minimum height of the rectangle
offset = 6  # Error margin in pixels
pos_linha = 550  # Position of the counting line
delay = 60  # FPS of the video

detec = []
carros = 0
opposite_direction_count = 0

def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

# Video path
cap = cv2.VideoCapture('C:\\Users\\SARAVANARAJAN\\Downloads\\video (online-video-cutter.com).mp4')

subtracao = cv2.createBackgroundSubtractorKNN()

while True:
    ret, frame1 = cap.read()
    if not ret:
        break
    
    tempo = float(1 / delay)
    sleep(tempo)
    
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (5, 5), 0)  # Increased kernel size for better blur
    img_sub = subtracao.apply(blur)
    
    # Advanced morphological operations
    dilat = cv2.dilate(img_sub, np.ones((7, 7)))  # Larger kernel for dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))  # Larger kernel for morphology
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_OPEN, kernel)  # Added opening
    
    contorno, _ = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
    for (i, c) in enumerate(contorno):
        (x, y, w, h) = cv2.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue

        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centro = pega_centro(x, y, w, h)
        detec.append((centro, y))  # Append center and initial y-position for direction tracking
        cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

        for i, (centro, initial_y) in enumerate(detec):
            cx, cy = centro
            # Vehicle coming downwards (normal direction)
            if cy < (pos_linha + offset) and cy > (pos_linha - offset) and initial_y < pos_linha:
                carros += 1
                cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
                detec.pop(i)
                print("Vehicle detected in normal direction: " + str(carros))
            
            # Vehicle coming upwards (opposite direction)
            elif cy > (pos_linha - offset) and cy < (pos_linha + offset) and initial_y > pos_linha:
                opposite_direction_count += 1
                cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 0, 255), 3)
                detec.pop(i)
                print("Vehicle detected in opposite direction: " + str(opposite_direction_count))

    # Display the vehicle counts in the top-left corner
    cv2.putText(frame1, "VEHICLE COUNT (NORMAL) : " + str(carros), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.putText(frame1, "VEHICLE COUNT (OPPOSITE) : " + str(opposite_direction_count), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Video Original", frame1)
    cv2.imshow("Detectar", dilatada)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
cap.release()
