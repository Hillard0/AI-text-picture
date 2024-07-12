import ezdxf
import os
import json
import math
import numpy as np
from ezdxf.math import area, Vec3


dxf_file_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\text0710.dxf"
output_json_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\text3.5.json"

def get_dimension_scale(doc, entity):
    """获取DIMENSION实体的比例因子"""
    # 获取DIMENSION实体的dimlfac属性
    if hasattr(entity.dxf, 'dimlfac'):
        return entity.dxf.dimlfac
    # 如果dimlfac属性不存在，尝试从标注样式中获取
    dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
    if dim_style:
        return dim_style.dxf.dimlfac
    # 如果都不存在，返回默认比例因子1
    return 1.0



def convert_to_list1(coord):
    """Convert Vec3 object or tuple to a list."""
    if isinstance(coord, ezdxf.math.Vec3):
        return [coord.x, coord.y, coord.z]
    elif isinstance(coord, tuple):
        return list(coord[:3])  # Only take the first three elements
    else:
        raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def find_bounding_box(filename):
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for entity in msp:
        if entity.dxftype() in {'POINT', 'LINE', 'LWPOLYLINE', 'SPLINE', 'ARC', 'TEXT', 'MTEXT'}:
            if entity.dxftype() == 'POINT':
                point = convert_to_list1(entity.dxf.location)
                min_x = min(min_x, point[0])
                min_y = min(min_y, point[1])
                max_x = max(max_x, point[0])
                max_y = max(max_y, point[1])
            elif entity.dxftype() == 'LINE':
                start = convert_to_list1(entity.dxf.start)
                end = convert_to_list1(entity.dxf.end)
                min_x = min(min_x, start[0], end[0])
                min_y = min(min_y, start[1], end[1])
                max_x = max(max_x, start[0], end[0])
                max_y = max(max_y, start[1], end[1])
            elif entity.dxftype() == 'LWPOLYLINE':
                points = [convert_to_list1(point) for point in entity.get_points()]
                for point in points:
                    min_x = min(min_x, point[0])
                    min_y = min(min_y, point[1])
                    max_x = max(max_x, point[0])
                    max_y = max(max_y, point[1])
        if min_x < 1e-10:
            min_x = 0
        if min_y < 1e-10:
            min_y = 0

    return (min_x, min_y), (max_x, max_y)


def convert_to_list(coord):
    """Convert Vec3 object, tuple, or numpy array to a list."""
    if isinstance(coord, ezdxf.math.Vec3):
        return [coord.x, coord.y, coord.z]
    elif isinstance(coord, tuple) or isinstance(coord, np.ndarray):
        return list(coord[:3])  # Only take the first three elements
    else:
        raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def is_inside_bbox(x, y, bbox):
    """Check if a coordinate is inside the bounding box."""
    min_x, min_y, max_x, max_y = bbox
    return min_x <= x <= max_x and min_y <= y <= max_y

def calculate_lwpolyline_area(points):
    """Calculate the area of a closed LWPOLYLINE given its points."""
    points_2d = [(point[0], point[1]) for point in points]
    return abs(area(points_2d))

