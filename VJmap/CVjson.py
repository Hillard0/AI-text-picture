import ezdxf
import os
import json

def convert_to_list(coord):
    """Convert Vec3 object or tuple to a list."""
    if isinstance(coord, ezdxf.math.Vec3):
        return [coord.x, coord.y, coord.z]
    elif isinstance(coord, tuple):
        return list(coord)
    else:
        raise TypeError(f"Unsupported coordinate type: {type(coord)}")


def extract_coordinates(filename):
    coordinates = {
        "points": [],
        "lines": [],
        "lwpolylines": []
    }

    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()

        for entity in msp:
            if entity.dxftype() == 'POINT':  # 提取点的坐标
                coordinates["points"].append(convert_to_list(entity.dxf.location))
            elif entity.dxftype() == 'LINE':  # 提取线段的起始和结束点
                line_coords = {
                    "start": convert_to_list(entity.dxf.start),
                    "end": convert_to_list(entity.dxf.end)
                }
                coordinates["lines"].append(line_coords)
            elif entity.dxftype() == 'LWPOLYLINE':  # 提取多段线的所有顶点
                lwpolyline_coords = [convert_to_list(point) for point in entity.get_points()]
                coordinates["lwpolylines"].append(lwpolyline_coords)

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


# 提取坐标并保存为JSON文件
coords = extract_coordinates(r"C:\Users\Lenovo\Desktop\水闸纵剖面图\text.dxf")
if coords:
    save_to_json(coords, r"C:\Users\Lenovo\Desktop\水闸纵剖面图\text.json")
