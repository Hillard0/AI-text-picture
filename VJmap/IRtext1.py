import cv2
import numpy as np
import json
import matplotlib.pyplot as plt


def preprocess_image(image_path):
    # 读取图像
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 二值化处理
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)

    return binary_img


def detect_edges(binary_img):
    # 边缘检测（Canny）
    edges = cv2.Canny(binary_img, 50, 150, apertureSize=3)

    return edges


def detect_lines(edges):
    # 霍夫直线变换
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

    return lines


def extract_line_segments(lines):
    line_segments = []
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                line_segments.append({
                    "start": {"x": int(x1), "y": int(y1)},
                    "end": {"x": int(x2), "y": int(y2)}
                })
    return line_segments


def visualize_lines(image_path, line_segments):
    img = cv2.imread(image_path)
    for segment in line_segments:
        cv2.line(img, (segment["start"]["x"], segment["start"]["y"]), (segment["end"]["x"], segment["end"]["y"]),
                 (0, 255, 0), 2)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


def save_to_json(data, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Coordinates successfully saved to {output_filename}")


def main(image_path, output_filename):
    # 图像预处理
    binary_img = preprocess_image(image_path)

    # 边缘检测
    edges = detect_edges(binary_img)

    # 直线检测
    lines = detect_lines(edges)

    # 提取线段信息
    line_segments = extract_line_segments(lines)

    # 打印线段信息
    for segment in line_segments:
        print(f"Line segment: {segment}")

    # 保存到JSON文件
    save_to_json(line_segments, output_filename)

    # 可视化结果
    visualize_lines(image_path, line_segments)


# 输入图像路径和输出JSON文件路径
image_path = r"C:\Users\Lenovo\Desktop\123.png"
output_filename = r"C:\\Users\\Lenovo\\Desktop\\水闸纵剖面图\\cad解析\\text2.1lotlib.pyplot as plt.json"

# 运行主程序
main(image_path, output_filename)
