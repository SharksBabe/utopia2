import csv
import os

# 输入文件路径
input_file = "bilibili_endfield_comments_edge.csv"
# 输出文件路径
output_clean_file = "bilibili_endfield_comments_clean.csv"
output_filtered_file = "bilibili_endfield_comments_filtered.csv"

# 要过滤的字符串
filter_string = "终末地临行事项开启，参与必得五星武器："

print(f"开始数据清洗...")
print(f"输入文件: {input_file}")
print(f"过滤字符串: {filter_string}")

# 检查输入文件是否存在
if not os.path.exists(input_file):
    print(f"错误: 输入文件 '{input_file}' 不存在！")
    exit(1)

# 读取并处理数据
clean_data = []
filtered_data = []

try:
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        print(f"文件字段: {fieldnames}")
        
        for i, row in enumerate(reader, 1):
            content = row.get('content', '')
            # 检查level和stars
            level = row.get('level', '')
            stars = row.get('stars', '')
            
            # 检查是否需要过滤
            should_filter = False
            
            # 检查level是否等于0
            try:
                if int(level) == 0:
                    should_filter = True
            except:
                pass
            
            # 检查stars是否等于0
            try:
                if int(stars) == 0:
                    should_filter = True
            except:
                pass
            
            # 检查是否包含过滤字符串
            if filter_string in content:
                should_filter = True
            
            if should_filter:
                filtered_data.append(row)
            else:
                clean_data.append(row)
            
            if i % 100 == 0:
                print(f"已处理 {i} 条记录")
    
    print(f"共读取 {len(clean_data) + len(filtered_data)} 条记录")
    print(f"过滤掉 {len(filtered_data)} 条记录")
    print(f"保留 {len(clean_data)} 条记录")
    
    # 保存清洗后的数据
    with open(output_clean_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_data)
    print(f"清洗后的数据已保存到: {output_clean_file}")
    
    # 保存过滤掉的数据
    with open(output_filtered_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)
    print(f"过滤掉的数据已保存到: {output_filtered_file}")
    
    print("数据清洗完成！")
    
except Exception as e:
    print(f"错误: {str(e)}")
