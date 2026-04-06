'''
processes to run:
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
        super().__init__('cannibal')
        
        self.lives = 3
        self.get_logger().info("You have 3 lives")
        self.gameOver = False
        self.score = 0
        self.timeLeft = 30.0
        self.dt = 0.1
        self.spawnTime = 30.0
        self.killed = True
        #spawn turtles
        self.preyX = None
        self.preyY = None
        self.toSpawn = self.create_client(Spawn, '/spawn')
        self.toSpawn.wait_for_service()
        
        
        
        
        #create subscription
        
        self.posePlayer = None
        
        
        self.subPlayer = self.create_subscription(Pose,'turtle1/pose',self.posePlayerCallback,10)
        
        self.killClient = self.create_client(Kill, '/kill')
        self.killClient.wait_for_service()
        
        
        timer_period = 0.1
        self.timer = self.create_timer(timer_period,self.gameLoop)
        
        
        
    def spawnTurtles(self):
        
        prey = Spawn.Request()
        prey.x = random()*9+1
        prey.y = random()*9+1
        prey.theta = random()*6.28 - 3.14  
        prey.name = 'prey'
        self.toSpawn.call_async(prey)
        
        return (prey.x, prey.y)
        
        
    def kill(self):
        req = Kill.Request()
        req.name = 'prey'
        self.killClient.call_async(req)

        
    def posePlayerCallback(self,pos):
        self.posePlayer = pos
    

        
        
    def gameLoop(self):
        self.timeLeft-=self.dt
        
        if self.timeLeft < 0:
            print("Game Over")
            self.timer.cancel()
            return
        
        if self.killed:
            self.preyX,self.preyY = self.spawnTurtles()
            self.spawnTime = self.timeLeft
            self.killed = False
        
        if self.spawnTime-self.timeLeft >= 6:
            self.kill()
            self.killed = True
            
        
        #Eating
        if self.posePlayer is not None and self.preyX is not None and self.preyY is not None:
            playerHits = abs(self.preyX - self.posePlayer.x) < 0.5 and abs(self.preyY - self.posePlayer.y) < 0.5
            if playerHits:
                self.kill()
                self.score+=1
                print(self.score)
                self.killed = True
        

def main():
    rclpy.init()
    node = cannibalNode()
    rclpy.spin(node)
    rclpy.shutdown()