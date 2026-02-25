from robot import Robot
from sensors.lidar import LidarScan
import matplotlib.pyplot as plt
import math
import csv

# -----------------------------------------------------
# Runtime modes & visualization toggles
# -----------------------------------------------------
MODE = "MANUAL"        # MANUAL | AUTO
SHOW_LIDAR = True
SHOW_ODOM = True


# -----------------------------------------------------
# Control commands (shared state)
# -----------------------------------------------------
v = 0.0   # linear velocity [m/s]
w = 0.0   # angular velocity [rad/s]


def on_key(event):
    """Keyboard control & visualization toggles."""
    global v, w, MODE, SHOW_LIDAR, SHOW_ODOM

    # --- visualization toggles ---
    if event.key == 'o':
        SHOW_ODOM = not SHOW_ODOM
        print(f"Odometry visualization: {'ON' if SHOW_ODOM else 'OFF'}")
        return

    if event.key == 'l':
        SHOW_LIDAR = not SHOW_LIDAR
        print(f"LiDAR visualization: {'ON' if SHOW_LIDAR else 'OFF'}")
        return

    # --- mode switching ---
    if event.key == 'm':
        MODE = "MANUAL"
        v = 0.0
        w = 0.0
        print("Switched to MANUAL mode")
        return

    if event.key == 'a':
        MODE = "AUTO"
        print("Switched to AUTO mode")
        return

    # --- manual control ---
    if MODE != "MANUAL":
        return

    if event.key == 'up':
        v += 1.5
    elif event.key == 'down':
        v -= 1.5
    elif event.key == 'left':
        w += 2.0
    elif event.key == 'right':
        w -= 2.0
    elif event.key == ' ':
        v = 0.0
        w = 0.0

    # clamp commands
    v = max(min(v, 6.0), -6.0)
    w = max(min(w, 6.0), -6.0)


if __name__ == "__main__":

    lidar = LidarScan(max_range=4.0)
    robot = Robot()

    plt.close('all')
    fig = plt.figure(num=2)
    fig.canvas.manager.set_window_title("Autonomy Debug View")
    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show(block=False)

    dt = 0.01 

    path=[]
    with open('Autonomous-Rover-Simulation-clean-main\path.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            path.append((float(row['x']), float(row['y'])))

    ld=0.3
    max_v=6.0
    max_w=6.0
    goal_radius=0.4
    pp_idx=0
    stop_d=0.4
    slow_d=0.8
    min_d=0.3
    front_beams=list(range(0,6))+list(range(31,36))
    left_beams=list(range(1,6))
    right_beams=list(range(31,36))


    # -------------------------------------------------
    # Main simulation loop
    # -------------------------------------------------
    while plt.fignum_exists(fig.number):

        # ground truth pose
        real_x, real_y, real_theta = robot.get_ground_truth()
        # odometry estimate
        ideal_x, ideal_y, ideal_theta = robot.get_odometry()
        # LiDAR scan 
        lidar_ranges, lidar_points, lidar_rays, lidar_hits = lidar.get_scan((real_x, real_y, real_theta))

        if MODE == "AUTO":

            # ---------------------------------------------
            # write your autonomous code here!!!!!!!!!!!!!
            # ---------------------------------------------

            # ---------------------------------------------
            # Allowed inputs:
            #   - real_x, real_y, real_theta
            #   - ideal_x, ideal_y, ideal_theta (odometry you have to use for logic)
            #   - lidar_ranges (lidar data you have to use for logic, array of length 36 corresponding to 36 beams)
            #
            # Required outputs:
            #   - v, w (linear and angular velocity commands)

            min_front=min([lidar_ranges[i] for i in front_beams])
            min_left=min([lidar_ranges[i] for i in left_beams])
            min_right=min([lidar_ranges[i] for i in right_beams])
            min_all=min(lidar_ranges)


            end_x, end_y = path[-1]
            if math.hypot(end_x - ideal_x, end_y - ideal_y) < goal_radius:
               v=0.0
               w=0.0
            else:
                goal_x,goal_y=path[-1]
                for i in range(pp_idx,len(path)):
                    dist = math.hypot(path[i][0] - ideal_x, path[i][1] - ideal_y)
                    if dist>=ld:
                        pp_idx=i
                        goal_x,goal_y=path[i]
                        break
            
                dx=goal_x-ideal_x
                dy=goal_y-ideal_y
                ly=-math.sin(ideal_theta)*dx+math.cos(ideal_theta)*dy
                curvature=2*ly/(ld**2)
                v=max_v
                w=curvature*v
                w=max(-max_w,min(max_w,w))

                if min_all<stop_d:
                    v=0.0
                    w=0.0
                elif min_front<min_d:
                    v=-0.2*max_v
                    w=0.0
                elif min_front<slow_d:
                    scale = (min_front - min_d) / (slow_d - min_d)
                    v = max_v * scale
                    avoid_bias = 1.5 * (min_right - min_left) / (min_right + min_left + 0.01)
                    w += avoid_bias
                    w = max(-max_w, min(max_w, w))
                else:   
                    v=max_v


            # ---------------------------------------------
            # don't edit below this line (visualization & robot stepping)
            # ---------------------------------------------
        robot.step(
            lidar_points,
            lidar_rays,
            lidar_hits,
            v,
            w,
            dt,
            show_lidar=SHOW_LIDAR,
            show_odom=SHOW_ODOM
        )

        plt.pause(dt)
