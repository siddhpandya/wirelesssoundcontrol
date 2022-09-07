import cv2
import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
hand_module=mp.solutions.hands
mpHands=mp.solutions.hands.Hands()
mpDraw=mp.solutions.drawing_utils
cap= cv2.VideoCapture(0)
while True:
    _,img=cap.read()
    img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    hands=mpHands.process(img_rgb)
    if hands.multi_hand_landmarks:
        two_hands=[]
        for hand in hands.multi_hand_landmarks:
            hand_landmarks=[]
            for id,location in enumerate(hand.landmark):
                h,w,c=img.shape
                cx,cy=int(location.x*w),int(location.y*h)
                hand_landmarks.append([id,cx,cy])
                #print(cx,cy)
            two_hands.append(hand_landmarks)
            mpDraw.draw_landmarks(img,hand,hand_module.HAND_CONNECTIONS)
            if hand_landmarks and len(two_hands)==2:
                x1,y1=two_hands[0][8][1],two_hands[0][8][2]
                x2,y2=two_hands[1][8][1],two_hands[1][8][2]
                cv2.circle(img,(x1,y1),10,(0,255,0),cv2.FILLED)
                cv2.circle(img,(x2,y2),10,(0,255,0),cv2.FILLED)
                cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)
                length=((x2-x1)**2+(y2-y1)**2)**0.5
                #print(length)
                if length<40:
                    cv2.circle(img,((x1+x2)//2,(y1+y2)//2),10,(0,255,0),cv2.FILLED)
                #print(volume.GetMasterVolumeLevel())
                #print(volume.GetVolumeRange())
                minVol,maxVol,_=volume.GetVolumeRange()
                final_vol=np.interp(length,[40,350],[-35,maxVol])
                print(final_vol)
                volume.SetMasterVolumeLevel(final_vol,None)
                vol_bar=np.interp(length,[40,350],[400,50])
                vol_perc=np.interp(length,[40,350],[0,100])
                cv2.rectangle(img,(40,50),(80,400),(255,255,0),3)
                cv2.rectangle(img,(40,int(vol_bar)),(80,400),(255,255,0),cv2.FILLED)
                cv2.putText(img,f'{int(vol_perc)}%',(40,30),cv2.CAP_PROP_FPS,1,(0,255,255),2)

    cv2.imshow("img",img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break