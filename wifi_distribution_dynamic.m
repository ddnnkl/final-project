% %% 初始化环境
% clear; clc; close all
% 
% % 室内环境大小
% room_length = 10; % meters
% room_width = 10;
% room_height = 6;
% 
% % 路由器位置 (放在中心)
% router_pos = [room_length/2, room_width/2, 0.5]; % 高度0.5米
% 
% % 静止障碍物参数（3个正方体）
% obstacles = [
%     0 0 4 2; % [x,y,z,size]
%     4 8 0 2;
%     8 0 0 2
% ];
% 
% % 移动障碍物的初始位置和最终位置
% moving_obstacle_start = [1, 1, 0];
% moving_obstacle_end = [9, 9, 0];
% moving_obstacle_size = 1; % 大小
% 
% % 信号参数
% Pt = -30; % 发射功率 dBm
% PL0 = 40; % 参考路径损耗 @1m dB
% n = 2.7; % 路径损耗指数
% shadowing_std = 3; % dB
% 
% % 仿真参数
% grid_resolution = 0.5; % 每隔0.5米采样
% move_duration = 20; % seconds
% sampling_interval = 1; % 每秒采一次
% time_steps = move_duration / sampling_interval;
% [X,Y,Z] = meshgrid(0:grid_resolution:room_length, ...
%                    0:grid_resolution:room_width, ...
%                    0:grid_resolution:room_height);
% sample_points = [X(:), Y(:), Z(:)]; % (N,3)
% 
% %% 准备输出数据
% final_data = []; % 存储所有(x,y,z,RSSI,time,label)
% 
% %% 生成障碍物点云
% obstacle_cloud = [];
% for i = 1:size(obstacles,1)
%     pos = obstacles(i,1:3);
%     sz = obstacles(i,4);
%     [Xo,Yo,Zo] = meshgrid(pos(1):0.1:pos(1)+sz, ...
%                            pos(2):0.1:pos(2)+sz, ...
%                            pos(3):0.1:pos(3)+sz);
%     points = [Xo(:), Yo(:), Zo(:)];
%     obstacle_cloud = [obstacle_cloud; points];
% end
% 
% %% 开始时间步循环
% for t = 1:time_steps
%     current_time = t * sampling_interval;
%     
%     % 计算当前移动障碍物位置 (匀速运动)
%     moving_obstacle_pos = moving_obstacle_start + (moving_obstacle_end - moving_obstacle_start) * (t/time_steps);
%     
%     % 生成移动障碍物点云
%     [Xm, Ym, Zm] = meshgrid(moving_obstacle_pos(1):0.1:moving_obstacle_pos(1)+moving_obstacle_size, ...
%                             moving_obstacle_pos(2):0.1:moving_obstacle_pos(2)+moving_obstacle_size, ...
%                             moving_obstacle_pos(3):0.1:moving_obstacle_pos(3)+moving_obstacle_size);
%     moving_obstacle_cloud = [Xm(:), Ym(:), Zm(:)];
%     
%     % 合并场景点云（静止障碍物 + 移动障碍物）
%     scene_cloud = [obstacle_cloud; moving_obstacle_cloud];
%     
%     % 遍历所有采样点
%     for i = 1:size(sample_points,1)
%         pt = sample_points(i,:);
%         
%         % 计算自由空间损耗
%         d = norm(pt - router_pos);
%         if d < 1
%             d = 1; % 避免 log(0) 错误
%         end
%         path_loss = PL0 + 10*n*log10(d);
%         
%         % 穿过障碍物附加损耗
%         attenuation = 0;
%         for j = 1:size(obstacles,1)
%             obs_center = obstacles(j,1:3) + obstacles(j,4)/2;
%             obs_size = obstacles(j,4);
%             if is_line_cross_cube(router_pos, pt, obs_center, obs_size)
%                 attenuation = attenuation + 5; % 穿过一个障碍增加5dB
%             end
%         end
%         
%         % 穿过移动障碍物附加损耗
%         moving_obs_center = moving_obstacle_pos + moving_obstacle_size / 2;
%         if is_line_cross_cube(router_pos, pt, moving_obs_center, moving_obstacle_size)
%             attenuation = attenuation + 5;
%         end
%         
%         % 多径效应模拟（简单Rayleigh衰落近似）
%         multipath = 0 + 3*(randn);
%         
%         % 阴影衰落（Shadowing）
%         shadowing = shadowing_std * randn;
%         
%         % 总接收功率
%         RSSI = Pt - path_loss - attenuation + multipath + shadowing;
%         
%         % 判断点是否在障碍物/人体内部
%         label = is_in_cloud(pt, scene_cloud);
%         
%         % 记录
%         final_data = [final_data; pt, RSSI, current_time, label];
%     end
%     
%     fprintf('Time step %d/%d finished\n',t,time_steps);
% end
% 
% %% 保存数据
% writematrix(final_data, 'dataset.csv');
% disp('Data generation complete!');
% 
% %% 辅助函数 - 判断线段是否穿过立方体
% function crossed = is_line_cross_cube(p1, p2, cube_center, cube_size)
%     cube_min = cube_center - cube_size/2;
%     cube_max = cube_center + cube_size/2;
%     crossed = ray_box_intersect(p1, p2, cube_min, cube_max);
% end
% 
% %% 辅助函数 - 点是否在点云附近（容差判断）
% function inside = is_in_cloud(pt, cloud)
%     tolerance = 0.1; % 10cm容差
%     distances = sqrt(sum((cloud - pt).^2,2));
%     inside = any(distances < tolerance);
% end
% 
% %% 辅助函数 - 线段和AABB盒子相交检测
% function hit = ray_box_intersect(p1, p2, box_min, box_max)
%     dir = p2 - p1;
%     tmin = (box_min - p1)./dir;
%     tmax = (box_max - p1)./dir;
%     t1 = min(tmin, tmax);
%     t2 = max(tmin, tmax);
%     tnear = max([0, t1]);
%     tfar = min([1, t2]);
%     hit = tnear <= tfar;
% end

