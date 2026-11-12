import evdev
import argparse
import sys
import asyncio
from statistics import median

EV_ABS =3  #3 is the dict key containing absinfo values
ABS_X = 0  #Steering
ABS_Y = 1  #Break
ABS_RZ= 2  #Throttle

STEERING_LEFTMOST   = 0
STEERING_MIDDLE     = 0
STEERING_RIGHTMOST  = 0
BREAK_NOT_APPLIED   = 0
BREAK_FULLY_APPLIED = 0
THROTTLE_NOT_APPLIED= 0
THROTTLE_FULL_BEANS = 0


def get_steering_device(hardware_name:str)-> evdev.InputDevice:
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
    print(f"Detected Steering: {connected_device[0].name}")
    return connected_device[0]  # There must be only one element


def set_device_value_ranges(capabilities):
    """This method sets the min, max values for the steering and pedals."""
    global STEERING_LEFTMOST, STEERING_RIGHTMOST, STEERING_MIDDLE
    global BREAK_NOT_APPLIED, BREAK_FULLY_APPLIED
    global THROTTLE_NOT_APPLIED, THROTTLE_FULL_BEANS

    STEERING_LEFTMOST = capabilities[EV_ABS][ABS_X][1].min  # 1 is the index of the tuple containing absinfo
    STEERING_RIGHTMOST= capabilities[EV_ABS][ABS_X][1].max
    STEERING_MIDDLE= int(median([STEERING_LEFTMOST, STEERING_RIGHTMOST]))

    BREAK_NOT_APPLIED = capabilities[EV_ABS][ABS_Y][1].max
    BREAK_FULLY_APPLIED = capabilities[EV_ABS][ABS_Y][1].min

    THROTTLE_NOT_APPLIED = capabilities[EV_ABS][ABS_RZ][1].max
    THROTTLE_FULL_BEANS = capabilities[EV_ABS][ABS_RZ][1].min
#end def

async def remote_car_ctrl(device):
    async for ev in device.async_read_loop():
        if ev.type == EV_ABS:
            if ev.code == ABS_X:  # Steering event
                if STEERING_LEFTMOST <= ev.value <= STEERING_MIDDLE:  # turning left
                    steering_angle = ((STEERING_MIDDLE - ev.value) / STEERING_MIDDLE) * 100
                    print(f"Steering Angle LEFT: {steering_angle:.2f}%")
                elif STEERING_MIDDLE < ev.value <= STEERING_RIGHTMOST:  # turning right
                    steering_angle = ((ev.value - STEERING_MIDDLE) / STEERING_MIDDLE) * 100
                    print(f"Steering Angle RIGHT: {steering_angle:.2f}%")
                #end if
            #end if
        # end if
#end def()

""" START OF MAIN """
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-n', '--hardware_name',
                           help="Enter a keyword identifying the steering hardware. Example: Thrustmaster",
                           default='Thrustmaster',
                           )
    args = argparser.parse_args()
    print("Starting Steering Control...")
    steering_device = get_steering_device(args.hardware_name)
    dev_capabilities = steering_device.capabilities(verbose=False, absinfo=True)
    set_device_value_ranges(dev_capabilities)
    asyncio.run(remote_car_ctrl(steering_device))
