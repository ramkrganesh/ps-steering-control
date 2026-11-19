import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ThrottleReceiver(Node):
    def __init__(self):
        super().__init__('throttle_receiver')
        self.t_subscriber = self.create_subscription(String,
                                                     'steering_data',
                                                     self.throttle_callback,
                                                     10)
        #self.t_subscriber  # just to avoid warnings


    def throttle_callback(self, msg):
        self.get_logger().info(f"Received Throttle value: {msg.data}%")

if __name__ == "__main__":
    rclpy.init()
    t_sub = ThrottleReceiver()
    try:
        rclpy.spin(t_sub)
    except KeyboardInterrupt as e:
        print(f"{e}")
    finally:
        if rclpy.ok():  # when ctrl+C is pressed, the nodes are already shutdown and this returns False
            t_sub.destroy_node()
            rclpy.shutdown()