%% 初始化环境
clear; clc; close all

% 室内环境大小
room_length = 10; % meters
room_width = 10;
room_height = 6;

% 路由器位置 (放在中心)
router_pos = [room_length/2, room_width/2, 0.5]; % 高度0.5米

% 静止障碍物参数（3个正方体）
obstacles = [
    0 0 4 2; % [x,y,z,size]
    4 8 0 2;
    8 0 0 2
];

% 移动障碍物的初始位置和最终位置
moving_obstacle_start = [1, 1, 0];
moving_obstacle_end = [9, 9, 0];
moving_obstacle_size = 1; % 大小

% 信号参数
Pt = -30; % 发射功率 dBm
PL0 = 40; % 参考路径损耗 @1m dB
n = 2.7; % 路径损耗指数
shadowing_std = 3; % dB

% 仿真参数
grid_resolution = 0.5; % 每隔0.5米采样
move_duration = 20; % seconds
sampling_interval = 1; % 每秒采一次
time_steps = move_duration / sampling_interval;
[X,Y,Z] = meshgrid(0:grid_resolution:room_length, ...
                   0:grid_resolution:room_width, ...
                   0:grid_resolution:room_height);
sample_points = [X(:), Y(:), Z(:)]; % (N,3)

%% 准备输出数据
final_data = []; % 存储所有(x,y,z,RSSI,time,label)

%% 生成障碍物点云（只生成表面）
obstacle_cloud = [];
for i = 1:size(obstacles,1)
    pos = obstacles(i,1:3);
    sz = obstacles(i,4);
    
    % 生成正方体表面上的点
    [Xo, Yo, Zo] = meshgrid(pos(1):0.1:pos(1)+sz, ...
                             pos(2):0.1:pos(2)+sz, ...
                             pos(3):0.1:pos(3)+sz);
    
    % 过滤掉不属于表面的点（只保留正方体的表面）
    points = [];
    for x = pos(1):0.1:pos(1)+sz
        for y = pos(2):0.1:pos(2)+sz
            % 保留x, y轴上的表面点
            points = [points; [x, y, pos(3)]; [x, y, pos(3)+sz]];
        end
    end
    for y = pos(2):0.1:pos(2)+sz
        for z = pos(3):0.1:pos(3)+sz
            % 保留y, z轴上的表面点
            points = [points; [pos(1), y, z]; [pos(1)+sz, y, z]];
        end
    end
    for x = pos(1):0.1:pos(1)+sz
        for z = pos(3):0.1:pos(3)+sz
            % 保留x, z轴上的表面点
            points = [points; [x, pos(2), z]; [x, pos(2)+sz, z]];
        end
    end
    
    % 添加到障碍物点云
    obstacle_cloud = [obstacle_cloud; points];
end

