import ezdxf
import json


def extract_linear_dimensions(dxf_file_path, output_json_path):
    # 读取DXF文件
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()

    # 存储线性标注信息的列表
    linear_dimensions = []

    # 遍历所有标注对象
    for entity in msp.query('DIMENSION'):
        if entity.dimtype in {0, 1}:  # 线性标注类型的dimtype为0或1
            # 获取标注的起点和终点
            try:
                # 获取显式设置的标注文本
                text = entity.dxf.get('text', None)

                # 如果检测到的text不是数字，则使用测量值
                if text is None or not text.strip().isdigit() or text == '<>':
                    measurement = round(entity.get_measurement(), 0)  # 四舍五入取整到三位小数
                else:
                    measurement = text

                # 获取起点和终点坐标
                start_point = entity.dxf.get('defpoint2')
                end_point = entity.dxf.get('defpoint3')
                dimension_line_position = entity.dxf.get('defpoint')

                if start_point and end_point and dimension_line_position:
                    linear_info = {
                        "type": "Linear Dimension",
                        "text": str(measurement),
                        "measurement": measurement,  # 获取标注的长度值（已四舍五入取整）
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

    # 将结果保存到JSON文件中
    with open(output_json_path, 'w') as json_file:
        json.dump(linear_dimensions, json_file, indent=4)


# 示例用法
dxf_file_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\剖面底板厚度.dxf"
output_json_path = 'linear_dimensions.json'
extract_linear_dimensions(dxf_file_path, output_json_path)
print(f"Linear dimensions extracted and saved to {output_json_path}")
