import numpy as np
import pandas as pd
import open3d as o3d
from sklearn.neighbors import NearestNeighbors
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample  # 导入欠采样所需的库

# 读取 Wi-Fi 采样数据
wifi_data = pd.read_csv("static.csv")

# Wi-Fi 采样点坐标
wifi_points = wifi_data[['x', 'y', 'z']].values

# 读取 3D 点云数据
pcd = o3d.io.read_point_cloud("environment.ply")
point_cloud = np.asarray(pcd.points)  # 点云数据
print("📋 点云数据（前 10 行）：")
print(point_cloud[:10])  # 显示前 10 行

# 训练最近邻模型 (KNN)
knn = NearestNeighbors(n_neighbors=1)
knn.fit(point_cloud)

# 计算 Wi-Fi 采样点到点云的最近距离
distances, indices = knn.kneighbors(wifi_points)

# 设定阈值，判断哪些点是障碍物 (假设阈值 0.12m)
obstacle_threshold = 0.12
wifi_data['is_obstacle'] = (distances[:, 0] < obstacle_threshold).astype(int)

# 欠采样处理，减少类别为0的样本
wifi_data_majority = wifi_data[wifi_data['is_obstacle'] == 0]  # 类别为0的样本
wifi_data_minority = wifi_data[wifi_data['is_obstacle'] == 1]  # 类别为1的样本

# 欠采样，减少类别为0的样本数量，使得类别为0和类别为1的样本数量一致
wifi_data_majority_downsampled = resample(wifi_data_majority,
                                          replace=False,  # 不允许重复采样
                                          n_samples=len(wifi_data_minority),  # 平衡样本数
                                          random_state=42)  # 随机种子，保证每次结果相同

# 合并采样后的数据集
wifi_data_balanced = pd.concat([wifi_data_majority_downsampled, wifi_data_minority])

# 确认数据平衡
print("\n📋 数据集平衡情况：")
print(wifi_data_balanced['is_obstacle'].value_counts())

# 划分特征和标签
X_balanced = wifi_data_balanced[['x', 'y', 'z', 'signal_strength']].values
y_balanced = wifi_data_balanced['is_obstacle'].values

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

# 训练 XGBoost 分类器
model = XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6,
                      random_state=42, eval_metric=["logloss", "error"])

# 训练模型，并记录验证集表现
eval_set = [(X_train, y_train), (X_test, y_test)]
model.fit(X_train, y_train, eval_set=eval_set, verbose=True)

# 提取训练过程中 `logloss` 和 `error` 变化
results = model.evals_result()

# 可视化 `logloss` 和 `error`
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Log Loss 变化
ax[0].plot(results["validation_0"]["logloss"], label="Train Log Loss")
ax[0].plot(results["validation_1"]["logloss"], label="Test Log Loss")
ax[0].set_title("Log Loss during Training")
ax[0].set_xlabel("Iterations")
ax[0].set_ylabel("Log Loss")
ax[0].legend()

# Error 变化
ax[1].plot(results["validation_0"]["error"], label="Train Error")
ax[1].plot(results["validation_1"]["error"], label="Test Error")
ax[1].set_title("Error Rate during Training")
ax[1].set_xlabel("Iterations")
ax[1].set_ylabel("Error Rate")
ax[1].legend()

plt.show()

# 预测训练集
y_train_pred = model.predict(X_train)

# 训练集评估
print("\n📋 训练集分类报告：")
print(classification_report(y_train, y_train_pred))
print("训练集准确率:", accuracy_score(y_train, y_train_pred))

# 预测测试集
y_pred = model.predict(X_test)

# 测试集评估
print("\n📋 测试集分类报告：")
print(classification_report(y_test, y_pred))
print("测试集准确率:", accuracy_score(y_test, y_pred))

# 计算 Precision-Recall 曲线
y_scores = model.predict_proba(X_test)[:, 1]  # 获取正类的概率
precision, recall, _ = precision_recall_curve(y_test, y_scores)

# 绘制 Precision-Recall 曲线
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', color='b', label="Precision-Recall Curve")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend()
plt.grid()
plt.show()



# 手动输入一个测试点 (x, y, z, RSSI)
test_point = np.array([[1.9, -3.9, 3.5, -48.654]])

# 进行预测
predicted_label = model.predict(test_point)
print("\n🧐 手动输入点的预测结果:")
print(f"坐标: {test_point[0][:3]}, RSSI: {test_point[0][3]}, 预测是否为障碍物: {'是' if predicted_label[0] == 1 else '否'}")

# 计算混淆矩阵
cm = confusion_matrix(y_test, y_pred)

# 绘制混淆矩阵热力图
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Non-Obstacle", "Obstacle"],
            yticklabels=["Non-Obstacle", "Obstacle"])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.show()


# 读取 Wi-Fi 分布数据（例如，每隔一段距离扫描的 Wi-Fi 信号）
wifi_distribution_data = pd.read_csv("wifi_signal_multipath_with_shadowing.csv")  # 你要换成实际路径

# 提取特征
distribution_features = wifi_distribution_data[['x', 'y', 'z', 'signal_strength']].values

# 预测每个点是否为障碍物
distribution_predictions = model.predict(distribution_features)

# 找出预测为障碍物的点
obstacle_points = distribution_features[distribution_predictions == 1][:, :3]  # 提取 x, y, z 坐标

# 用 Open3D 可视化这些障碍点
obstacle_pcd = o3d.geometry.PointCloud()
obstacle_pcd.points = o3d.utility.Vector3dVector(obstacle_points)
obstacle_pcd.paint_uniform_color([0, 0, 0])  # 黑色标记


# 显示结果
o3d.visualization.draw_geometries([ obstacle_pcd], window_name="模型预测的障碍物分布图")
