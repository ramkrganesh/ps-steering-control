import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from steering_control import SteeringControl

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
        st_data.data = str(steering_data["r_paddleshifter"])
        self.st_publisher.publish(st_data)
        self.get_logger().info(f"Sent Throttle: {st_data.data}")

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