import cv2
import numpy as np

def detect_april_tag(image):
    
    # تبدیل تصویر به grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # تعریف دیکشنری AprilTag
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    
    # تشخیص برچسب‌ها
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray_image)
    
    # بررسی نتایج
    if ids is not None:
        for i in range(len(ids)):
            myTagId=ids[i][0]
            #2: right / 3: left / 1,4: straight / 5: stop
            if myTagId==1 or myTagId==4:
                myTagDirectionText= "Straight"
            elif myTagId==2: myTagDirectionText="Right"
            elif myTagId==3: myTagDirectionText="Left"
            elif myTagId==5: myTagDirectionText="STOP"

            # print(f"Tag ID: {myTagId}")
            cv2.putText(image, f'Tag ID: {myTagDirectionText}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # print(f"Corners: {corners[i]}")
            
            # نمایش گوشه‌های برچسب‌ها
            cv2.polylines(image, [np.int32(corners[i])], True, (0, 255, 0), 2)
    else: 
        #cv2.imshow("Image", image)
        return -100
    # نمایش تصویر نهایی
    #cv2.imshow("Image", image)
    return myTagId