import serial
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['keymap.save'] = ''       
plt.rcParams['keymap.fullscreen'] = '' 
plt.rcParams['keymap.grid'] = ''       


# 1. SETUP THÔNG SỐ KHỞI TẠO

Kp_line = 7.0
Kd_line = 45.0
target_base_speed = 40
max_manual_speed = 33

current_mode = "MODE 0: DUNG XE"
motor_L, motor_R = 0, 0
error_line = 0.0

time_data = []
error_data = []

start_time = None


# 2. QUẢN LÝ KẾT NỐI BLUETOOTH

SERIAL_PORT = '/dev/rfcomm0' 
BAUD_RATE = 9600

ser = None
is_connected = False

def sync_state_to_robot():
    if not (ser and ser.is_open): return
    
    diff_kp = int((Kp_line - 7.0) / 0.5)
    diff_kd = int((Kd_line - 45.0) / 1.0)
    diff_base = int(target_base_speed - 40)
    diff_man = int(max_manual_speed - 33)

    cmd_sequence = ""
    if diff_kp > 0: cmd_sequence += 'I' * diff_kp
    elif diff_kp < 0: cmd_sequence += 'K' * abs(diff_kp)
    if diff_kd > 0: cmd_sequence += 'O' * diff_kd
    elif diff_kd < 0: cmd_sequence += 'L' * abs(diff_kd)
    if diff_base > 0: cmd_sequence += 'T' * diff_base
    elif diff_base < 0: cmd_sequence += 'G' * abs(diff_base)
    if diff_man > 0: cmd_sequence += 'Y' * diff_man
    elif diff_man < 0: cmd_sequence += 'H' * abs(diff_man)

    if "MODE 1" in current_mode: cmd_sequence += '1'
    elif "MODE 2" in current_mode: cmd_sequence += '2'
    else: cmd_sequence += '0'

    if cmd_sequence:
        try:
            for char in cmd_sequence:
                ser.write(char.encode('utf-8'))
                time.sleep(0.01)
            print(f"-> Da dong bo xong! (Lenh: {cmd_sequence})")
        except: pass
    else:
        print("-> Da dong bo! (Thong so goc)")
        
    if 'txt_status' in globals():
        txt_status.set_text("Trang thai: DA KET NOI (Dong bo hoan tat)")
        txt_status.set_color('#00ff00') 
        fig.canvas.draw_idle()

