import cv2
import numpy as np
import time

from comtypes import CLSCTX_ALL

import handTrackingModule as htm
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

###########################
wCam, hCam = 640, 480
###########################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(maxHands=1,
                            detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volMin = volume.GetVolumeRange()[0]
volMax = volume.GetVolumeRange()[1]
#volume.SetMasterVolumeLevel(-60.0, None)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) != 0:
        # 4,8 index and thumb
        #print(lmList[4], lmList[8])

        x1,y1 = lmList[4][1], lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2

        cv2.circle(img, (x1,y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
        cv2.circle(img, (cx,cy), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        #Hand Range 20-220 aprox
        #Volume Range -65 - 0

        vol = np.interp(length,[5, 120],[volMin,volMax])
        volBar = np.interp(length, [5, 120], [400,150])
        volPer = np.interp(length, [5, 120], [0, 100])

        print(length, vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (50, 150), (85, 400 ), (255, 0 ,0 ), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), 3)
        cv2.putText(img, f'{int(volPer)} %', (40,450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0,0),3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)
