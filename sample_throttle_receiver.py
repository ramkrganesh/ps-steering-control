import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from json import loads as json_loads

class ThrottleReceiver(Node):
    def __init__(self):
        super().__init__('throttle_receiver')
        self.t_subscriber = self.create_subscription(String,
                                                     'steering_data',
                                                     self.throttle_callback,
                                                     5)
        #self.t_subscriber  # just to avoid warnings


    def throttle_callback(self, msg):
        steering_data = json_loads(msg.data)
        self.get_logger().info(f"Sent Steering Data- "
                               f"T:{steering_data["throttle"]:.2f}% "
                               f"B:{steering_data["breaking"]:.2f}% "
                               f"SP:{'LEFT' if steering_data['steering_pos'] == 1 else 'RIGHT'} "
                               f"SR:{steering_data["steering_rot"]:.2f}\n"
                               f"BTN_TRI:{'TRUE' if steering_data["btn_triangle"] else 'FALSE'} "
                               f"BTN_CIR:{'TRUE' if steering_data["btn_circle"] else 'FALSE'} "
                               f"BTN_X:{'TRUE' if steering_data["btn_x"] else 'FALSE'} "
                               f"BTN_SQR:{'TRUE' if steering_data["btn_square"] else 'FALSE'} "
                               f"PAD_R:{'TRUE' if steering_data["r_paddleshifter"] else 'FALSE'}"
                               f"PAD_L:{'TRUE' if steering_data["l_paddleshifter"] else 'FALSE'}")

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
