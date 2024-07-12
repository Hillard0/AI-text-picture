import ezdxf
import os
import json
import math
from ezdxf.math import area, Vec3

def convert_to_list(coord):
    """Convert Vec3 object or tuple to a list."""
    if isinstance(coord, ezdxf.math.Vec3):
        return [coord.x, coord.y, coord.z]
    elif isinstance(coord, tuple):
        return list(coord[:3])  # Only take the first three elements
    else:
        raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def find_outermost_coordinates(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"The file {filename} does not exist.")

    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for entity in msp:
        f = -1
        if entity.dxftype() in {'POINT', 'LINE', 'LWPOLYLINE', 'SPLINE', 'ARC', 'TEXT', 'MTEXT'}:
            if entity.dxftype() == 'POINT':
                point = convert_to_list(entity.dxf.location)
                min_x = min(min_x, point[0])
                min_y = min(min_y, point[1])
                max_x = max(max_x, point[0])
                max_y = max(max_y, point[1])
                f =1
            elif entity.dxftype() == 'LWPOLYLINE':
                points = [convert_to_list(point) for point in entity.get_points()]
                for point in points:
                    min_x = min(min_x, point[0])
                    min_y = min(min_y, point[1])
                    max_x = max(max_x, point[0])
                    max_y = max(max_y, point[1])
                f =3
            elif entity.dxftype() == 'SPLINE':
                points = [convert_to_list(point) for point in entity.control_points]
                for point in points:
                    min_x = min(min_x, point[0])
                    min_y = min(min_y, point[1])
                    max_x = max(max_x, point[0])
                    max_y = max(max_y, point[1])
                f =4
        if  min_x < 1e-10 :
            min_x = 0
        if min_y <  1e-10 :
            min_y = 0

    return (min_x, min_y), (max_x, max_y)

def is_inside_bbox(x, y, bbox):
    """Check if a coordinate is inside the bounding box."""
    min_x, min_y, max_x, max_y = bbox
    return min_x <= x <= max_x and min_y <= y <= max_y

def calculate_distance(point1, point2):
    """Calculate the distance between two points."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)

def extract_linear_dimensions(msp, bbox):
    linear_dimensions = []

    for entity in msp.query('DIMENSION'):
        if entity.dimtype in {0, 1}:  # 线性标注类型的dimtype为0或1
            try:
                text = entity.dxf.get('text', None)
                if text is None or not text.strip().isdigit() or text == '<>':
                    measurement = round(entity.get_measurement(), 0)
                else:
                    measurement = text

                start_point = entity.dxf.get('defpoint2')
                end_point = entity.dxf.get('defpoint3')
                dimension_line_position = entity.dxf.get('defpoint')
                if abs(start_point[0] - end_point[0]) <= abs(start_point[1] - end_point[1]):
                    x = dimension_line_position.x
                    y = (start_point[1] + end_point[1]) // 2
                else:
                    y = dimension_line_position.y
                    x = (start_point[0] + end_point[0]) // 2

                if is_inside_bbox(x, y, bbox):
                    if start_point and end_point and dimension_line_position:
                        linear_info = {
                            "type": "Linear Dimension",
                            "text": str(measurement),
                            "measurement": measurement,
                            "start_point": {
                                "x": start_point.x,
                                "y": start_point.y,
                                "z": start_point.z,
                            },
                            "end_point": {
                                "x": end_point.x,
                                "y": end_point.y,
                                "z": end_point.z,
                            },
                            "dimension_line_position": {
                                "x": dimension_line_position.x,
                                "y": dimension_line_position.y,
                                "z": dimension_line_position.z,
                            },
                        }
                        linear_dimensions.append(linear_info)
            except AttributeError as e:
                print(f"AttributeError: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    return linear_dimensions

def find_linear_dimension_in_moving_bbox(dxf_file_path, initial_bbox, step_size):
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()

    bbox = initial_bbox
    linear_dimensions = []
    while not linear_dimensions:
        linear_dimensions = extract_linear_dimensions(msp, bbox)

        if linear_dimensions:
            text_values = [dim['text'] for dim in linear_dimensions]
            print(f"Linear dimension texts found within bbox: {bbox}")
            print(f"Text values: {text_values}")
            break
        else:
            print(f"No linear dimension found within bbox: {bbox}. Moving bbox.")
            # 向上移动
            bbox_up = (bbox[0], bbox[1] - step_size, bbox[2], bbox[3] - step_size)
            linear_dimensions_up = extract_linear_dimensions(msp, bbox_up)

            if linear_dimensions_up:
                text_values = [dim['text'] for dim in linear_dimensions_up]
                print(f"Linear dimension texts found within bbox: {bbox_up}")
                print(f"Text values: {text_values}")
                break

            # 向下移动
            bbox_down = (bbox[0], bbox[1] + step_size, bbox[2], bbox[3] + step_size)
            linear_dimensions_down = extract_linear_dimensions(msp, bbox_down)

            if linear_dimensions_down:
                text_values = [dim['text'] for dim in linear_dimensions_down]
                print(f"Linear dimension texts found within bbox: {bbox_down}")
                print(f"Text values: {text_values}")
                break

            bbox = bbox_down  # 更新bbox为向下移动后的bbox

# Define the initial bounding box coordinates
xmin, ymin, xmax, ymax = map(int, input("Enter xmin, ymin, xmax, ymax: ").split())

initial_bbox = (xmin, ymin, xmax, ymax)

dxf_file_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\9#口门水工施工图.dxf"

# Find linear dimension within moving bounding box and print the text values
find_linear_dimension_in_moving_bbox(dxf_file_path, initial_bbox, ymax - ymin)

lower_left, upper_right = find_outermost_coordinates(dxf_file_path)
print(f"Lower Left Corner: {lower_left}")
print(f"Upper Right Corner: {upper_right}")
