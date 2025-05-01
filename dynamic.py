# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.ensemble import RandomForestClassifier
# from mpl_toolkits.mplot3d import Axes3D
# import os
#
# # 1. 读入数据
# data = pd.read_csv('dataset1.csv')
#
# # 2. 训练模型
# X = data[['x', 'y', 'z', 'RSSI']]
# Y = data['label']
#
# model = RandomForestClassifier(n_estimators=50, random_state=42)
# model.fit(X, Y)
#
# # 3. 按时间分组
# times = sorted(data['time'].unique())
#
# # 创建保存图片的文件夹
# output_dir = 'frames'
# os.makedirs(output_dir, exist_ok=True)
#
# # 4. 遍历每个时间点，分别画图
# for t in times:
#     fig = plt.figure(figsize=(10, 8))
#     ax = fig.add_subplot(111, projection='3d')
#     ax.set_xlim(0, 10)
#     ax.set_ylim(0, 10)
#     ax.set_zlim(0, 3)
#     ax.set_xlabel('X (m)')
#     ax.set_ylabel('Y (m)')
#     ax.set_zlabel('Z (m)')
#     ax.set_title(f'Obstacle Prediction - Time {t:.0f} s')
#
#     # 拿出当前时间的数据
#     frame_data = data[data['time'] == t]
#     X_frame = frame_data[['x', 'y', 'z', 'RSSI']]
#
#     preds = model.predict(X_frame)
#
#     # 根据预测结果分开障碍物和非障碍物
#     obstacle_points = X_frame[preds == 1]
#     free_points = X_frame[preds == 0]
#
#     # 画障碍物（黑色点）
#     if not obstacle_points.empty:
#         ax.scatter(obstacle_points['x'], obstacle_points['y'], obstacle_points['z'],
#                    c='black', marker='o', s=10, label='Obstacle')
#
#     # 画自由空间点（透明或者淡颜色）
#     if not free_points.empty:
#         ax.scatter(free_points['x'], free_points['y'], free_points['z'],
#                    c='lightgray', marker='o', s=10, alpha=0.1, label='Free Space')
#
#     ax.legend()
#
#     # 保存每一帧的图
#     plt.savefig(f'{output_dir}/frame_{int(t):03d}.png')
#     plt.close(fig)
#

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import train_test_split
import os

# 1. 读入数据
data = pd.read_csv('dynamic.csv')

# 2. 准备特征和标签
X = data[['x', 'y', 'z', 'RSSI']]
Y = data['label']

# 3. 划分训练集和测试集
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 4. 训练模型（用训练集）
model = XGBClassifier(n_estimators=1000, random_state=42, eval_metric='logloss')
model.fit(X_train, Y_train)

# 5. 按时间分组（用原始data里的时间列）
times = sorted(data['time'].unique())

# 创建保存图片的文件夹
output_dir = 'frames'
os.makedirs(output_dir, exist_ok=True)

# 6. 遍历每个时间点，分别画图（用全体数据）
for t in times:
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_zlim(0, 6)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'Obstacle Prediction - Time {t:.0f} s')

    # 拿出当前时间的数据
    frame_data = data[data['time'] == t]
    X_frame = frame_data[['x', 'y', 'z', 'RSSI']]

    preds = model.predict(X_frame)

    # 根据预测结果分开障碍物和自由空间
    obstacle_points = X_frame[preds == 1]
    free_points = X_frame[preds == 0]

    # 画障碍物（黑色点）
    if not obstacle_points.empty:
        ax.scatter(obstacle_points['x'], obstacle_points['y'], obstacle_points['z'],
                   c='black', marker='o', s=10, label='Obstacle')

    # 画自由空间（灰色透明）
    if not free_points.empty:
        ax.scatter(free_points['x'], free_points['y'], free_points['z'],
                   c='lightgray', marker='o', s=10, alpha=0.1, label='Free Space')

    ax.legend()

    # 保存每一帧
    plt.savefig(f'{output_dir}/frame_{int(t):03d}.png')
    plt.close(fig)