%% 开始时间步循环
for t = 1:time_steps
    current_time = t * sampling_interval;
    
    % 计算当前移动障碍物位置 (匀速运动)
    moving_obstacle_pos = moving_obstacle_start + (moving_obstacle_end - moving_obstacle_start) * (t/time_steps);
    
    % 生成移动障碍物表面点云
    [Xm, Ym, Zm] = meshgrid(moving_obstacle_pos(1):0.1:moving_obstacle_pos(1)+moving_obstacle_size, ...
                            moving_obstacle_pos(2):0.1:moving_obstacle_pos(2)+moving_obstacle_size, ...
                            moving_obstacle_pos(3):0.1:moving_obstacle_pos(3)+moving_obstacle_size);
    
    moving_obstacle_cloud = [];
    for x = moving_obstacle_pos(1):0.1:moving_obstacle_pos(1)+moving_obstacle_size
        for y = moving_obstacle_pos(2):0.1:moving_obstacle_pos(2)+moving_obstacle_size
            moving_obstacle_cloud = [moving_obstacle_cloud; [x, y, moving_obstacle_pos(3)]; [x, y, moving_obstacle_pos(3)+moving_obstacle_size]];
        end
    end
    for y = moving_obstacle_pos(2):0.1:moving_obstacle_pos(2)+moving_obstacle_size
        for z = moving_obstacle_pos(3):0.1:moving_obstacle_pos(3)+moving_obstacle_size
            moving_obstacle_cloud = [moving_obstacle_cloud; [moving_obstacle_pos(1), y, z]; [moving_obstacle_pos(1)+moving_obstacle_size, y, z]];
        end
    end
    for x = moving_obstacle_pos(1):0.1:moving_obstacle_pos(1)+moving_obstacle_size
        for z = moving_obstacle_pos(3):0.1:moving_obstacle_pos(3)+moving_obstacle_size
            moving_obstacle_cloud = [moving_obstacle_cloud; [x, moving_obstacle_pos(2), z]; [x, moving_obstacle_pos(2)+moving_obstacle_size, z]];
        end
    end
    
    % 合并场景点云（静止障碍物 + 移动障碍物）
    scene_cloud = [obstacle_cloud; moving_obstacle_cloud];
    
    % 遍历所有采样点
    for i = 1:size(sample_points,1)
        pt = sample_points(i,:);
        
        % 计算自由空间损耗
        d = norm(pt - router_pos);
        if d < 1
            d = 1; % 避免 log(0) 错误
        end
        path_loss = PL0 + 10*n*log10(d);
        
        % 穿过障碍物附加损耗
        attenuation = 0;
        for j = 1:size(obstacles,1)
            obs_center = obstacles(j,1:3) + obstacles(j,4)/2;
            obs_size = obstacles(j,4);
            if is_line_cross_cube(router_pos, pt, obs_center, obs_size)
                attenuation = attenuation + 5; % 穿过一个障碍增加5dB
            end
        end
        
        % 穿过移动障碍物附加损耗
        moving_obs_center = moving_obstacle_pos + moving_obstacle_size / 2;
        if is_line_cross_cube(router_pos, pt, moving_obs_center, moving_obstacle_size)
            attenuation = attenuation + 5;
        end
        
        % 多径效应模拟（简单Rayleigh衰落近似）
        multipath = 0 + 3*(randn);
        
        % 阴影衰落（Shadowing）
        shadowing = shadowing_std * randn;
        
        % 总接收功率
        RSSI = Pt - path_loss - attenuation + multipath + shadowing;
        
        % 判断点是否在障碍物/人体内部
        label = is_in_cloud(pt, scene_cloud);
        
        % 记录
        final_data = [final_data; pt, RSSI, current_time, label];
    end
    
    fprintf('Time step %d/%d finished\n',t,time_steps);
end

%% 保存数据
writematrix(final_data, 'dataset.csv');
disp('Data generation complete!');

%% 辅助函数 - 判断线段是否穿过立方体
function crossed = is_line_cross_cube(p1, p2, cube_center, cube_size)
    cube_min = cube_center - cube_size/2;
    cube_max = cube_center + cube_size/2;
    crossed = ray_box_intersect(p1, p2, cube_min, cube_max);
end

%% 辅助函数 - 点是否在点云附近（容差判断）
function inside = is_in_cloud(pt, cloud)
    tolerance = 0.1; % 10cm容差
    distances = sqrt(sum((cloud - pt).^2,2));
    inside = any(distances < tolerance);
end

%% 辅助函数 - 线段和AABB盒子相交检测
function hit = ray_box_intersect(p1, p2, box_min, box_max)
    dir = p2 - p1;
    tmin = (box_min - p1)./dir;
    tmax = (box_max - p1)./dir;
    t1 = min(tmin, tmax);
    t2 = max(tmin, tmax);
    tnear = max([0, t1]);
    tfar = min([1, t2]);
    hit = tnear <= tfar;
end