def calculate_distance(point1, point2):
    """Calculate the distance between two points."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)

def calculate_lwpolyline_length(points):
    """Calculate the total length of an LWPOLYLINE given its points."""
    length = 0
    num_points = len(points)
    for i in range(num_points - 1):
        length += calculate_distance(points[i], points[i + 1])
    if points[0] == points[-1]:  # If polyline is closed
        length += calculate_distance(points[-1], points[0])
    return length

def extract_coordinates_in_bbox(filename, bbox):
    coordinates = {
        "points": [],
        "lines": [],
        "lwpolylines": [],
        "splines": [],
        "arcs": [],
        "texts": [],
        "mtexts": [],
        "linear_dimensions": []
    }

    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()

        for entity in msp:
            if entity.dxftype() == 'POINT':
                point_coord = convert_to_list(entity.dxf.location)
                if is_inside_bbox(point_coord[0], point_coord[1], bbox):
                    coordinates["points"].append(point_coord)
            elif entity.dxftype() == 'LINE':
                start_coord = convert_to_list(entity.dxf.start)
                end_coord = convert_to_list(entity.dxf.end)
                if is_inside_bbox(start_coord[0], start_coord[1], bbox) or is_inside_bbox(end_coord[0], end_coord[1], bbox):
                    line_coords = {
                        "start": start_coord,
                        "end": end_coord,
                        "length": calculate_distance(start_coord, end_coord)
                    }
                    coordinates["lines"].append(line_coords)
            elif entity.dxftype() == 'LWPOLYLINE':
                lwpolyline_coords = [convert_to_list(point) for point in entity.get_points()]
                is_closed = entity.is_closed
                if any(is_inside_bbox(point[0], point[1], bbox) for point in lwpolyline_coords):
                    lwpolyline_info = {
                        "points": lwpolyline_coords,
                        "is_closed": is_closed,
                        "area": calculate_lwpolyline_area(lwpolyline_coords) if is_closed else None,
                        "length": calculate_lwpolyline_length(lwpolyline_coords)
                    }
                    coordinates["lwpolylines"].append(lwpolyline_info)
            elif entity.dxftype() == 'SPLINE':
                spline_coords = [convert_to_list(point) for point in entity.control_points]
                if any(is_inside_bbox(point[0], point[1], bbox) for point in spline_coords):
                    spline_length = sum(calculate_distance(spline_coords[i], spline_coords[i + 1]) for i in range(len(spline_coords) - 1))
                    coordinates["splines"].append({
                        "points": spline_coords,
                        "length": spline_length
                    })
            elif entity.dxftype() == 'ARC':
                center = convert_to_list(entity.dxf.center)
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                arc_length = radius * (abs(end_angle - start_angle) * (3.141592653589793 / 180))
                arc_info = {
                    "center": center,
                    "radius": radius,
                    "start_angle": start_angle,
                    "end_angle": end_angle,
                    "length": arc_length
                }
                if is_inside_bbox(center[0], center[1], bbox):
                    coordinates["arcs"].append(arc_info)
            elif entity.dxftype() == 'TEXT':
                text_location = convert_to_list(entity.dxf.insert)
                if is_inside_bbox(text_location[0], text_location[1], bbox):
                    text_info = {
                        "text": entity.dxf.text,
                        "location": text_location,
                        "height": entity.dxf.height
                    }
                    coordinates["texts"].append(text_info)
            elif entity.dxftype() == 'MTEXT':
                mtext_location = convert_to_list(entity.dxf.insert)
                if is_inside_bbox(mtext_location[0], mtext_location[1], bbox):
                    mtext_info = {
                        "text": entity.text,
                        "location": mtext_location,
                        "height": entity.dxf.char_height
                    }
                    coordinates["mtexts"].append(mtext_info)

        return coordinates
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        return None
    except ezdxf.DXFStructureError as dxf_error:
        print(f"DXFStructureError: {dxf_error}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def extract_linear_dimensions(msp, bbox):
    linear_dimensions = []
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()
    for entity in msp.query('DIMENSION'):
        if entity.dimtype in {0, 1}:  # 线性标注类型的dimtype为0或1
            # 获取标注比例因子
            dim_scale = get_dimension_scale(doc, entity)
            try:
                text = entity.dxf.get('text', None)

                #print(text)
                if text is None or not text.strip().isdigit() or text == '<>':
                    measurement = round(entity.get_measurement(), 2)
                else:
                    measurement = text
                measurement = measurement * dim_scale
                measurement = round(measurement, 0)
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
                    # print(x , y )
                    # print(text)
                    # print(measurement)
                    print(f"测量长度为 {measurement} ,比例因子为{dim_scale}")
                    if start_point and end_point and dimension_line_position:
                        linear_info = {
                            "type": "Linear Dimension",
                            "text": int(measurement),
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

def save_to_json(data, output_filename):
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Coordinates successfully saved to {output_filename}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

# Define the initial bounding box coordinates
xmin, ymin, xmax, ymax = map(int, input("Enter xmin, ymin, xmax, ymax: ").split())
initial_bbox = (xmin, ymin, xmax, ymax)


coords = extract_coordinates_in_bbox(dxf_file_path, initial_bbox)

def find_linear_dimension_in_moving_bbox(dxf_file_path, initial_bbox, output_json_path, step_size, coords):
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()
    c = 0
    bbox = initial_bbox
    linear_dimensions = []
    direction = 'up'
    uxmin, uymin, uxmax, uymax = initial_bbox
    dxmin, dymin, dxmax, dymax = initial_bbox

    while not linear_dimensions:
        linear_dimensions = extract_linear_dimensions(msp, bbox)
        c += 1
        if linear_dimensions:
            coords["linear_dimensions"] = linear_dimensions
            save_to_json(coords, output_json_path)
            print(f"Linear dimension found within bbox: {bbox}")
            break
        else:
            print(f"No linear dimension found within bbox: {bbox}. Moving bbox.")
            if direction == 'up':
                bbox = (uxmin, uymin - step_size, uxmax, uymax - step_size)
                uymin -= step_size
                uymax -= step_size
                direction = 'down'
            else:
                bbox = (dxmin, dymin + step_size, dxmax, dymax + step_size)
                dymin += step_size
                dymax += step_size
                direction = 'up'
        if c > 1000:
            break

# Find linear dimension within moving bounding box and save to JSON
if coords is not None:
    find_linear_dimension_in_moving_bbox(dxf_file_path, initial_bbox, output_json_path, step_size=ymax - ymin, coords=coords)
else:
    print("Error: Unable to extract initial coordinates from the DXF file.")

lower_left, upper_right = find_bounding_box(dxf_file_path)
print(f"Lower Left Corner: {lower_left}")
print(f"Upper Right Corner: {upper_right}")