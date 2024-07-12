import ezdxf

def is_entity_in_bounds(entity, bounds):
    """
    检查实体是否在给定的裁剪范围内。
    :param entity: DXF实体
    :param bounds: (xmin, ymin, xmax, ymax)
    :return: 是否在范围内
    """
    xmin, ymin, xmax, ymax = bounds
    if entity.dxftype() == 'LINE':
        start, end = entity.dxf.start, entity.dxf.end
        return (xmin <= start.x <= xmax and ymin <= start.y <= ymax) or \
               (xmin <= end.x <= xmax and ymin <= end.y <= ymax)
    elif entity.dxftype() == 'CIRCLE':
        center = entity.dxf.center
        radius = entity.dxf.radius
        return (xmin <= center.x - radius <= xmax and ymin <= center.y - radius <= ymax) or \
               (xmin <= center.x + radius <= xmax and ymin <= center.y + radius <= ymax)
    # 根据需要添加更多实体类型的判断
    return False

def crop_dxf(input_file, output_file, bounds):
    """
    裁剪DXF文件并生成新的文件。
    :param input_file: 输入DXF文件路径
    :param output_file: 输出DXF文件路径
    :param bounds: (xmin, ymin, xmax, ymax)
    """
    # 读取原始DXF文件
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()

    # 创建新的DXF文件
    new_doc = ezdxf.new(dxfversion=doc.dxfversion)
    new_msp = new_doc.modelspace()

    # 过滤并复制在裁剪范围内的实体
    for entity in msp:
        if is_entity_in_bounds(entity, bounds):
            new_msp.add_entity(entity)

    # 保存新的DXF文件
    new_doc.saveas(output_file)

# 使用示例
input_file = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\图纸测试\201112311325299076340.dxf"
output_file = r"C:\Users\Lenovo\Desktop\水闸纵剖面图\图纸测试\CJ20212.dxf"
bounds = (1459,2225,2057,2649)  # 定义裁剪范围 (xmin, ymin, xmax, ymax)

crop_dxf(input_file, output_file, bounds)
