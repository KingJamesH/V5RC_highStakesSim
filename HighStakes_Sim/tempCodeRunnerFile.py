import pygame
import sys
import math
import numpy as np
# import time 

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

BOT_SIZE = (SCREEN_WIDTH / 144) * 18
BOT_COLOR = (255, 0, 0)

BOT_WITH_GOAL_WIDTH = ((SCREEN_WIDTH / 144) * 18)
BOT_WITH_GOAL_LEN = ((SCREEN_WIDTH / 144) * 18 * 1.446)

BG_COLOR = (0, 0, 0)

GOAL_SIZE = (25 / 6) * 10

GREEN = (0,255,0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HST SIM")

background_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/fieldNoGoals.png')
# background_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/emptyField.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

bot_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/bot.png')
bot_image = pygame.transform.scale(bot_image, (int(BOT_SIZE), int(BOT_SIZE)))
bot_image = pygame.transform.rotate(bot_image, 270)

bot_with_goal_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/botWithGoal.png')
bot_with_goal_image = pygame.transform.scale(bot_with_goal_image, (int(BOT_WITH_GOAL_WIDTH), int(BOT_WITH_GOAL_LEN)))
bot_with_goal_image = pygame.transform.rotate(bot_with_goal_image, 270)

goal_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/goal.png')
goal_image = pygame.transform.scale(goal_image, (int(GOAL_SIZE + 8), int(GOAL_SIZE + 4)))

bot_x, bot_y = 50, 200  
starting_x, starting_y = 50, 200  

bot_angle = 180  
starting_angle = bot_angle  

bot_rot_speed = 10

goal_x = [200,200,400,400,300]
goal_y = [200,400,200,400,500]
goal_picked = [False, False, False, False, False]
speed = ((SCREEN_WIDTH / 144) * 6.38) * 0.5

log_file = "movement_log.txt"

font = pygame.font.SysFont(None, 30)
clamp_status = "Clamp OFF"
intake_status = "Intake OFF"

delay_time = 250
last_clamp_time = 0
last_intake_time = 0
last_reset_time = 0

pointList = [(starting_x, starting_y)]

def log_action(action):
    with open(log_file, 'a') as file:
        file.write("{}\n".format(action))

def add_point(pointX, pointY):
    global pointList
    newPoint = (pointX, pointY)
    pointList.append(newPoint)

def plot_points():
    global pointList
    if len(pointList) < 2:
        return  # No points to draw

    previousPoint = pointList[0]

    for point in range(1, len(pointList)):
        total_dist = math.sqrt((previousPoint[0] - pointList[point][0])**2 + (previousPoint[1] - pointList[point][1])**2)
        pygame.draw.line(screen, (0, 255, 0), previousPoint, pointList[point], width=3)

        pygame.draw.circle(screen, (0, 255, 0), pointList[point], 5)
        
        # Update previousPoint to the current point
        previousPoint = pointList[point]


def forward(distance):
    global bot_x, bot_y
    delta_x = distance * math.cos(math.radians(-bot_angle))
    delta_y = distance * math.sin(math.radians(-bot_angle))
    bot_x += delta_x
    bot_y += delta_y

    add_point(bot_x, bot_y)
    log_action("drivePIDC({},0);".format(distance / (25 / 6)))
    log_action("wait(0.5,seconds);")

def backward(distance):
    global bot_x, bot_y
    delta_x = distance * math.cos(math.radians(-bot_angle))
    delta_y = distance * math.sin(math.radians(-bot_angle))
    bot_x -= delta_x
    bot_y -= delta_y

    add_point(bot_x, bot_y)
    log_action("drivePIDC(-{},0);".format(distance / (25 / 6)))
    log_action("wait(0.5,seconds);")

def right(degrees):
    global bot_angle
    bot_angle -= degrees
    log_action("turnPD({});".format(degrees))
    log_action("wait(0.5,seconds);")

def left(degrees):
    global bot_angle
    bot_angle += degrees
    log_action("turnPD(-{})".format(degrees))
    log_action("wait(0.5,seconds);")

def compute_angle(px1, py1, px2, py2):
    delta_x = px2 - px1
    delta_y = py2 - py1
    angle_rad = math.atan2(delta_y, delta_x)  # Angle in radians
    return math.degrees(angle_rad)  # Convert to degrees

def bezierCurve(points):
    global bot_x, bot_y, bot_angle
    for p in [points[0], points[1], points[2]]:
        pygame.draw.circle(screen, (255, 255, 255), p, 5)

    previous_point = points[0] 
    for t in np.arange(0, 1, 0.01):
        px = points[0][0] * (1 - t) ** 2 + 2 * (1 - t) * t * points[1][0] + points[2][0] * t ** 2
        py = points[0][1] * (1 - t) ** 2 + 2 * (1 - t) * t * points[1][1] + points[2][1] * t ** 2

        add_point(px,py)

        angle = compute_angle(previous_point[0], previous_point[1], px, py)

        previous_point = (px, py) 
    
    # log_action("CURVE: " + points[0], + points[1] + points[2])
    bot_x = px
    bot_y = py
    bot_angle += angle
    

def clamp(state, log=True):
    global clamp_status, bot_image
    if state == 1:
        clamp_status = "Clamp ON"
        if log:
            log_action("Clamp.set(true);")
            log_action("wait(0.25,seconds);")
        check_goal_contact()
        
    elif state == 2:
        clamp_status = "Clamp OFF"
        if log:
            log_action("Clamp.set(false);")
            log_action("wait(0.25,seconds);")
        drop_goal()

def check_goal_contact():
    global bot_image
    for i in range(len(goal_x)):
        if not goal_picked[i]: 
            distance = math.sqrt((bot_x - goal_x[i]) ** 2 + (bot_y - goal_y[i]) ** 2)
            if distance < BOT_SIZE / 2 + GOAL_SIZE / 2:
                bot_image = bot_with_goal_image 
                goal_picked[i] = True 
                break

def drop_goal():
    global bot_image
    drop_distance = BOT_SIZE - 20 

    drop_x = bot_x - drop_distance * math.cos(math.radians(-bot_angle))
    drop_y = bot_y - drop_distance * math.sin(math.radians(-bot_angle))

    goal_width_half = (GOAL_SIZE + 8) / 2
    goal_height_half = (GOAL_SIZE + 4) / 2

    drop_x = max(goal_width_half, min(SCREEN_WIDTH - goal_width_half, drop_x))
    drop_y = max(goal_height_half, min(SCREEN_HEIGHT - goal_height_half, drop_y))

    for i in range(len(goal_x)):
        if goal_picked[i]:  
            goal_x[i], goal_y[i] = drop_x, drop_y  
            goal_picked[i] = False  
            bot_image = pygame.image.load('/Users/jameshou/Desktop/HighStakesSim/bot.png')
            bot_image = pygame.transform.scale(bot_image, (int(BOT_SIZE), int(BOT_SIZE)))
            bot_image = pygame.transform.rotate(bot_image, 270)
            break


def intake(state, log=True):
    global intake_status
    if state == 1:
        intake_status = "Intake ON"
        if log:
            log_action("intake.spin(forward,100,percent);")
            log_action("wait(0.25,seconds);")
    if state == 2:
        intake_status = "Intake OFF"
        if log:
            log_action("intake.stop();")

def getPos():
    x_inches = (bot_x - starting_x) / (25 / 6)
    y_inches = (bot_y - starting_y) / (25 / 6)
    return x_inches, y_inches

def getAngle():
    return bot_angle - starting_angle

actions = [
    (backward, 32 * (25 / 6)),
    (clamp, 1),
    (backward, 6 * (25 / 6)),
    (right, 90),
    (intake, 1),
    (forward, 22 * (25 / 6)),
    (right, 65),
    (forward, 14 * (25 / 6)),
    (backward, 6 * (25 / 6)),
    (right, 35),
    (forward, 8 * (25 / 6)),
    (backward, 6 * (25 / 6)),
    (right, 80),
    (intake, 2),
    (forward, 20 * (25 / 6)),
    (clamp, 2),
    (forward, 4 * (25 / 6))

    # (bezierCurve,[(50, 200), (150,500), (200,400)]),
    # (forward, 10*(25/6))
]

reverse_actions = []

current_action_index = 0

delay_time = 250
last_action_time = pygame.time.get_ticks()

running = True

print("Enter 1 for Autonomous mode or 2 for Manual mode: ")

try:
    user_input = input("Please enter your choice: ")
    x = int(user_input)
except ValueError:
    print("Invalid input. Please enter 1 or 2.")
    pygame.quit()
    sys.exit()

if x == 1:
    print("Autonomous mode activated.")
    log_action("~~~~~~~~~~RUN START~~~~~~~~~~")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        current_time = pygame.time.get_ticks()

        screen.fill(BG_COLOR)
        screen.blit(background_image, (0, 0))

        # Blit goals on the screen
        for i in range(len(goal_x)):
            if not goal_picked[i]:
                goal_rect = goal_image.get_rect(center=(goal_x[i], goal_y[i]))
                screen.blit(goal_image, goal_rect.topleft)

        if keys[pygame.K_RIGHT] and (current_time - last_action_time > 250):
            if current_action_index < len(actions):
                action, value = actions[current_action_index]
                reverse_actions.append((action, value))
                action(value)
                current_action_index += 1
                last_action_time = current_time

        if keys[pygame.K_LEFT] and (current_time - last_action_time > 250):
            if reverse_actions:
                last_action, last_value = reverse_actions.pop()
                if last_action == forward:
                    backward(last_value)
                elif last_action == backward:
                    forward(last_value)
                elif last_action == right:
                    left(last_value)
                elif last_action == left:
                    right(last_value)
                current_action_index -= 1
                last_action_time = current_time

        if clamp_status == "Clamp ON":
            check_goal_contact()  

        rotated_bot = pygame.transform.rotate(bot_image, bot_angle)
        rotated_rect = rotated_bot.get_rect(center=(bot_x, bot_y))
        screen.blit(rotated_bot, rotated_rect.topleft)

        half_bot_size = BOT_SIZE / 2
        bot_x = max(half_bot_size, min(SCREEN_WIDTH - half_bot_size, bot_x))
        bot_y = max(half_bot_size, min(SCREEN_HEIGHT - half_bot_size, bot_y))

        x_inches, y_inches = getPos()
        angle_deg = getAngle()

        position_text1 = font.render("X: {:.2f} in".format(x_inches), True, (255, 255, 255))
        screen.blit(position_text1, (SCREEN_WIDTH - 160, 20))

        position_text2 = font.render("Y: {:.2f} in".format(y_inches), True, (255, 255, 255))
        screen.blit(position_text2, (SCREEN_WIDTH - 160, 50))

        inertial_text = font.render("Inertial: {:.2f}".format(angle_deg), True, (255, 255, 255))
        screen.blit(inertial_text, (SCREEN_WIDTH - 160, 80))

        clamp_text = font.render(clamp_status, True, (255, 255, 255))
        intake_text = font.render(intake_status, True, (255, 255, 255))

        screen.blit(clamp_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60))
        screen.blit(intake_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 30))

        plot_points()

        pygame.display.flip()
        pygame.time.Clock().tick(30)


