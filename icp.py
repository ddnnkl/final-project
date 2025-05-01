import open3d as o3d
import numpy as np

# 读取两个点云
source = o3d.io.read_point_cloud("final_merged1.ply")
target = o3d.io.read_point_cloud("transformed_combined.ply")

# 可选：下采样（加快速度、增强鲁棒性）
source_down = source.voxel_down_sample(voxel_size=0.02)
target_down = target.voxel_down_sample(voxel_size=0.02)

# 可选：估计法线
source_down.estimate_normals()
target_down.estimate_normals()

# 初始变换
init_trans = np.eye(4)

# 使用 ICP 进行配准
threshold = 0.05
reg_p2p = o3d.pipelines.registration.registration_icp(
    source_down, target_down, threshold, init_trans,
    o3d.pipelines.registration.TransformationEstimationPointToPoint()
)

# 获取最终变换矩阵
final_trans = reg_p2p.transformation
print("ICP transformation matrix:\n", final_trans)

# 对原始高精度点云进行变换
source.transform(final_trans)

# 合并两个点云
combined = source + target

# 保存合并后的点云
o3d.io.write_point_cloud("merged_result.ply", combined)
print("已保存合并后的点云为 'merged_result.ply'")

# 可视化合并结果
o3d.visualization.draw_geometries([
    source.paint_uniform_color([1, 0, 0]),   # 红色：变换后的 source
    target.paint_uniform_color([0, 1, 0])    # 绿色：target
])