def connect_bluetooth():
    global ser, is_connected, start_time
    if ser and ser.is_open: ser.close()
        
    try:
        print(f"Dang ket noi toi {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        is_connected = True
        start_time = None 
        time_data.clear(); error_data.clear()
        
        if 'txt_status' in globals():
            txt_status.set_text("Trang thai: DA KET NOI (Dang dong bo...)")
            txt_status.set_color('#00ff00')
            fig.canvas.draw_idle()
            
        sync_state_to_robot()

    except Exception:
        is_connected = False
        print("Loi ket noi COM. Kiem tra lai ket noi hoac service auto_rfcomm.")
        if 'txt_status' in globals():
            txt_status.set_text("Trang thai: LOI KET NOI (Bam 'R' de thu lai)")
            txt_status.set_color('#ff3333') 
            fig.canvas.draw_idle()

def handle_disconnect():
    global is_connected, ser
    if is_connected: 
        print("-> Canh bao: Mat ket noi voi xe!")
    is_connected = False
    if ser:
        try: ser.close()
        except: pass
    if 'txt_status' in globals():
        txt_status.set_text("Trang thai: DA ROT MANG (Bam 'R' de ket noi)")
        txt_status.set_color('#ff3333')
        txt_motor.set_text("Xung Trai: [ -- ]  |  Xung Phai: [ -- ]  |  Sai so: [ -- ]")
        fig.canvas.draw_idle()


# 3. GIAO DIỆN BỐ CỤC

BG_COLOR = '#121212'        
PANEL_COLOR = '#1e1e1e'     
TEXT_COLOR = '#e0e0e0'      
ACCENT_COLOR = '#00d2ff'    
BORDER_COLOR = '#333333'    

fig = plt.figure(figsize=(14, 8))
fig.canvas.manager.set_window_title("Tram Telemetry & Live-Tuning PID")
fig.patch.set_facecolor(BG_COLOR) 

gs = gridspec.GridSpec(2, 1, height_ratios=[1.2, 1.8], hspace=0.2)

# --- BẢNG ĐIỀU KHIỂN ---
ax_hud = fig.add_subplot(gs[0])
ax_hud.set_facecolor(BG_COLOR)
ax_hud.axis('off')

ax_hud.text(0.45, 0.95, "HE THONG DIEU KHIEN XE TU HANH", fontsize=18, ha='center', weight='bold', color=ACCENT_COLOR)
txt_status = ax_hud.text(0.45, 0.78, "Trang thai: DANG KHOI TAO...", fontsize=11, ha='center', color='#ffcc00', weight='bold')
txt_mode = ax_hud.text(0.45, 0.50, current_mode, fontsize=16, ha='center', color='#ff4444', weight='bold', 
                       bbox=dict(facecolor='#2a0000', edgecolor='#ff4444', boxstyle='round,pad=0.4'))
txt_motor = ax_hud.text(0.45, 0.15, f"Xung Trai: [ {motor_L} ]  |  Xung Phai: [ {motor_R} ]  |  Sai so: [ {error_line} ]", 
                        fontsize=12, ha='center', color='#00ffcc', weight='bold',
                        bbox=dict(facecolor='#002222', edgecolor='#00ffcc', boxstyle='round,pad=0.4'))

bbox_props = dict(boxstyle="round,pad=0.4", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, alpha=0.9)
txt_kp   = ax_hud.text(0.01, 0.85, f"Kp_line : {Kp_line:.1f}", fontsize=11, weight='bold', color=TEXT_COLOR, bbox=bbox_props, ha='left')
txt_kd   = ax_hud.text(0.01, 0.60, f"Kd_line : {Kd_line:.1f}", fontsize=11, weight='bold', color=TEXT_COLOR, bbox=bbox_props, ha='left')
txt_base = ax_hud.text(0.01, 0.35, f"Base Spd : {target_base_speed}", fontsize=11, weight='bold', color=TEXT_COLOR, bbox=bbox_props, ha='left')
txt_man  = ax_hud.text(0.01, 0.10, f"Man Spd  : {max_manual_speed}", fontsize=11, weight='bold', color=TEXT_COLOR, bbox=bbox_props, ha='left')

help_text = (
    "[ 1 ]: Do Line | [ 2 ]: Lai Tay | [ 0 ]: Dung\n"
    "[ R ]: Ket Noi | [ C ]: XOA DO THI\n"
    "-------------------------------------------\n"
    "[ I/K ]: ± Kp  | [ O/L ]: ± Kd\n"
    "[ T/G ]: ± Base| [ Y/H ]: ± Man Spd\n"
    "[ W-A-S-D ]: Lai xe"
)
ax_hud.text(0.99, 0.90, help_text, fontsize=10, ha='right', va='top', linespacing=1.6, family='monospace', color='#aaaaaa',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=PANEL_COLOR, edgecolor='#555555', alpha=0.9))

# --- ĐỒ THỊ SAI SỐ ---
ax_err = fig.add_subplot(gs[1])
ax_err.set_facecolor(PANEL_COLOR)
for spine in ax_err.spines.values(): spine.set_color(BORDER_COLOR)
ax_err.tick_params(colors='#888888')
ax_err.yaxis.label.set_color(TEXT_COLOR)
ax_err.xaxis.label.set_color(TEXT_COLOR)
ax_err.set_title("Do thi Sai So", fontsize=13, weight='bold', color=TEXT_COLOR)
ax_err.set_ylabel("Error (-2 to +2)", fontsize=11)
ax_err.set_xlabel("Thoi gian (giay)", fontsize=11)
ax_err.grid(True, linestyle='--', color='#333333')
ax_err.set_ylim(-2.5, 2.5) 

line_err, = ax_err.plot([], [], color='#ffcc00', linewidth=2.0, label="Current Error")
ax_err.axhline(0, color='#00ff00', linestyle=':', linewidth=1.5, alpha=0.7) 

connect_bluetooth()


# 4. XỬ LÝ BÀN PHÍM

current_key = None
last_key_time = 0
pending_stop = False

def send_cmd(char, desc=""):
    global is_connected, ser
    if is_connected and ser and ser.is_open:
        try: 
            ser.write(char.encode('utf-8'))
            if desc: 
                print(f"-> {desc}")
        except: 
            handle_disconnect()

