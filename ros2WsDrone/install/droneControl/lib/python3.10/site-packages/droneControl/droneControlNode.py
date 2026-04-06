import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, SetMode

class droneControl(Node):
    def __init__(self):
        super().__init__('drone_control')

        # Publisher
        self.pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )

        # Service clients
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        # Timer loop (10 Hz)
        self.timer = self.create_timer(0.1, self.loop)

        self.counter = 0
        self.phase = "INIT"

    def loop(self):
        # Always publish setpoint
        msg = PoseStamped()
        msg.pose.position.x = 0.0
        msg.pose.position.y = 0.0
        msg.pose.position.z = 5.5

        self.pub.publish(msg)

        # ---- PHASE LOGIC ----

        # 1. Wait before arming (send setpoints first)
        if self.counter == 20:
            self.arm()
            self.set_mode("OFFBOARD")
            self.phase = "TAKEOFF"

        # 2. Hover after reaching altitude (~5 sec)
        if self.counter == 100:
            self.get_logger().info("Hovering complete, landing...")
            self.set_mode("AUTO.LAND")
            self.phase = "LAND"

        self.counter += 1

    def arm(self):
        req = CommandBool.Request()
        req.value = True
        self.arm_client.call_async(req)
        self.get_logger().info("Arming...")

    def set_mode(self, mode):
        req = SetMode.Request()
        req.custom_mode = mode
        self.mode_client.call_async(req)
        self.get_logger().info(f"Switching to {mode}")


def main():
    rclpy.init()
    node = droneControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
