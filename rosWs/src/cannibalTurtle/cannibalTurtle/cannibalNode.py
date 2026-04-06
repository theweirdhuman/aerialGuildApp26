'''
FILENAME: cannibalNode.py
AUTHOR: Ashwin K (EE25B018)
DESCRIPTION: Turtlesim game where a player controls a turtle to catch randomly spawning prey.


processes to run to start the game:
ros2 run turtlesim turtlesim_node
ros2 run cannibalTurtle cannibalNode 
ros2 run turtlesim turtle_teleop_key
'''

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
from turtlesim.msg import Pose
from turtlesim.srv import Kill
from random import random

class cannibalNode(Node):
    
    def __init__(self):
        """
        Initializes the Node
        
        Variables:
        score: total score of the player
        timeLeft: starts at 30s, decremented in the game loop
        dt: time decrement
        spawnTime: used to keep track of the latest prey spawn time
        killed: checks if prey is active
        preyX: x coord of prey
        preyY: y coord of prey
        posePlayer: stores coords of player
        """
                
        super().__init__('cannibal')
        
        #initialize variables
        self.score = 0
        self.timeLeft = 30.0
        self.dt = 0.1
        self.spawnTime = 30.0
        self.killed = True
        self.preyX = None
        self.preyY = None
        self.posePlayer = None
        
        #spawn turtles
        self.toSpawn = self.create_client(Spawn, '/spawn')
        self.toSpawn.wait_for_service()
        
        
        #create subscription to get player position
        self.subPlayer = self.create_subscription(Pose,'turtle1/pose',self.posePlayerCallback,10)
        
        #create a kill client
        self.killClient = self.create_client(Kill, '/kill')
        self.killClient.wait_for_service()
        
        
        #run the game loop on repeat        
        timer_period = 0.1
        self.timer = self.create_timer(timer_period,self.gameLoop)
        
        
        
    def spawnTurtles(self):
        """
        spawns prey turtles randomly
        
        Returns:
        (x,y) coordinate of the spawned turtle        
        """
        
        prey = Spawn.Request()
        prey.x = random()*9+1
        prey.y = random()*9+1
        prey.theta = random()*6.28 - 3.14  
        prey.name = 'prey'
        self.toSpawn.call_async(prey)
        
        return (prey.x, prey.y)
        
        
    def kill(self):
        """
        kills spawned prey, either on 'catching' or timeout
        """
        
        req = Kill.Request()
        req.name = 'prey'
        self.killClient.call_async(req)

        
    def posePlayerCallback(self,pos):
        """
        callback function to receive player position
        """
        
        self.posePlayer = pos
    
        
    def gameLoop(self):
        """
        main game loop that repeats every 0.1 second
        """
        
        #print remaining time every 5 seconds
        if int(self.timeLeft*10)%50 == 0:
            print("\t\t\tTime remaining:",int(self.timeLeft))
        
        #decrement time left
        self.timeLeft-=self.dt
        
        #end game if remaining time elapses
        if self.timeLeft < 0:
            if not self.killed:
                self.kill()
            print("Game Over!")
            print("Final Score:",self.score)
            self.timer.cancel()
            return
        
        #kill prey if it has been more than 6 seconds since spawn
        if self.spawnTime-self.timeLeft >= 6:
            self.kill()
            self.killed = True
        
        #spawn turtle if not present
        if self.killed:
            self.preyX,self.preyY = self.spawnTurtles()
            self.spawnTime = self.timeLeft
            self.killed = False
        
        
        
        #kill prey if player reaches it
        if self.posePlayer is not None and self.preyX is not None and self.preyY is not None:
            playerHits = abs(self.preyX - self.posePlayer.x) < 0.5 and abs(self.preyY - self.posePlayer.y) < 0.5
            
            if playerHits and not self.killed:
                self.kill()
                self.score+=1
                print("Score",self.score)
                self.killed = True
        

def main():
    rclpy.init()
    print("Welcome to Teenage Mutant Cannibal Turtles!\n")
    print("You have 30 seconds to eat as many turtles as possible!")
    print("Use the arrow keys to control your turtle.\n")
    node = cannibalNode()
    rclpy.spin(node)
    rclpy.shutdown()