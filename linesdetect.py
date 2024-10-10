import cv2
import numpy as np


def lines_Categorize (image):
    # Edge detection using Canny
    gray = cv2.cvtColor(image , cv2.COLOR_RGB2GRAY)
    gaussian = cv2.GaussianBlur(gray,(5,5),0)
    edges = cv2.Canny(gaussian,50,150,apertureSize=3)
    # Line detection using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)
    left_lines = []
    right_lines = []
    horizontal_lines = []
    slope = 0
    # Classify detected lines based on their slope
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x2-x1) > 1e-6:
            slope = (y2 - y1) / (x2 - x1)
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi 
        
        if abs(angle) < 10:
           # cv2.line(image,(x1, y1),(x2, y2),(0,0,255),2)
            horizontal_lines.append(line)

        elif slope < 0:
            #cv2.line(image,(x1, y1),(x2, y2),(0,255,0),2)
            left_lines.append(line)
        elif slope!=0:
           # cv2.line(image,(x1, y1),(x2, y2),(255,0,0),2)
            right_lines.append(line)

    return  left_lines, right_lines,horizontal_lines

def white_lines_Distance(image, greenLineStart, greenLineEnd, blueLineYDistance):
    """
    Detects the distance of white lines in the image from the car's current position.
    
    Args:
        image (numpy.ndarray): The input image on which line detection will be performed.
        
    Returns:
        tuple: Contains the processed image with annotated lines and circles,
               distance to the front line (disfront), 
               distance to the left line (disleft),
               distance to the right line (disright),
               midline status ("continuous" or "discontinuous"),
               side of the line where the car is ("Left" or "Right").
    """    
    height, width = image.shape[:2]
    car_position = (width // 2, height - 117)
    
    # Edge detection using Canny
    gray = cv2.cvtColor(image , cv2.COLOR_RGB2GRAY)
    gaussian = cv2.GaussianBlur(gray,(5,5),0)
    edges = cv2.Canny(gaussian,50,150,apertureSize=3)
    
    # Line detection using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)
    
    # Define reference lines (blue and green)
    blue_line = np.array([[(5 , car_position[1] - blueLineYDistance), (width - 5, car_position[1] - blueLineYDistance)]], dtype=np.int32)
    green_line = np.array([[(car_position[0], car_position[1] - greenLineStart), (car_position[0], car_position[1] - greenLineEnd)]], dtype=np.int32)
    red_line = np.array([[(car_position[0]+10, car_position[1] - greenLineStart), (car_position[0]+10, car_position[1] - greenLineEnd-35)]], dtype=np.int32)
    #blue_line2 = np.concatenate([blue_line-20, blue_line+20], axis=0)
    
    # Draw reference lines on the image
    cv2.polylines(image, blue_line, isClosed=True, color=(255, 0, 0), thickness=2)
    cv2.polylines(image, red_line, isClosed=True, color=(0, 0, 255), thickness=2)
    cv2.polylines(image, green_line, isClosed=True, color=(0, 225, 255), thickness=2)

    # Initialize lists for detected lines
    left_lines = []
    right_lines = []
    horizontal_lines = []

    # Classify detected lines based on their slope
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi 
        
        if abs(angle) < 10:
            horizontal_lines.append(line)
        elif slope < 0:
            left_lines.append(line)
        else:
            right_lines.append(line)
    
    # Sort lines by their y-intercept
    left_lines = sorted(left_lines, key=lambda line: line[0][1])
    right_lines = sorted(right_lines, key=lambda line: line[0][1])

    # Find intersections with the green line
    front_points = []
    for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        x3, y3 = green_line[0][0]
        x4, y4 = green_line[0][1]
        
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
    
    front_points2 = []
    for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        x3, y3 = red_line[0][0]
        x4, y4 = red_line[0][1]
        
        # Calculate intersection point using line equations
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            continue
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            front_points2.append(y)
            

    # Calculate distance to the front line
    if front_points:
        disfront = abs(min(front_points) - car_position[1]) - 10
       # cv2.circle(image, (frontx, min(front_points)), 5, (0, 0, 255), -1)  # Draw red circle
    else:
        disfront = float('inf')


    # Calculate distance to the front line
    if front_points2:
        disfront2 = abs(min(front_points2) - car_position[1]) - 10
       # cv2.circle(image, (frontx, min(front_points)), 5, (0, 0, 255), -1)  # Draw red circle
    else:
        disfront2 = float('inf')


    # Find intersections with the blue line
    intersection_points = []
    right_pointsX = []
    right_pointsY = []
    left_pointsX = []
    left_pointsY = []
    
    for side_lines in [left_lines, right_lines]:
        for line in side_lines:
            x1, y1, x2, y2 = line[0]
            x3, y3 = blue_line[0][0]
            x4, y4 = blue_line[0][1]
            
            # Calculate intersection point using line equations
            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if denominator == 0:
                continue
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
            
            if 0 <= t <= 1 and 0 <= u <= 1:
                x = int(x1 + t * (x2 - x1))
                y = int(y1 + t * (y2 - y1))
                intersection_points.append((x, y))
                
                # Classify intersection points based on car position
                if car_position[0] - x < 0:
                    right_pointsX.append(x)
                    right_pointsY.append(y)
                   # cv2.circle(image, (x, y), 5, (255, 0, 0), -1)  # Draw blue circle
                else:
                    left_pointsX.append(x)
                    left_pointsY.append(y)
                    #cv2.circle(image, (x, y), 5, (255, 0, 0), -1)  # Draw blue circle

    # Determine the status of the midline and the side of the line where the car is
    midline_status = "continuous"
    car_line_side = "Right"
    disright = 0
    disleft = 0
    
    if right_pointsX:
        disright = abs(min(right_pointsX) - car_position[0])
       # cv2.circle(image, (min(right_pointsX), min(right_pointsY)), 5, (255, 0, 255), -1)  
    else:
        car_line_side = "Left"
        midline_status = "discontinuous"
    
    if left_pointsX:
        disleft = abs(max(left_pointsX) - car_position[0])
       # cv2.circle(image, (max(left_pointsX), max(left_pointsY)), 5, (255, 255, 0), -1) 
    else:
        car_line_side = "Right"
        midline_status = "discontinuous"

    return image, disfront, disleft, disright, midline_status, car_line_side,right_pointsX,left_pointsX,right_lines, horizontal_lines,left_lines,disfront2



def curve_finder(disfront, disleft, disright):
    if (disfront != float('inf')):
        if disleft == 0:
            print("find curve in left*************************************8s")
            return "Turn left"
        elif disright == 0:
            print("find curve in right*************************************8s")
            return "Turn right"
        else:
            return 'No curve'
    else:
        return 'No curve'