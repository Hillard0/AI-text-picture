import ezdxf


def get_dimension_scale(doc, entity):
    """获取DIMENSION实体的比例因子"""
    # 获取DIMENSION实体的dimlfac属性
    if hasattr(entity.dxf, 'dimlfac'):
        return entity.dxf.dimlfac
    # 尝试从标注样式中获取
    dim_style = doc.dimstyles.get(entity.dxf.dimstyle)
    if dim_style and hasattr(dim_style.dxf, 'dimlfac'):
        return dim_style.dxf.dimlfac
    # 如果都不存在，返回默认比例因子1
    return 1.0


def extract_linear_dimensions(filename):
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    linear_dimensions = []

    for entity in msp.query('DIMENSION'):
        if entity.dimtype in {0, 1}:  # 线性标注类型
            dim_line_location = entity.dxf.defpoint2  # 标注线位置的点

            # 获取标注比例因子
            dim_scale = get_dimension_scale(doc, entity)

            if hasattr(entity.dxf, 'text') and entity.dxf.text not in (None, '<>'):
                measurement_text = entity.dxf.text
                try:
                    measurement = float(measurement_text) * dim_scale
                except ValueError:
                    # 如果文本无法转换为浮点数，直接使用原始文本作为测量值
                    measurement = measurement_text
            else:
                try:
                    measurement = entity.get_measurement() * dim_scale
                except AttributeError:
                    # 如果获取测量值失败，跳过这个标注
                    continue

            linear_dim_info = {
                "measurement": measurement,
                "raw_text": entity.dxf.text,
                "dim_scale": dim_scale,
                "dim_line_location": [dim_line_location.x, dim_line_location.y, dim_line_location.z]
            }
            linear_dimensions.append(linear_dim_info)

    return linear_dimensions


# 示例调用
dxf_file_path = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\cad解析\text0710.dxf"
dimensions = extract_linear_dimensions(dxf_file_path)

for dim in dimensions:
    print(dim)