elif x == 2:
    print("Manual mode activated.")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        current_time = pygame.time.get_ticks()

        if keys[pygame.K_LEFT]:
            bot_angle += bot_rot_speed
        if keys[pygame.K_RIGHT]:
            bot_angle -= bot_rot_speed

        delta_x = speed * math.cos(math.radians(-bot_angle))
        delta_y = speed * math.sin(math.radians(-bot_angle))

        if keys[pygame.K_UP]:
            bot_x += delta_x
            bot_y += delta_y
        if keys[pygame.K_DOWN]:
            bot_x -= delta_x
            bot_y -= delta_y
        if keys[pygame.K_c] and (current_time - last_clamp_time > delay_time):
            if clamp_status == "Clamp OFF":
                clamp(1, False)
            else:
                clamp(2, False)
            last_clamp_time = current_time
        if keys[pygame.K_i] and (current_time - last_intake_time > delay_time):
            if intake_status == "Intake OFF":
                intake(1, False)
            else:
                intake(2, False)
            last_intake_time = current_time
        if keys[pygame.K_r] and (current_time - last_reset_time > delay_time):
            bot_angle = starting_angle 
            last_reset_time = current_time

        half_bot_size = BOT_SIZE / 2
        bot_x = max(half_bot_size, min(SCREEN_WIDTH - half_bot_size, bot_x))
        bot_y = max(half_bot_size, min(SCREEN_HEIGHT - half_bot_size, bot_y))

        screen.fill(BG_COLOR)
        screen.blit(background_image, (0, 0))

        for i in range(len(goal_x)):
            if not goal_picked[i]:
                goal_rect = goal_image.get_rect(center=(goal_x[i], goal_y[i]))
                screen.blit(goal_image, goal_rect.topleft)

        rotated_bot = pygame.transform.rotate(bot_image, bot_angle)
        rotated_rect = rotated_bot.get_rect(center=(bot_x, bot_y))
        screen.blit(rotated_bot, rotated_rect.topleft)

        clamp_text = font.render(clamp_status, True, (255, 255, 255))
        intake_text = font.render(intake_status, True, (255, 255, 255))

        screen.blit(clamp_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60))
        screen.blit(intake_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

else:
    print("Invalid option. Please restart the program and enter either 1 or 2.")
    pygame.quit()
    sys.exit()