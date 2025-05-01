clc; clear; close all;

% ====================== 房间参数 =======================
room_x = [-5, 5];
room_y = [-5, 5];
room_z = [0, 6];
resolution = 0.1;

[x, y, z] = meshgrid(room_x(1):resolution:room_x(2), ...
                     room_y(1):resolution:room_y(2), ...
                     room_z(1):resolution:room_z(2));
points = [x(:), y(:), z(:)];

% ====================== Wi-Fi 参数 =======================
freq = 5; % GHz
ap_position = [0, 0, 0];
P0 = -30; % 发射功率 dBm
c = 3e8;
f_Hz = freq * 1e9;
lambda = c / f_Hz;

% 路损指数设定
if freq == 2.4
    n = 2.0;
elseif freq == 5
    n = 2.5;
elseif freq == 6
    n = 2.8;
end

% 穿墙和障碍损耗设定
wall_loss_values = [10, 15, 20];
box_loss_values = [5, 8, 12];
if freq == 2.4
    wall_loss = wall_loss_values(1);
    box_loss = box_loss_values(1);
elseif freq == 5
    wall_loss = wall_loss_values(2);
    box_loss = box_loss_values(2);
elseif freq == 6
    wall_loss = wall_loss_values(3);
    box_loss = box_loss_values(3);
end

% ====================== 阴影衰落参数 =======================
sigma_shadow = 6; % 阴影衰落的标准差，单位为dB

% ====================== 障碍物定义 =======================
obstacles = {
    [-5, -3, -1, 1, 0, 2];
    [3, 5, 3, 5, 0, 2];
    [3, 5, -5, -3, 4, 6];
};

% ====================== 初始化 =======================
num_points = size(points, 1);
RSSI = zeros(num_points, 1);
max_distance = 100; % 超过这个距离的反射不考虑
reflection_loss = 6; % 每次反射的损耗

% ====================== 遍历每个点 =======================
for i = 1:num_points
    p = points(i, :);
    d = norm(p - ap_position);

    if d < 1e-6
        RSSI(i) = P0;
        continue;
    end

    signal_direct = P0 - 10 * n * log10(d);

    % ====== 穿墙 & 障碍物损耗 ======
    for j = 1:length(obstacles)
        box = obstacles{j};
        is_outer_shell = ...
            (p(1) == box(1) || p(1) == box(2) || ...
             p(2) == box(3) || p(2) == box(4) || ...
             p(3) == box(5) || p(3) == box(6));
        is_inside_box = ...
            (p(1) >= box(1) && p(1) <= box(2) && ...
             p(2) >= box(3) && p(2) <= box(4) && ...
             p(3) >= box(5) && p(3) <= box(6));
        if is_outer_shell && is_inside_box
            signal_direct = signal_direct - box_loss;
        end
    end

    % 房间边界的墙体损耗
    if p(1) == room_x(1) || p(1) == room_x(2) || ...
       p(2) == room_y(1) || p(2) == room_y(2) || ...
       p(3) == room_z(1) || p(3) == room_z(2)
        signal_direct = signal_direct - wall_loss;
    end

    % =================== 多路径反射 =======================
    mirror_signals = [];

    % 定义6个反射面
    mirror_planes = [
        1 0 0 2*room_x(2);    % x = xmax
        1 0 0 2*room_x(1);    % x = xmin
        0 1 0 2*room_y(2);    % y = ymax
        0 1 0 2*room_y(1);    % y = ymin
        0 0 1 2*room_z(2);    % z = zmax
        0 0 1 2*room_z(1);    % z = zmin
    ];

    for m = 1:size(mirror_planes, 1)
        normal = mirror_planes(m, 1:3);
        d_m = mirror_planes(m, 4);
        mirror_ap = ap_position;
        % 镜像点计算
        proj = dot(normal, ap_position) - d_m;
        mirror_ap = ap_position - 2 * proj * normal;
        % 距离和损耗
        d_reflect = norm(p - mirror_ap);
        if d_reflect < 1e-6 || d_reflect > max_distance
            continue;
        end

        % 计算路径差带来的相位延迟
        path_diff = d_reflect - d; % 路径差
        phase_shift = 2 * pi * path_diff / lambda; % 相位延迟

        % 反射信号的损耗与相位变化
        signal_reflect = P0 - 10 * n * log10(d_reflect) - reflection_loss;
        mirror_signals(end+1) = 10^(signal_reflect / 10) * exp(1i * phase_shift); % 使用复数表示，包含幅度和相位
    end

    % ====== 合成信号 ======
    signal_direct_complex = 10^(signal_direct / 10) * exp(1i * 0); % 直射信号，假设没有相位变化
    total_signal = signal_direct_complex + sum(mirror_signals);

    % ====================== 阴影衰落 =======================
    shadow_factor_real = randn() * sigma_shadow; % 随机阴影衰落因子（单位dB）
    total_signal_dB = 10 * log10(abs(total_signal)^2) + shadow_factor_real; % 将阴影衰落添加到总信号的衰减中

    % 获取合成信号的幅度（RSSI）
    RSSI(i) = total_signal_dB;
end

% ====================== 保存与可视化 =======================
csvwrite('wifi_signal_multipath_with_shadowing.csv', [points, RSSI]);
scatter3(points(:,1), points(:,2), points(:,3), 15, RSSI, 'filled');
colorbar;
title(['Wi-Fi 信号（含多路径效应与阴影衰落） - ', num2str(freq), ' GHz']);
xlabel('X');
ylabel('Y');
zlabel('Z');
