import ezdxf
import os
import json
from ezdxf.math import area, Vec3

def convert_to_list(coord):
    """Convert Vec3 object or tuple to a list."""
    if isinstance(coord, ezdxf.math.Vec3):
        return [coord.x, coord.y, coord.z]
    elif isinstance(coord, tuple):
        return list(coord[:3])  # Only take the first three elements
    else:
        raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def is_inside_bbox(coord, bbox):
    """Check if a coordinate is inside the bounding box."""
    if len(coord) != 3:
        raise ValueError(f"Coordinate must be a tuple or list with exactly 3 elements: {coord}")

    x, y, z = coord
    min_x, min_y, max_x, max_y = bbox
    return min_x <= x <= max_x and min_y <= y <= max_y

def calculate_lwpolyline_area(points):
    """Calculate the area of a closed LWPOLYLINE given its points."""
    points_2d = [(point[0], point[1]) for point in points]
    return abs(area(points_2d))

def calculate_distance(point1, point2):
    """Calculate the distance between two points."""
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2) ** 0.5

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
        "mtexts": []
    }

    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()

        for entity in msp:
            if entity.dxftype() == 'POINT':
                point_coord = convert_to_list(entity.dxf.location)
                if is_inside_bbox(point_coord, bbox):
                    coordinates["points"].append(point_coord)
            elif entity.dxftype() == 'LINE':
                start_coord = convert_to_list(entity.dxf.start)
                end_coord = convert_to_list(entity.dxf.end)
                if is_inside_bbox(start_coord, bbox) or is_inside_bbox(end_coord, bbox):
                    line_coords = {
                        "start": start_coord,
                        "end": end_coord,
                        "length": calculate_distance(start_coord, end_coord)
                    }
                    coordinates["lines"].append(line_coords)
            elif entity.dxftype() == 'LWPOLYLINE':
                lwpolyline_coords = [convert_to_list(point) for point in entity.get_points()]
                is_closed = entity.is_closed
                if any(is_inside_bbox(point, bbox) for point in lwpolyline_coords):
                    lwpolyline_info = {
                        "points": lwpolyline_coords,
                        "is_closed": is_closed,
                        "area": calculate_lwpolyline_area(lwpolyline_coords) if is_closed else None,
                        "length": calculate_lwpolyline_length(lwpolyline_coords)
                    }
                    coordinates["lwpolylines"].append(lwpolyline_info)
            elif entity.dxftype() == 'SPLINE':
                spline_coords = [convert_to_list(point) for point in entity.control_points]
                if any(is_inside_bbox(point, bbox) for point in spline_coords):
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
                if is_inside_bbox(center, bbox):
                    coordinates["arcs"].append(arc_info)
            elif entity.dxftype() == 'TEXT':
                text_location = convert_to_list(entity.dxf.insert)
                if is_inside_bbox(text_location, bbox):
                    text_info = {
                        "text": entity.dxf.text,
                        "location": text_location,
                        "height": entity.dxf.height
                    }
                    coordinates["texts"].append(text_info)
            elif entity.dxftype() == 'MTEXT':
                mtext_location = convert_to_list(entity.dxf.insert)
                if is_inside_bbox(mtext_location, bbox):
                    mtext_info = {
                        "text": entity.text,
                        "location": mtext_location,
                        "height": entity.dxf.char_height
                    }
                    coordinates["mtexts"].append(mtext_info)

        return coordinates
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except ezdxf.DXFStructureError as dxf_error:
        print(f"DXFStructureError: {dxf_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def save_to_json(data, output_filename):
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Coordinates successfully saved to {output_filename}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

# Define the bounding box coordinates
# xmin = int(input("Enter xmin: "))
# ymin = int(input("Enter ymin: "))
# xmax = int(input("Enter xmax: "))
# ymax = int(input("Enter ymax: "))
xmin , ymin , xmax ,ymax = input("Enter xmin,ymin,xmax,ymax: ").split()
xmin = int(xmin)
ymin = int(ymin)
xmax = int(xmax)
ymax = int(ymax)
bbox = (xmin, ymin, xmax, ymax)

# Extract coordinates within the bounding box and save to a JSON file
coords = extract_coordinates_in_bbox(r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\9#口门水工施工图.dxf", bbox)
if coords:
    save_to_json(coords, r"C:\\Users\\Lenovo\\Desktop\\水闸纵剖面图\\text3.5.json")
