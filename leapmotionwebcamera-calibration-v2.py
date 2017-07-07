import numpy as np
import cv2
import sys
import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture



class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "initialized"

    def on_connect(self, controller):
        print "leap motion connected"
        #controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        #controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        #controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

        controller.config.set("Gesture.KeyTap.MinDownVelocity", 5.0)
        controller.config.set("Gesture.KeyTap.HistorySeconds", .3)
        controller.config.set("Gesture.KeyTap.MinDistance", 0.5)
        controller.config.save()

        controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "leap motion disconnected"

    def on_exit(self, controller):
        print "exited"

    def on_frame(self, controller):
        self.frame = controller.frame()

def to_np(v):
    return np.float32([v[0], v[1], v[2]])

def main():
    controller = Leap.Controller()
    controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

    # Initial Intrinsic Camaera Parameters
    # the resolution is 1280x720,
    cm0 = np.float32( [[  1.31446976e+03, 0.00000000e+00, 1.03816814e+03],
 [  0.00000000e+00, 1.31845592e+03, 5.53934350e+02],
 [  0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist0 = np.float32([[-0.10849121,  0.05242051,  0.00223423, -0.01146983, -0.04983505]])


    cm=None
    #test points are 5 * 3
    #test_pos=[(0.1+(1.0*i/4)*0.8,0.1+(1.0*j/2)*0.8) for i in range(5) for j in range(3)]

    #test points are 5 * 5
    test_pos=[(0.1+(1.0*i/4)*0.8,0.1+(1.0*j/4)*0.8) for i in range(5) for j in range(5)]

    result = []
    screen_pos = []

    # opencv related content
    cv2.startWindowThread()
    cap = cv2.VideoCapture(2)
    #ret = cap.set(3,1280);
    #ret = cap.set(4,720);
    #ret = cap.set(3,960);
    #ret = cap.set(4,720);
    ret = cap.set(3,1920);
    ret = cap.set(4,1080);

    idx = 0

    while(True):
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        H, W = img.shape[:2]
        keycode = cv2.waitKey(1) & 0xff
        frame = controller.frame()
        tip = None

        for hand1 in frame.hands:
            index_finger_list = hand1.fingers.finger_type(Finger.TYPE_INDEX)
            index_finger = index_finger_list[0] #since there is only one per hand

        if keycode == ord('q'):
            break;
        elif keycode == ord(' '):
            if tip:
                screen_pos.append((int(test_pos[idx][0]*W), int(test_pos[idx][1]*H)))

                result.append((tip[0], tip[1], tip[2]))
                idx += 1
                if idx >= len(test_pos):
                    idx = 0
        cv2.circle(img, (int(test_pos[idx][0]*W), int(test_pos[idx][1]*H)), 10, (0,0,255) if tip else (255,0,0), -1)

        cv2.imshow('frame', img)

    cv2.destroyWindow('frame')
    cap.release()
    controller.clear_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)


    screen_pos2 = [(W-1-x, y) for (x,y) in screen_pos]

    retval, cm, dist, rvec, tvec = cv2.calibrateCamera(np.float32([result]), \
                                                   np.float32([screen_pos]), (W, H), cm0.copy(), dist0.copy(),\
                                                   flags=cv2.CALIB_USE_INTRINSIC_GUESS)

    np.set_printoptions(threshold='nan')
    np.set_printoptions(suppress = True)

    print retval, rvec, tvec, cm, dist

    controller.clear_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        #controller.remove_listener(listener)
        pass

if __name__ == "__main__":
    main()
