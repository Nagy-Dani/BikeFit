from cv2_enumerate_cameras import enumerate_cameras

for c_inf in enumerate_cameras():
    print(f'Incdex: {c_inf}, Name: {c_inf.name}')