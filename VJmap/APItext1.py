import ezdxf
import os


def extract_coordinates(filename):
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()
        coordinates = []

        for entity in msp:
            if entity.dxftype() == 'POINT':  # 提取点的坐标
                coordinates.append(entity.dxf.location)
            elif entity.dxftype() == 'LINE':  # 提取线段的起始和结束点
                coordinates.append(entity.dxf.start)
                coordinates.append(entity.dxf.end)
            elif entity.dxftype() == 'LWPOLYLINE':  # 提取多段线的所有顶点
                coordinates.extend(entity.get_points())

        return coordinates
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except ezdxf.DXFStructureError as dxf_error:
        print(f"DXFStructureError: {dxf_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# 调用函数并打印结果
coords = extract_coordinates(r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\9#口门水工施工图.dxf")
if coords:
    for coord in coords:
        print(coord)
