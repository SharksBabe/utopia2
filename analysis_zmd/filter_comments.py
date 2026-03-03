import pandas as pd
import csv

# 读取清洗后的数据
input_file = "bilibili_endfield_comments_clean.csv"
df = pd.read_csv(input_file)
print(f"共读取 {len(df)} 条评论")

# 确保level和stars列是数值类型
df['level'] = pd.to_numeric(df['level'], errors='coerce')
df['stars'] = pd.to_numeric(df['stars'], errors='coerce')

# 筛选条件1: level = 6, stars = 1
filtered_df1 = df[(df['level'] == 6) & (df['stars'] == 1)]
output_file1 = "bilibili_endfield_comments_level6_stars1.csv"
filtered_df1.to_csv(output_file1, index=False, encoding='utf-8-sig')
print(f"筛选条件1(level=6, stars=1): 找到 {len(filtered_df1)} 条评论，已保存到 {output_file1}")

# 筛选条件2: level = 6, stars = 5
filtered_df2 = df[(df['level'] == 6) & (df['stars'] == 5)]
output_file2 = "bilibili_endfield_comments_level6_stars5.csv"
filtered_df2.to_csv(output_file2, index=False, encoding='utf-8-sig')
print(f"筛选条件2(level=6, stars=5): 找到 {len(filtered_df2)} 条评论，已保存到 {output_file2}")

print("\n筛选完成！")
