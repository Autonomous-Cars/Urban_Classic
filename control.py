import cv2
import numpy as np
import time
import linesdetect

red_point = False
end_crossroad = False 
yellow = False
yellow_on = False

def detect_lines(image):
        
    rho = 1  
    angle = np.pi / 180  
    min_threshold = 10  
    lines = cv2.HoughLinesP(image, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)
                
    return lines


def find_lines(frame, lines):
    a = np.zeros_like(frame)
    try:
        left_line_x = []
        left_line_y = []
        right_line_x = []
        right_line_y = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (y2 - y1) / (x2 - x1) 
                if abs(slope) < 0.5: 
                    continue
                if slope <= 0:
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                else: 
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])
        min_y = int(frame.shape[0] * (3 / 5)) 
        max_y = int(frame.shape[0]) 
        poly_left = np.poly1d(np.polyfit(left_line_y, left_line_x, deg=1))
        left_x_start = int(poly_left(max_y))
        left_x_end = int(poly_left(min_y))
        poly_right = np.poly1d(np.polyfit( right_line_y, right_line_x, deg=1))
        right_x_start = int(poly_right(max_y))
        right_x_end = int(poly_right(min_y))
        cv2.line(a, (left_x_start, max_y), (left_x_end, min_y), [255,0,0], 5)
        cv2.line(a, (right_x_start, max_y), (right_x_end, min_y), [255,0,0], 5)
        present_pix = (left_x_end+right_x_end)/2
    except:
        present_pix = 128
    return a, present_pix




