# V5RC High Stakes simulator
This is a simulator I made using Pygame because I was bored. It's main purpose is for planning out auton routes.

Note: Considering this was made on my computer, if you download it you will have to change the file paths in #main.py


## Auton
So basically, you just say what actions you want the robot to do in the actions list. Uses some simple trig to make the robot go a certain distance at the angle the robot is at currently. There are no curve options enabled because I am not using curves to code my actual robot so why have curves. There is still a working quadratic bezier function in curves.py. The purpose of this was so that I could try to code my autons at home instead of having to spend time doing it in the lab. To do this, every movement of the bot is logged into movement_log.txt in the format of the c++ functions that I use. This way I can just copy and paste from the movement log and hopefully my code works. Additionally, the position of the robot on the field (in inches) from the starting point and the angle of the robot are also printed on the screen. The path the robot follows is in green to ensure that it does not interfere with anything. 


## Driver
This was just for fun. You are able to move around using the arrow keys or WASD. Press C to pick up a mobile goal. Press I to turn on the intake (i was too lazy to make the rings actually scorable so the intake doesn't actually do anything). Speed and turns is proportional to my 450rpm 66w drivetrain. 


## Credits

https://www.path.jerryio.com for all of the field images and mobile goal images

the Fusion 360 V5RC CAD library for the robot picture

## Example images
![Screenshot 2024-11-27 at 11 15 43 PM](https://github.com/user-attachments/assets/d77936f8-7f6f-45ca-baaf-4ac340e1837e)
![Screenshot 2024-11-27 at 11 19 00 PM](https://github.com/user-attachments/assets/07f4a41b-8cf6-464a-ac90-e4401ce60476)
