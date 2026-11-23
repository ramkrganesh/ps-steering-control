import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from steering_control import SteeringControl
from json import dumps as json_dumps

class SteeringDataPublisher(Node):
    def __init__(self):
        super().__init__("steering_data_publisher")
        self.steeringctrl = SteeringControl()
        self.st_publisher = self.create_publisher(String, 'steering_data', 5)
        timer_period = 0.250  # seconds
        self.timer = self.create_timer(timer_period, self.publish_steering_values)


    def publish_steering_values(self):
        st_data = String()
        self.steeringctrl.do_steering_events_detection()
        steering_data = self.steeringctrl.get_steering_data()
        st_data.data = json_dumps(steering_data)
        self.st_publisher.publish(st_data)
        self.get_logger().info(f"Sent Steering Data- "
                               f"T:{steering_data["throttle"]:.2f}% "
                               f"B:{steering_data["breaking"]:.2f}% "
                               f"SP:{'LEFT' if steering_data['steering_pos']==1 else 'RIGHT'} "
                               f"SR:{steering_data["steering_rot"]:.2f}\n"
                               f"BTN_TRI:{'TRUE' if steering_data["btn_triangle"] else 'FALSE'} "
                               f"BTN_CIR:{'TRUE' if steering_data["btn_circle"] else 'FALSE'} "
                               f"BTN_X:{'TRUE' if steering_data["btn_x"] else 'FALSE'} "
                               f"BTN_SQR:{'TRUE' if steering_data["btn_square"] else 'FALSE'} "
                               f"PAD_R:{'TRUE' if steering_data["r_paddleshifter"] else 'FALSE'}"
                               f"PAD_L:{'TRUE' if steering_data["l_paddleshifter"] else 'FALSE'}")

if __name__ == '__main__':
    print("Starting ROS2 Steering Data Publisher Node...")
    rclpy.init()
    sdp = SteeringDataPublisher()
    try:
        rclpy.spin(sdp)
    except KeyboardInterrupt as e:
        print(f"{e}")
    finally:
        if rclpy.ok():
            sdp.destroy_node()
            rclpy.shutdown()