def region_of_interest(image):
    (height, width) = image.shape
    mask = np.zeros_like(image)
    polygon = np.array([[
        (0, height),
        (0, 180),
        (80, 130),
        (256-80,130),
        (width, 180),   
        (width, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    masked_image = image * (mask)
 
    return masked_image




def horiz_lines(mask):
    roi = mask[160:180, 96:160]
    try:
        lines = detect_lines(roi)
        lines = lines.reshape(-1,2,2)
        slope = (lines[:,1,1]-lines[:,0,1]) / (lines[:,1,0]-lines[:,0,0])
        
        if (lines[np.where(abs(slope)<0.2)]).shape[0] != 0:
            detected = True
        else:
            detected = False
    except:
        detected = False
    return detected



def detect_side(side_mask):
    side_pix = np.mean(np.where(side_mask[150:190, :]>0), axis=1)[1]
    return side_pix




def reduce_speed(car,breaking):
    car.setSteering(0)
    while car.getSpeed():
        car.setSpeed(breaking)
        car.getData()
    car.setSpeed(0)
    return True





    

def stop_car(car):
    car.setSteering(0)
    while car.getSpeed():
        car.setSpeed(-150)
        car.getData()
    car.setSpeed(0)
    return True


def turn_the_car(car,s,t):
    time_ref = time.time()
    while((time.time()-time_ref)<t):
        car.getData()
        car.setSteering(s)
        car.setSpeed(60)



def turning_the_car(car,s,t):
    time_ref = time.time()
    while((time.time()-time_ref)<t):
        car.getData()
        car.setSteering(s)
        car.setSpeed(50)

'''
def go_back(car):
    #time_ref = time.time()
    dFront2 = 0
    while(dFront2!=float('inf')):
        car.getData()
        car.setSpeed(-30)
        newImage,dFront,Dleft,Dright,midline_status, mySide, right_points, left_points, right_lines, horizontal_lines, left_lines, dFront2 =linesdetect.white_lines_Distance(car.getImage(), 15, 75, 15)
    print("outttttt")
'''

def go_back(car, t):
    #newImage,dFront,Dleft,Dright,midline_status, mySide, right_points, left_points, right_lines, horizontal_lines, left_lines, dFront2 =linesdetect.white_lines_Distance(imageCopy, 15, 95, 40)
    time_ref = time.time()
    while((time.time()-time_ref)<t):
        car.getData()
        car.setSpeed(-80)
    
def find_intersection(lines,colored_line):
    for line in lines:
        x1, y1, x2, y2 = line[0]
        x3, y3 = colored_line[0][0]
        x4, y4 = colored_line[0][1]

        # Calculate intersection point using line equations
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
                continue
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
                
        if 0 <= t <= 1 and 0 <= u <= 1:
                    return True

    return False    

def turn_left(image,car,red_len,pink_len):

    global red_point,end_crossroad,yellow

    steering_deg = 0
    height, width = image.shape[:2]
    car_position = (width // 2, height - 117)

    left_lines = []
    right_lines = []
    horizontal_lines = []

    left_lines,right_lines,horizontal_lines = linesdetect.lines_Categorize (image)

    yellow_line = np.array([[(300, car_position[1] ), (550, car_position[1] )]], dtype=np.int32)
    green_line = np.array([[(car_position[0], car_position[1] - 10), (car_position[0], car_position[1] - 90)]], dtype=np.int32)
   
    cv2.polylines(image, yellow_line, isClosed=True, color=(0, 255, 255), thickness=4)

    # find_intersection between horizontal_lines  and red_line 
    if(not red_point and not end_crossroad):
        red_line = np.array([[(car_position[0]-3, car_position[1] -130 ), (car_position[0]-3, car_position[1] - red_len)]], dtype=np.int32)
        cv2.polylines(image, red_line, isClosed=True, color=(0, 0, 255), thickness=2)
        if(find_intersection(horizontal_lines,red_line)):
            red_point = True
                   
    if(find_intersection(left_lines,green_line)):
          end_crossroad = True  
          red_point = False
         
    #end of turn_left and switch operation
    end = False 
   
    if(end_crossroad):
        if(find_intersection(left_lines + right_lines,yellow_line)):
            yellow = True

        if(yellow) :
             pink_line = np.array([[(car_position[0],car_position[1] - 100), (car_position[0]-pink_len,car_position[1] - 100)]], dtype=np.int32)
             cv2.polylines(image, pink_line, isClosed=True, color=(255, 0, 255), thickness=4)

             if(find_intersection(left_lines ,pink_line)):
                yellow =  False
                print('exit')
                end_crossroad = False
                end = True

    if(red_point or end_crossroad  ):
        steering_deg = -90   

   
    car.setSteering(steering_deg)    


    return end

def turn_right(car, image, dFront, Dright, right_lines, straight_right):
                    global yellow, yellow_on
                    height = 512
                    width = 512
                    car_position = (width // 2, height - 117)
                    roadStatus = 0

                    if(dFront == float('inf') and yellow_on== False) : 
                        yellow = True

                    if(yellow):
                        yellow_on = True
                        yellow_line = np.array([[(-100, car_position[1] + 110), (250, car_position[1] + 110 )]], dtype=np.int32)
                        cv2.polylines(image, yellow_line, isClosed=True, color=(0, 255, 255), thickness=4)

                        if(find_intersection(right_lines,yellow_line)):
                            yellow = False

                    if(not yellow and yellow_on ):
                        pink_line = np.array([[(car_position[0]+130,car_position[1] - 100), (car_position[0],car_position[1] - 100)]], dtype=np.int32)
                        cv2.polylines(image, pink_line, isClosed=True, color=(255, 0, 255), thickness=4)

                        if(find_intersection(right_lines,pink_line)):
                             yellow_on = False
                             roadStatus=1
                             return 1

                       
                    if(roadStatus != 1):
                        if(Dright==0):
                            straight_right=False
                        if(straight_right and Dright!=0):
                            if(dFront != float('inf')):car.setSteering(abs(dFront-90))
                            else:car.setSteering(70)
                            car.setSpeed(20)
                            return 2
                        if(Dright==0 and dFront != float('inf')):
                            car.setSpeed(20)
                            car.setSteering(abs(dFront-80))
                            return 3

def turn_obstacles(num_sensors, steering, car):
                angle = 20
                #car.setSensorAngle(angle)
                print("start")
                if(sw_left):
                    switch = False
                    print(sensors[num_sensors],"sen1111")
                    car.setSteering(-abs((sensors[num_sensors]/40)-70))
                    if(sensors[2]<1000):
                        switch= True
                    while(switch):
                        sw_left=False
                        car.getData()
                        sensors = car.getSensors() 
                        print(sensors[2],"sen222222")
                        car.setSteering(-abs((sensors[2]/40)-70))
                        if(sensors[2]>=1500):
                            print(angle, "angle")
                            angle = angle+5
                            car.setSensorAngle(angle)
                        if(angle>53):
                            print("false switch left###################################")
                            switch = False
                            break
                if(not sw_left):
                    car.setSensorAngle(20)
                    turn_the_car(car,65,2.5)
                    print("go to road 1")

def FindMistake(myCar):
    #برای بررسی اینکه آیا سنسورها مانعی را کشف کرده اند یا خیر و اینکه مانع اگر در طرف ما هست عدد 1
    myCar.setSensorAngle(5)
    base=900
    
    LeftSideCount=0
    RightSideCount=0

    StartSensorsData=myCar.getSensors()
    if any(x < base for x in StartSensorsData): 
        for degree in range(45):
            myCar.setSensorAngle(degree)
            sensorsData=myCar.getSensors()
            if sensorsData[0]<1000: LeftSideCount+=1
            if sensorsData[2]<1000: RightSideCount+=1
        myCar.setSensorAngle(0)
        if RightSideCount>=LeftSideCount: return 1
        elif RightSideCount<LeftSideCount: return -1
    else: return 0                    

def findTheBestMistakeMax(mySpeed):
    result = 0
    if mySpeed!=0: result= (170/mySpeed )
    print("^^^^^^^^^^^^^^^^^^^", result)
    #if mySpeed<10: result+=11
    #elif mySpeed>10: result+=11
    #cv2.putText(image, f'MistakeMax: {MistakeMax}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)    
    return result      
              