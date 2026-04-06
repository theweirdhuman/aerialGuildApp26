# **Documentation:**

## Teenage Mutant Cannibal Turtles

A simple game built using ros2 and turtlesim where a player controls a turtle to catch randomly spawning turles (prey) in a given time limit.


Rules:
 - A prey turtle is randomly spawned in the game area.  
 - It will despawn after 6 seconds.  
 - Player's score increases if they reach the prey.  
 - Total time is 30 seconds.  

Controls:
Arrow keys on the teleop window.  

Output:
Time remaining and score.  

---


### **Code:**

**Node:**

cannibalNode  

**Functions in the node:**

__init__(self)  
Initializes the Node  

spawnTurtles(self)  
spawns prey turtles randomly  

kill(self)  
kills spawned prey, either on 'catching' or timeout  

posePlayerCallback(self,pos)  
callback function to receive player position  

gameLoop(self)  
main game loop that repeats every 0.1 second  

---

### **How to run:**

Build the workspace:
```
cd ~/rosWs
colcon build
source install/setup.bash
```

Start turtlesim, run teleop to control the turtle and run the game node:

```
ros2 run turtlesim turtlesim_node
ros2 run turtlesim turtle_teleop_key
ros2 run cannibalTurtle cannibalNode 
```