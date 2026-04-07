'''
FILENAME: droneControlNode.py
DESCRIPTION: Controls the drone to rise to 5.5m, hover for 5s and then land.


processes to run:

make px4_sitl gz_x500

./QGroundControl-x86_64.AppImage 

ros2 run mavros mavros_node \
  --ros-args \
  -p fcu_url:=udp://:14540@127.0.0.1:14557

ros2 run droneControl control
'''


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, SetMode
from rclpy.qos import QoSProfile, ReliabilityPolicy

class droneControl(Node):
    def __init__(self):
        super().__init__('drone_control')

        # Publisher
        self.pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT

        # Subscriber
        self.sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self.pose_callback,
            qos
        )

        # Services
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        self.timer = self.create_timer(0.1, self.loop)

        # State
        self.current_z = 0.0
        self.takeoff_alt = 5.5
        self.counter = 0
        self.phase = "INIT"
        self.hover_start_time = None
        self.altitude_reached = False

    def pose_callback(self, msg):
        self.current_z = msg.pose.position.z

    def loop(self):
        # Always publish setpoint
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = 0.0
        msg.pose.position.y = 0.0
        msg.pose.position.z = self.takeoff_alt
        self.pub.publish(msg)

        # Prints state
        if self.counter % 10 == 0:
            self.get_logger().info(f"[STATE] {self.phase} | Z={self.current_z:.2f}")

        # ---- INIT ----
        

        if self.phase == "INIT" and self.counter == 20:
            self.get_logger().info("Switching to OFFBOARD...")
            if self.mode_client.wait_for_service(timeout_sec=2.0):
                req = SetMode.Request()
                req.custom_mode = "OFFBOARD"
                self.mode_client.call_async(req)
                


        if self.phase == "INIT" and self.counter == 50:
            self.get_logger().info("Arming...")
            if self.arm_client.wait_for_service(timeout_sec=2.0):
                req = CommandBool.Request()
                req.value = True
                self.arm_client.call_async(req)
                self.phase = "TAKEOFF"

        # ---- TAKEOFF ----
        if self.phase == "TAKEOFF":
            if self.current_z >= 5.4 and not self.altitude_reached:
                self.get_logger().info("Reached altitude → start hover")
                self.hover_start_time = self.get_clock().now()
                self.altitude_reached = True
                self.phase = "HOVER"

        # ---- HOVER ----
        if self.phase == "HOVER":
            elapsed = (self.get_clock().now() - self.hover_start_time).nanoseconds / 1e9

            if self.counter % 10 == 0:
                self.get_logger().info(f"[HOVER] {elapsed:.2f}s")

            if elapsed >= 5.0:
                self.get_logger().info("Landing...")
                if self.mode_client.wait_for_service(timeout_sec=2.0):
                    req = SetMode.Request()
                    req.custom_mode = "AUTO.LAND"
                    self.mode_client.call_async(req)
                self.phase = "LAND"

        self.counter += 1


def main():
    rclpy.init()
    node = droneControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()