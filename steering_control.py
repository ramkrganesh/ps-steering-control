import evdev
import argparse
import sys
import asyncio
from statistics import median
from dataclasses import dataclass, field

#Todo : Create a class and have the event types and code as class variables.
# Event Types
EV_KEY =1  # Event Type for buttons
EV_ABS =3  # Event Type for steering
EV_MSC =4  # Padde shifters

# Event Codes
ABS_X = 0  #Steering
ABS_Y = 1  #Break
ABS_RZ= 5  #Throttle
BTN_THUMB2  = 290 # Triangle
BTN_TOP2    = 292 # Circle
BTN_TOP     = 291 # Square
BTN_PINKIE  = 293 # X
BTN_THUMB   = 289 # Right paddle shifter
BTN_TRIGGER = 288 # Left paddle shifter

STEERING_LEFTMOST   = 0
STEERING_MIDDLE     = 0
STEERING_RIGHTMOST  = 0
BREAK_NOT_APPLIED   = 0
BREAK_FULLY_APPLIED = 0
THROTTLE_NOT_APPLIED= 0
THROTTLE_FULL_BEANS = 0

# variables denoting steering position
POS_CENTRE=0  # unused at the moment
POS_LEFT = 1
POS_RIGHT= 2

@dataclass
class SteeringControl:
    hardware_name: str = 'Thrustmaster'
    steering_device: evdev.InputDevice = field(init=False)
    dev_capabilities: dict = field(init=False)
    steering_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.steering_device = self.get_steering_device(self.hardware_name)
        self.dev_capabilities = self.steering_device.capabilities(verbose=False, absinfo=True)
        self.set_device_value_ranges(self.dev_capabilities)
        self.reset_steering_data()
    #end post_init

    def get_steering_device(self, hardware_name:str='Thrustmaster')-> evdev.InputDevice:
        """This method gets the hardware name as input and returns a 'class' object.
        The returned object contains details about the steering hardware."""
        connected_device = []
        all_dev_paths = evdev.list_devices()
        for dev_path in all_dev_paths:
            device = evdev.InputDevice(dev_path)
            if hardware_name.lower() not in device.name.lower():
                continue
            connected_device.append(device)
        #end for
        if len(connected_device) == 0:
            raise Exception(f"Unable to find a matching input device named {hardware_name}")
        elif len(connected_device) > 1:
            raise Exception(f"More than one connected input has the name {hardware_name}."
                            f"Try again with a suitable match.")
        #end if
        #print(f"Detected Steering: {connected_device[0].name}")
        return connected_device[0]  # There must be only one element


    def set_device_value_ranges(self, capabilities):
        """This method sets the min, max values for the steering and pedals."""
        global STEERING_LEFTMOST, STEERING_RIGHTMOST, STEERING_MIDDLE
        global BREAK_NOT_APPLIED, BREAK_FULLY_APPLIED
        global THROTTLE_NOT_APPLIED, THROTTLE_FULL_BEANS

        CAPA_ABS_RZ =  2 # in capabilities dict, ABS_RZ is at index 2
        STEERING_LEFTMOST = capabilities[EV_ABS][ABS_X][1].min  # 1 is the index of the tuple containing absinfo
        STEERING_RIGHTMOST= capabilities[EV_ABS][ABS_X][1].max
        STEERING_MIDDLE= int(median([STEERING_LEFTMOST, STEERING_RIGHTMOST]))

        BREAK_NOT_APPLIED = capabilities[EV_ABS][ABS_Y][1].max
        BREAK_FULLY_APPLIED = capabilities[EV_ABS][ABS_Y][1].min

        THROTTLE_NOT_APPLIED = capabilities[EV_ABS][CAPA_ABS_RZ][1].max
        THROTTLE_FULL_BEANS = capabilities[EV_ABS][CAPA_ABS_RZ][1].min
    #end def

    def reset_steering_data(self):

        self.steering_data["btn_triangle"] = False
        self.steering_data["btn_circle"] = False
        self.steering_data["btn_x"] = False
        self.steering_data["btn_square"] = False
        self.steering_data["r_paddleshifter"] = False
        self.steering_data["l_paddleshifter"] = False
    #end def

    def do_steering_events_detection(self):
        self.reset_steering_data()
        try:
            for ev in self.steering_device.read():  # read() returns an iterator of InputEvent instances
                if ev.type == EV_ABS:
                    if ev.code == ABS_X:  # Steering event
                        steering_angle = 0
                        if STEERING_LEFTMOST <= ev.value <= STEERING_MIDDLE:  # turning left
                            steering_angle = ((STEERING_MIDDLE - ev.value) / STEERING_MIDDLE) * 100
                            #print(f"Steering Angle LEFT: {steering_angle:.2f}%")
                            self.steering_data["steering_pos"] = POS_LEFT
                        elif STEERING_MIDDLE < ev.value <= STEERING_RIGHTMOST:  # turning right
                            steering_angle = ((ev.value - STEERING_MIDDLE) / STEERING_MIDDLE) * 100
                            #print(f"Steering Angle RIGHT: {steering_angle:.2f}%")
                            self.steering_data["steering_pos"] = POS_RIGHT
                        #end if
                        self.steering_data["steering_rot"] = steering_angle
                    elif ev.code == ABS_RZ:
                        throttle = ((THROTTLE_NOT_APPLIED - ev.value) / THROTTLE_NOT_APPLIED) * 100
                        #print(f"Throttle : {throttle:.2f}%")
                        self.steering_data["throttle"] = throttle
                    elif ev.code == ABS_Y:
                        breaking = ((BREAK_NOT_APPLIED - ev.value) / BREAK_NOT_APPLIED) * 100
                        #print(f"Breaking : {breaking:.2f}%")
                        self.steering_data["breaking"] = breaking
                    #end if
                elif ev.type == EV_KEY:
                    if ev.code == BTN_THUMB2:  # triange
                        if ev.value == 1:
                            #print(f"Triangle Button-press event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        else:
                            #print(f"Triangle Button released.")
                            self.steering_data["btn_triangle"] = True
                    elif ev.code == BTN_TOP2:  # circle
                        if ev.value == 1:
                            #print(f"Circle Button-press event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        elif ev.value == 0:
                            #print(f"Circle Button released.")
                            self.steering_data["btn_circle"] = True
                    elif ev.code == BTN_TOP:  # square
                        if ev.value == 1:
                            #print(f"Square Button-press event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        elif ev.value == 0:
                            #print(f"Square Button released.")
                            self.steering_data["btn_square"] = True
                    elif ev.code == BTN_PINKIE:
                        if ev.value == 1:
                            #print(f"X Button-press event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        elif ev.value == 0:
                            #print(f"X Button released.")
                            self.steering_data["btn_x"] = True
                    elif ev.code == BTN_THUMB:  # right paddle shifter
                        if ev.value == 1:
                            #print(f"Right Paddle-Shifter event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        elif ev.value == 0:  # left paddle shifter
                            #print(f"Right Padde-Shifter released")
                            self.steering_data["r_paddleshifter"] = True
                    elif ev.code == BTN_TRIGGER:
                        if ev.value == 1:
                            #print(f"Left Paddle-Shifter event Type-{ev.type}:Code-{ev.code} detected.")
                            pass
                        elif ev.value == 0:  # left paddle shifter
                            #print(f"Left Paddle-Shifter released")
                            self.steering_data["l_paddleshifter"] = True
                    #end if
                # end if
            #end for
        except BlockingIOError as e:
            #print("No steering events at the moment.")
            pass
        #end try
    #end def()

    def get_steering_data(self):
        """This method returns previously stored steering position, throttle, breaks...etc values"""
        return self.steering_data
#end class

""" START OF MAIN """
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-n', '--hardware_name',
                           help="Enter a keyword identifying the steering hardware. Example: Thrustmaster",
                           default='Thrustmaster',
                           )
    args = argparser.parse_args()
    #print("Starting Steering Control...")
    steering_ctrl = SteeringControl(hardware_name=args.hardware_name)
    import pprint
    import time
    while True:
        steering_ctrl.do_steering_events_detection()
        steer_data = steering_ctrl.get_steering_data()
        #pprint.pprint(steer_data["throttle"])
        time.sleep(0.500)