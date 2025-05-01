import numpy as np
import open3d as o3d

# 读取 PLY 文件
pcd = o3d.io.read_point_cloud("merged_result.ply")

# 转换为 NumPy 数组
points = np.asarray(pcd.points)

# 交换 y 轴和 z 轴
points[:, [1, 2]] = points[:, [2, 1]]

# 以 y 轴为基准对称翻转
points[:, 1] = -points[:, 1]

# 沿 y 轴负方向平移 5
points[:, 1] -= 5

# 沿 z 轴正方向平移 6
points[:, 2] += 4

# 更新点云对象
pcd.points = o3d.utility.Vector3dVector(points)

# 保存处理后的点云
o3d.io.write_point_cloud("final1.ply", pcd)

print("点云变换完成，已保存为 final1.ply")
