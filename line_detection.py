import cv2
import numpy as np
from pylsd import lsd


def detect_lines(edges):
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=10)
    return lines

def do_lsd(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # Detect line segments
    segments = lsd(img)

    # Visualize the detected line segments
    for segment in segments:
        x1, y1, x2, y2, _ = segment
        start_point = (int(x1), int(y1))
        end_point = (int(x2), int(y2))
        cv2.line(img, start_point, end_point, (255, 0, 0), 2)

    # Show or save the result

    path_list = img_path.split("/")
    file_name = path_list[len(path_list)-1]
    filename_list = file_name.split(".")
    # print(path_list, filename_list)
    save_path = './assets/detected_' + filename_list[len(filename_list)-2] + "_edges." + filename_list[len(filename_list)-1]
    print("***", save_path)
    cv2.imwrite(save_path, img)

    return save_path