import sys
import os
current = os.path.dirname(os.path.realpath(__file__))# getting the name of the directory where the this file is present.
parent = os.path.dirname(current) # Getting the parent directory name where the current directory is present.
sys.path.append(parent)  # adding the parent directory to the sys.path.
##meeeeeeeeeeeeeeeeeeeeeeeememmmmmemmememmemememmemmemememememememememeemem
import avisengine
import config
import time
import cv2
import numpy as np
import control as con
import signs
import csv
import os
import linesdetect

# Creating an instance of the Car class
car = avisengine.Car()

# Connecting to the server (Simulator)
car.connect(config.SIMULATOR_IP, config.SIMULATOR_PORT)

# Counter variable
counter = 0

debug_mode = False
#debug_mode = True

global yellow 
yellow = False

global yellow_on
yellow_on = False

global turn 
turn = 0

global sw_left 
sw_left = False

global count 
count = 264

global is_april
is_april = False

global_startLeft = False


number = 0
save_turn = 0
end_crossroad= True

# Sleep for 3 seconds to make sure that client connected to the simulator 
time.sleep(3)

#to find where we are ! 
directionBase=1
afterMistakeCounter=0
MistakeMax= 300
roadStatus=1
straight_right = True
turn_right = 1
sw=0
curve_right = False
curve_left = False
start_timer = time.time()
try:
    '''
     with open("dataset/output.csv", "w", newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(["ImageIndex", "angle", "speed"])  # Add headers
    '''
   
    while(True):
        # Counting the loops
        counter = counter + 1

        # Set the power of the engine the car to 20, Negative number for reverse move, Range [-100,100]
        

        # Set the Steering of the car -10 degree from center, results the car to steer to the left
        
        
        # Set the angle between sensor rays to 45 degrees, Use this only if you want to set it from python client
        # Notice: Once it is set from the client, it cannot be changed using the GUI
        car.setSensorAngle(30) 

        # Get the data. Need to call it every time getting image and sensor data
        car.getData()



        # Start getting image and sensor data after 4 loops
        if(counter > 4):

            # Returns a list with three items which the 1st one is Left sensor data\
            # the 2nd one is the Middle Sensor data, and the 3rd is the Right one.
            sensors = car.getSensors() 

            # Returns an opencv image type array. if you use PIL you need to invert the color channels.
            image = car.getImage()

            # Returns an integer which is the real time car speed in KMH
            carSpeed = car.getSpeed()

            if(debug_mode):
                print(f"Speed : {carSpeed}") 
                print(f'Left : {str(sensors[0])} | Middle : {str(sensors[1])} | Right : {str(sensors[2])}')
            
            imageCopy=image

            newImage,dFront,Dleft,Dright,midline_status, mySide, right_points, left_points, right_lines, horizontal_lines, left_lines, dFront2 =linesdetect.white_lines_Distance(imageCopy, 15, 90, 40)

            
            #car.setSensorAngle(30)
            apriltagValue=signs.detect_april_tag(imageCopy)
            #cv2.putText(image, f'Sign: {apriltagValue}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if apriltagValue!=-100 : 
                 save_turn = apriltagValue
                 is_april = True
                 if(car.getSpeed()>=24):
                     car.setSpeed(10)
                 #curveStatus= 'No curve'
            #print("is_april==",is_april,"dFront==",dFront,"roadStatus==",roadStatus)     
            if (is_april) and (dFront<float('inf') and roadStatus==1): 
                print("crosssssssssssssssss")
                roadStatus=2
            '''
            isThereMistake=con.FindMistake(car) 
            MistakeMax= con.findTheBestMistakeMax(carSpeed)
            if isThereMistake==1: qa
                if(roadStatus!=2 and yellow_on==False and end_crossroad):
                    directionBase=-1
                    afterMistakeCounter=0
                    print("1111111111111")
                    car.setSpeed(30)
                    roadStatus=4
            '''
            car.setSensorAngle(30)
            if roadStatus==1: # مسیر عادی
                #print("in Status 1")
                if(not is_april):curveStatus=linesdetect.curve_finder(dFront2, Dleft, Dright)
                #cv2.putText(image, f'Curve Status: {curveStatus}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                #cv2.putText(image, f'Dfront: {dFront}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                frame = cv2.resize(image,(256,256))
                gray_scale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
                white_mask = cv2.inRange(frame, np.array([240,240,240]), np.array([255,255,255]))
                side_mask = cv2.inRange(frame, np.array([130,0,108]), np.array([160,160,200]))
                lines = con.detect_lines(con.region_of_interest(white_mask))
                side_line_mask,present_pxl = con.find_lines(white_mask, lines)
                side_pixl = con.detect_side(white_mask)
                car.setSpeed(45)
                #print(present_pxl)
                error = 128- present_pxl
                steering = -2.3*error
                car.setSteering(steering)

               
             

                '''                                                                                         
                if sensors[1] < 600:
                    #con.stop_car(car)
                    if side_pixl > 128:
                        x=0
                        if(car.getSpeed()<10): frm =50
                        else : frm = 0
                        while(sensors[1]<1500 or sensors[2]<1500 or x<frm):
                             car.getData()
                             car.setSensorAngle(39)
                             sensors = car.getSensors()
                             car.setSteering(-200)
                             car.setSpeed(60)
                             print("in while")
                             x+=1
                            # print(con.FindMistake(car))
                        #con.turn_the_car(car,-100,2.2)
                      
                        #print(con.FindMistake(car))
                        while(con.FindMistake(car)==1):
                            car.getData()
                            car.setSteering(-200)
                            car.setSpeed(60)
                       
                        con.turn_the_car(car,100,1.8)
                        con.turn_the_car(car,-100,0.75)
                '''
                
                if sensors[1] < 700 :
                    #con.stop_car(car)
                    x = 30
                    if side_pixl > 128:
                        print("obstacle is hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                        if(car.getSpeed()<10):
                            times = 1.5
                            streeng = -77
                            number = 400
                            print("speed kamtar as 10")
                        elif(car.getSpeed()<15) :
                            print("speed kamtar as 15")
                            times = 1.6
                            streeng = -77
                            number = 400
                        else : 
                            print("speed kamtar as 20")
                            times = 1.25
                            streeng = -77
                            number = 500
                        while True:
                             car.getData()
                             x=x+0.13
                             car.setSensorAngle(80)
                             sensors = car.getSensors()
                             car.setSteering(streeng)
                             car.setSpeed(60)
                             if(sensors[2]<number):
                                print("break")
                                break
                             #print(x, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                        #con.turn_the_car(car,-100,2.2)
                        con.turn_the_car(car,100,times)
                        #con.turn_the_car(car,-100,0.6)
                
                '''
                if sensors[1]<1200:
                    
                    print("road == 444444444444444444444444444444444444444")
                    sw_left = True
                    roadStatus = 4
                    
                    if(500<sensors[1]<1100):
                        number=1
                    elif(sensors[0]<1200):
                        number=0
                        print("%$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    
                    #command = con.stop_car(car)
                    
                
                    
                    con.turn_the_car(car,-25,2.6)
                    con.turn_the_car(car,65,3)
                    '''
                    #con.turn_the_car(car,-100,2.4)

                swich = True
                if curveStatus == 'Turn right' :
                    curveStatus = 'No curve'
                    #con.turning_the_car(car,100,6.5)
                    #print(mean_pixl)
                    #command = con.stop_car(car) 
                    print(dFront2, "dfronnnnt")
                    if(dFront != float('inf')):
                       command = con.stop_car(car) 
                       car.getData()
                       con.go_back(car, 1.8)
                       con.turning_the_car(car,200,6)
                       print("curve stop mode")
                       
                    
                    else:
                        while True:
                            print("left curve in not stop")
                            car.setSteering(200)
                            car.setSpeed(70)
                            car.getData()
                            image = car.getImage()
                            pink_line = np.array([[(car_position[0],car_position[1] - 100), (car_position[0]+130,car_position[1] - 100)]], dtype=np.int32)
                            cv2.polylines(image, pink_line, isClosed=True, color=(255, 255, 0), thickness=2)
                            cv2.imshow('Result', image)
                            left_lines,right_lines,horizontal_lines = linesdetect.lines_Categorize (image)
                            if(con.find_intersection(right_lines, pink_line)):
                                break
                        #con.turning_the_car(car,200,1.8)
                        
                
                elif curveStatus == 'Turn left':
                    curveStatus = 'No curve'
                    #con.turning_the_car(car,-100,6.45)
                    #print(mean_pixl)
                    print(dFront2, "dfr*&*&&*&*&*&*&&&*")
                    if(dFront != float('inf')):
                       command = con.stop_car(car)
                       con.go_back(car, 1.7)
                       con.turning_the_car(car,-100,6)
                       
                    #con.go_back(car, 5)
                    
                    else:
                        while True:
                            print("left curve in not stop")
                            car.setSteering(-200)
                            car.setSpeed(70)
                            car.getData()
                            image = car.getImage()
                            pink_line = np.array([[(car_position[0],car_position[1] - 100), (car_position[0]-100,car_position[1] - 100)]], dtype=np.int32)
                            cv2.polylines(image, pink_line, isClosed=True, color=(255, 255, 0), thickness=2)
                            cv2.imshow('Result', image)
                            left_lines,right_lines,horizontal_lines = linesdetect.lines_Categorize (image)
                            if(con.find_intersection(left_lines, pink_line)):
                                break
                        #con.turning_the_car(car,-200, 1.8)
                
                #print(isThereMistake)
                #print(curveStatus)

                #myCarControl_1()
            
            if roadStatus==2: # نزدیک چهارراه
                is_april = False
                drawing_pink = False
                turn = save_turn
                car.setSteering(0)
                command = con.stop_car(car)
                time.sleep(3)
                roadStatus = 3

                #کم کردن سرعت و توفق به مدت سه ثانیه و بعد از سه ثانیه تبدیل حالت به 3
                #myCarControl_2()
            straight_right=True
            if roadStatus==3: #وسط چهارراه
                if(turn==2): #turn right
                    
                    height, width = imageCopy.shape[:2]
                    car_position = (width // 2, height - 117)
                    Steering = 0

                    if(dFront == float('inf') and yellow_on== False) : 
                        yellow = True

                    if(yellow):
                        yellow_on = True
                        yellow_line = np.array([[(-100, car_position[1] + 110), (250, car_position[1] + 110 )]], dtype=np.int32)
                        cv2.polylines(image, yellow_line, isClosed=True, color=(0, 255, 255), thickness=10)

                        if(con.find_intersection(right_lines,yellow_line)):
                            yellow = False

                    if(not yellow and yellow_on ):
                        pink_line = np.array([[(car_position[0]+160,car_position[1] - 100), (car_position[0],car_position[1] - 100)]], dtype=np.int32)
                        cv2.polylines(image, pink_line, isClosed=True, color=(255, 0, 255), thickness=10)

                        if(con.find_intersection(right_lines,pink_line)):
                             yellow_on = False
                             print('exit')
                             turn = 0
                             roadStatus=1

                       
                    if(roadStatus != 1):
                        if(Dright==0):
                            straight_right=False
                        if(straight_right and Dright!=0):
                            if(dFront != float('inf')):car.setSteering(abs(dFront-90))
                            else:car.setSteering(80)
                            car.setSpeed(100)
                        if(Dright==0 and dFront != float('inf')):
                            car.setSpeed(100)
                            car.setSteering(abs(dFront-80))
                    
                elif(turn==3):#turn left
                       if(Dleft!=0 or Dright!=0):
                        count = count+1
                        car.setSpeed(60)
                           
                       else: 
                        global_startLeft=True
                       if (global_startLeft):
                        car.setSpeed(100)
                        end = con.turn_left(imageCopy,car,144.5,180)
                        if(end) :
                            turn = 0
                            global_startLeft=False
                            roadStatus = 1
                       
                        
                        '''
                        if sensors[0] < 1200 or sensors[1]< 1200:
                          
                          if side_pixl > 128:
                           
                            con.turn_the_car(car,-80,1.9)
                            con.turn_the_car(car,80,2.2)
                            con.turn_the_car(car,-100,1)
                      
                            #con.turn_the_car(car,-100,2.5)
                            roadStatus = 1
                        '''
                        
                elif(turn==5): #stop
                    car.stop()
                elif(turn == 1 or turn==4):#straight:#straight
                        cv2.putText(image, f'Dfront: {dFront}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        frame = cv2.resize(image,(256,256))
                        gray_scale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
                        white_mask = cv2.inRange(frame, np.array([240,240,240]), np.array([255,255,255]))
                        side_mask = cv2.inRange(frame, np.array([130,0,108]), np.array([160,160,200]))
                        lines = con.detect_lines(con.region_of_interest(white_mask))
                        side_line_mask,present_pxl = con.find_lines(white_mask, lines)
                        side_pixl = con.detect_side(white_mask)
                        #cv2.imshow("side_mask",side_line_mask)
                        car.setSpeed(100)
                        #print(present_pxl)
                        error = 128- present_pxl
                        steering = -0.1*error
                        car.setSteering(0)
                        if(dFront == float('inf')):
                            drawing_pink = True
                        if(drawing_pink):
                            height, width = imageCopy.shape[:2]
                            car_position = (width // 2, height - 117)
                            pinkline = np.array([[(car_position[0], car_position[1]-50), (car_position[0]-300, car_position[1] - 50)]], dtype=np.int32)
                            cv2.polylines(image, pinkline, isClosed=True, color=(255, 0, 255), thickness=2)
                            front_points = []
                           
                            for line in left_lines:
                                x1, y1, x2, y2 = line[0]
                                x3, y3 = pinkline[0][0]
                                x4, y4 = pinkline[0][1]
                                
                                # Calculate intersection point using line equations
                                denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                                if denominator == 0:
                                  continue
                                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
                                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
                                
                                if 0 <= t <= 1 and 0 <= u <= 1:
                                    x = int(x1 + t * (x2 - x1))
                                    y = int(y1 + t * (y2 - y1))
                                    front_points.append(y)
                                    frontx = x
                            if front_points:
                                roadStatus = 1

                            
                #myCarControl_3()
            if(roadStatus==4):
                car.setSpeed(35)
                '''
                                angle = 20
                #car.setSensorAngle(angle)
                print("start")
                if(sw_left):
                    switch = False
                    print(sensors[number],"sen1111")
                    car.setSteering(-abs((sensors[number]/40)-70))
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
                    con.turn_the_car(car,65,2.5)
                    print("go to road 1")
                '''

                if afterMistakeCounter>MistakeMax:
                    directionBase=1
        
                afterMistakeCounter=afterMistakeCounter+1

                print("directionBase_______________________________________",directionBase)
                if(directionBase==1 and Dleft>5):
                   Degree=50+((Dleft)//3)      
                elif(directionBase==1 ):
                    Degree=50+((Dright)//3) 


                if(Dleft < 5):
                    sw = 1
                if(directionBase==-1 and sw==0 ):
                   print("leeeeefffftttttttt$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",Dleft)
                   Degree=-111-((Dleft)//3)  


                elif(directionBase==-1 ):
                    print("rrrrrrrrrrriii============",Dright)
                    Degree=-111-(Dright)//3   

                car.setSteering(Degree)
                   
                
            # نمایش تصویر
            cv2.imshow('Result', image)

            if cv2.waitKey(10) == ord('q'):
                break

            time.sleep(0.001)

finally:
    print(time.time()-start_timer, ": time")
    car.stop()
