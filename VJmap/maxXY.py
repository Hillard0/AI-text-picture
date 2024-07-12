import ezdxf
import os


def convert_to_list(coord):
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
            if entity.dxftype() == 'LINE':
                start = convert_to_list(entity.dxf.start)
                end = convert_to_list(entity.dxf.end)
                print(start[0],start[1],end[0],end[1] , " ----- " , min_x,min_y,max_x,max_y )
                min_x = min(min_x, start[0], end[0])
                min_y = min(min_y, start[1], end[1])
                max_x = max(max_x, start[0], end[0])
                max_y = max(max_y, start[1], end[1])
            elif entity.dxftype() == 'LWPOLYLINE':
                points = [convert_to_list(point) for point in entity.get_points()]
                for point in points:
                    print(point[0],point[1] , min_x,min_y,max_x,max_y)
                    min_x = min(min_x, point[0])
                    min_y = min(min_y, point[1])
                    max_x = max(max_x, point[0])
                    max_y = max(max_y, point[1])
        if min_x < 1e-10:
            min_x = 0
        if min_y < 1e-10:
            min_y = 0
        print(min_x, min_y, max_x, max_y , " ********** ")
    return (min_x, min_y), (max_x, max_y)

# Define the DXF file path
dxf_file_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\9#口门水工施工图.dxf"

# Find and print the outermost coordinates
lower_left, upper_right = find_bounding_box(dxf_file_path)
print(f"Lower Left Corner: {lower_left}")
print(f"Upper Right Corner: {upper_right}")




