import open3d as o3d
import numpy as np

# 读取 PCD 点云文件
pcd = o3d.io.read_point_cloud("output1_noisy00000.pcd")  # 请替换为你的点云文件路径
print("原始点云加载完成，点数：", len(pcd.points))

# 统计滤波：去除离群点
nb_neighbors = 20  # 计算最近邻点个数（默认 20）
std_ratio = 2.0  # 设置标准差倍数（默认 2.0）

pcd_denoised, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
pcd_clean = pcd.select_by_index(ind)  # 仅保留去除噪声后的点

# 计算滤除的噪声点
pcd_noise = pcd.select_by_index(ind, invert=True)  # 反选得到噪声点

print(f"降噪后点数：{len(pcd_clean.points)}，被移除的噪声点数：{len(pcd_noise.points)}")

# 颜色设置（可视化对比）
pcd.paint_uniform_color([0.6, 0.6, 0.6])  # 原始点云设为灰色
pcd_clean.paint_uniform_color([0.1, 0.7, 0.1])  # 处理后点云设为绿色
pcd_noise.paint_uniform_color([1, 0, 0])  # 噪声点设为红色

# 以同一窗口并排显示对比
o3d.visualization.draw_geometries([pcd, pcd_clean], window_name="原始点云 vs 降噪后点云")
o3d.visualization.draw_geometries([pcd_clean, pcd_noise], window_name="降噪后点云 vs 移除的噪声点")

# 保存降噪后的 PCD 文件
o3d.io.write_point_cloud("denoised_data.pcd", pcd_clean)
print("降噪后的点云已保存为 denoised_data.pcd")