def on_key_press(event):
    global current_key, last_key_time, pending_stop, current_mode
    global Kp_line, Kd_line, target_base_speed, max_manual_speed
    global start_time

    if event.key is None: return
    key = event.key.upper()
    last_key_time = time.time()
    pending_stop = False

    if key != current_key:
        current_key = key
        
        if key == 'R': connect_bluetooth(); return
        
        elif key == 'C': 
            time_data.clear()
            error_data.clear()
            start_time = None
            ax_err.set_xlim(0, 5) 
            fig.canvas.draw_idle()
            print("-> Da xoa toan bo do thi!")
            return
        
        elif key == '0':
            current_mode = "MODE 0: DUNG XE"
            txt_mode.set_text(current_mode); txt_mode.set_color('#ff4444')
            txt_mode.set_bbox(dict(facecolor='#2a0000', edgecolor='#ff4444', boxstyle='round,pad=0.4'))
            send_cmd('0', current_mode)
        elif key == '1':
            current_mode = "MODE 1: AUTO DO LINE"
            txt_mode.set_text(current_mode); txt_mode.set_color('#00ff00')
            txt_mode.set_bbox(dict(facecolor='#002a00', edgecolor='#00ff00', boxstyle='round,pad=0.4'))
            send_cmd('1', current_mode)
        elif key == '2':
            current_mode = "MODE 2: MANUAL WASD"
            txt_mode.set_text(current_mode); txt_mode.set_color('#00d2ff')
            txt_mode.set_bbox(dict(facecolor='#001a2a', edgecolor='#00d2ff', boxstyle='round,pad=0.4'))
            send_cmd('2', current_mode)
        elif key in ['W', 'A', 'S', 'D']: 
            send_cmd(key, f"Lai xe: {key}")

        elif key == 'I': Kp_line += 0.5; send_cmd('I')
        elif key == 'K': Kp_line -= 0.5; send_cmd('K')
        elif key == 'O': Kd_line += 1.0; send_cmd('O')
        elif key == 'L': Kd_line -= 1.0; send_cmd('L')
        elif key == 'T': target_base_speed += 1; send_cmd('T')
        elif key == 'G': target_base_speed -= 1; send_cmd('G')
        elif key == 'Y': max_manual_speed += 1; send_cmd('Y')
        elif key == 'H': max_manual_speed -= 1; send_cmd('H')

        txt_kp.set_text(f"Kp_line : {Kp_line:.1f}")
        txt_kd.set_text(f"Kd_line : {Kd_line:.1f}")
        txt_base.set_text(f"Base Spd : {target_base_speed}")
        txt_man.set_text(f"Man Spd  : {max_manual_speed}")
        fig.canvas.draw_idle()

def on_key_release(event):
    global pending_stop, current_key
    if event.key is None: return
    key = event.key.upper()
    if key == current_key:
        if key in ['W', 'A', 'S', 'D']: pending_stop = True 
        else: current_key = None  

fig.canvas.mpl_connect('key_press_event', on_key_press)
fig.canvas.mpl_connect('key_release_event', on_key_release)


# 5. VÒNG LẶP ĐỌC DATA & VẼ ĐỒ THỊ

def update_gui(frame):
    global current_key, pending_stop, motor_L, motor_R, error_line, is_connected, start_time

    if pending_stop and (time.time() - last_key_time > 0.1):
        send_cmd('X', "Phanh (X)")
        current_key = None
        pending_stop = False

    if is_connected and ser and ser.is_open:
        try:
            raw_line = b''
            while ser.in_waiting > 0:
                raw_line = ser.readline()
            
            if raw_line:
                line_data = raw_line.decode('utf-8', errors='ignore').strip()
                data = line_data.split(',')

                if len(data) == 6:
                    try:
                        timestamp_ms = int(data[0])
                        error_val = float(data[5])
                        
                        motor_L = int(data[2])
                        motor_R = int(data[4])
                        error_line = error_val
                        
                        txt_motor.set_text(f"Xung Trai: [ {motor_L} ]  |  Xung Phai: [ {motor_R} ]  |  Sai so: [ {error_line} ]")

                        current_t = timestamp_ms / 1000.0 
                        if start_time is None: start_time = current_t
                        rel_time = current_t - start_time

                        time_data.append(rel_time)
                        error_data.append(error_val)

                        line_err.set_data(time_data, error_data)

                        ax_err.set_xlim(0, max(5.0, rel_time + 0.5))

                    except ValueError: pass
        except serial.SerialException:
            handle_disconnect()
        except Exception: pass

    return line_err,

ani = FuncAnimation(fig, update_gui, interval=50, blit=False, save_count=150)
plt.show()

if ser and ser.is_open: ser.close()
