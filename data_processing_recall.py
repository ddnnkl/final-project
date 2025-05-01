import numpy as np
import pandas as pd
import open3d as o3d
from sklearn.neighbors import NearestNeighbors
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns


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

# 划分训练集和测试集
X = wifi_data[['x', 'y', 'z', 'signal_strength']].values
y = wifi_data['is_obstacle'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
y_train_scores = model.predict_proba(X_train)[:, 1]  # 获取类别 1（障碍物）的概率
y_train_pred = (y_train_scores >= 0.45).astype(int)  # 设定新的阈值 0.45

# 训练集评估
print("\n📋 训练集分类报告：")
print(classification_report(y_train, y_train_pred))
print("训练集准确率:", accuracy_score(y_train, y_train_pred))

# 预测测试集
y_scores = model.predict_proba(X_test)[:, 1]  # 获取类别 1（障碍物）的概率
y_pred = (y_scores >= 0.45).astype(int)  # 设定新的阈值 0.45

# 测试集评估
print("\n📋 测试集分类报告（阈值 0.45）：")
print(classification_report(y_test, y_pred))
print("测试集准确率:", accuracy_score(y_test, y_pred))

# 计算 Precision-Recall 曲线
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
test_point = np.array([[3.3, 4, 1.8, -48.487]])

# 进行预测
test_score = model.predict_proba(test_point)[:, 1]  # 获取类别 1（障碍物）的概率
predicted_label = int(test_score >= 0.45)  # 设定新的阈值 0.45
print("\n🧐 手动输入点的预测结果:")
print(f"坐标: {test_point[0][:3]}, RSSI: {test_point[0][3]}, 预测是否为障碍物: {'是' if predicted_label == 1 else '否'}")

# 计算混淆矩阵
cm = confusion_matrix(y_test, y_pred)

# 绘制混淆矩阵热力图
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Non-Obstacle", "Obstacle"],
            yticklabels=["Non-Obstacle", "Obstacle"])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix (Threshold = 0.45)")
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
