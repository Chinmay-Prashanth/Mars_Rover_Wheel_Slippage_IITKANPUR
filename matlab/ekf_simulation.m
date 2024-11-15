%% Mars Rover EKF State Estimation Simulation
% Generates the EKF slip detection graph as shown in research paper
% Compatible with MATLAB and GNU Octave
% 
% This simulation models a Mars rover's navigation system with Extended Kalman Filter
% for state estimation and slip detection during rover locomotion on Martian terrain.
% 
% Research Application: Single-wheel test bench for slip detection validation
% Institution: IIT Kanpur Mars Rover Research
% 
% Usage: Modify the USER CONFIGURATION section below for your specific rover setup

clear all; close all; clc;

% Load statistics package for Octave
if exist('OCTAVE_VERSION', 'builtin')
    pkg load statistics
end

fprintf('========================================================\n');
fprintf('    MARS ROVER EKF STATE ESTIMATION SIMULATION\n');
fprintf('    IIT Kanpur Mars Rover Research Project\n');
fprintf('========================================================\n\n');

%% =========================== USER CONFIGURATION ===========================
% CONFIGURE THESE PARAMETERS FOR YOUR SPECIFIC ROVER SETUP
% Enter your rover's specifications below

% --- Rover Physical Parameters ---
ROVER_MASS = [];                      % Rover mass in kg (e.g., 15.0 for small rover, 899.0 for Mars rover)
ROVER_WHEEL_RADIUS = [];              % Wheel radius in meters (e.g., 0.125 for small, 0.2625 for Mars rover)
ROVER_WHEEL_BASE = [];                % Distance between front/rear wheels in meters
ROVER_TRACK_WIDTH = [];               % Distance between left/right wheels in meters  
ROVER_MAX_SPEED = [];                 % Maximum rover speed in m/s
NUM_WHEELS = [];                      % Number of wheels (e.g., 4 or 6)

% --- Simulation Parameters ---
SIMULATION_TIME = [];                 % Total simulation time in seconds
TIME_STEP = [];                       % Time step in seconds (recommend 0.1 for 10 Hz)
SLIP_PROBABILITY = [];                % Probability of slip occurrence (0-1, e.g., 0.15-0.25)
SLIP_SEVERITY = [];                   % Slip severity factor (0-1, where 0=full slip, 1=no slip)

% --- Rover Motion Commands ---
FORWARD_VELOCITY = [];                % Forward velocity command in m/s
VERTICAL_VELOCITY = [];               % Vertical velocity (z-axis) in m/s
ANGULAR_VELOCITY = [];                % Angular velocity (turning) in rad/s
PITCH_RATE = [];                      % Pitch angle rate in rad/s

% --- EKF Noise Parameters ---
PROCESS_NOISE_VAR = [];               % Process noise variance (0.01-0.05 typical)
MEASUREMENT_NOISE_VAR = [];           % Measurement noise variance (0.1-0.15 typical)
INITIAL_COVARIANCE = [];              % Initial state covariance (0.1-0.2 typical)

% --- Slip Detection Parameters ---
SLIP_THRESHOLD = [];                  % Innovation threshold for slip detection
MIN_SLIP_DURATION = [];               % Minimum slip duration in seconds
WHEEL_SINKAGE_FACTOR = [];            % Wheel sinkage in soft terrain (0-1)

% --- Terrain Parameters ---
TERRAIN_TYPE = '';                    % Options: 'rocky', 'sandy', 'smooth', 'martian_regolith', etc.
TERRAIN_ROUGHNESS = [];               % Terrain roughness factor (0-1)
GRAVITY = [];                         % Gravity in m/s² (Earth: 9.81, Mars: 3.711, Moon: 1.62)
ATMOSPHERIC_PRESSURE = [];            % Atmospheric pressure in bar (Earth: 1.0, Mars: 0.006)

% --- Environmental Factors (Optional, set to 1.0 if not applicable) ---
DUST_STORM_FACTOR = [];               % Dust storm effect on sensors (1.0 = no storm)
TEMPERATURE_EFFECT = [];              % Temperature effect on rover performance
WHEEL_WEAR_FACTOR = [];               % Wheel wear factor (1.0 = new wheels)

% --- Output Configuration ---
SAVE_PLOTS = true;                    % Save plots to files
PLOT_RESOLUTION = 300;                % Plot resolution in DPI
SHOW_ANALYSIS = true;                 % Show additional analysis plots

% =========================== PARAMETER VALIDATION ===========================

% Check if all required parameters are set
required_params = {'ROVER_MASS', 'ROVER_WHEEL_RADIUS', 'ROVER_WHEEL_BASE', ...
                  'ROVER_TRACK_WIDTH', 'ROVER_MAX_SPEED', 'NUM_WHEELS', ...
                  'SIMULATION_TIME', 'TIME_STEP', 'SLIP_PROBABILITY', 'SLIP_SEVERITY', ...
                  'FORWARD_VELOCITY', 'VERTICAL_VELOCITY', 'ANGULAR_VELOCITY', 'PITCH_RATE', ...
                  'PROCESS_NOISE_VAR', 'MEASUREMENT_NOISE_VAR', 'INITIAL_COVARIANCE', ...
                  'SLIP_THRESHOLD', 'MIN_SLIP_DURATION', 'WHEEL_SINKAGE_FACTOR', ...
                  'TERRAIN_ROUGHNESS', 'GRAVITY', 'ATMOSPHERIC_PRESSURE', ...
                  'DUST_STORM_FACTOR', 'TEMPERATURE_EFFECT', 'WHEEL_WEAR_FACTOR'};

missing_params = {};
for i = 1:length(required_params)
    param_name = required_params{i};
    if strcmp(param_name, 'TERRAIN_TYPE')
        if isempty(eval(param_name))
            missing_params{end+1} = param_name;
        end
    else
        if isempty(eval(param_name))
            missing_params{end+1} = param_name;
        end
    end
end

if ~isempty(missing_params)
    fprintf('ERROR: Please configure the following parameters in the USER CONFIGURATION section:\n');
    for i = 1:length(missing_params)
        fprintf('  - %s\n', missing_params{i});
    end
    fprintf('\nExample configurations:\n');
    fprintf('\n--- Small Test Rover Example ---\n');
    fprintf('ROVER_MASS = 15.0;\n');
    fprintf('ROVER_WHEEL_RADIUS = 0.125;\n');
    fprintf('ROVER_WHEEL_BASE = 0.6;\n');
    fprintf('ROVER_TRACK_WIDTH = 0.5;\n');
    fprintf('ROVER_MAX_SPEED = 2.0;\n');
    fprintf('NUM_WHEELS = 4;\n');
    fprintf('SIMULATION_TIME = 30.0;\n');
    fprintf('TIME_STEP = 0.1;\n');
    fprintf('SLIP_PROBABILITY = 0.15;\n');
    fprintf('SLIP_SEVERITY = 0.3;\n');
    fprintf('FORWARD_VELOCITY = 0.5;\n');
    fprintf('VERTICAL_VELOCITY = 0.1;\n');
    fprintf('ANGULAR_VELOCITY = 0.02;\n');
    fprintf('PITCH_RATE = 0.01;\n');
    fprintf('PROCESS_NOISE_VAR = 0.01;\n');
    fprintf('MEASUREMENT_NOISE_VAR = 0.1;\n');
    fprintf('INITIAL_COVARIANCE = 0.1;\n');
    fprintf('SLIP_THRESHOLD = 0.3;\n');
    fprintf('MIN_SLIP_DURATION = 0.2;\n');
    fprintf('WHEEL_SINKAGE_FACTOR = 0.05;\n');
    fprintf('TERRAIN_TYPE = ''sandy'';\n');
    fprintf('TERRAIN_ROUGHNESS = 0.05;\n');
    fprintf('GRAVITY = 9.81;\n');
    fprintf('ATMOSPHERIC_PRESSURE = 1.0;\n');
    fprintf('DUST_STORM_FACTOR = 1.0;\n');
    fprintf('TEMPERATURE_EFFECT = 1.0;\n');
    fprintf('WHEEL_WEAR_FACTOR = 1.0;\n');
    
    fprintf('\n--- Mars Rover Example ---\n');
    fprintf('ROVER_MASS = 899.0;\n');
    fprintf('ROVER_WHEEL_RADIUS = 0.2625;\n');
    fprintf('ROVER_WHEEL_BASE = 2.7;\n');
    fprintf('ROVER_TRACK_WIDTH = 2.7;\n');
    fprintf('ROVER_MAX_SPEED = 0.042;\n');
    fprintf('NUM_WHEELS = 6;\n');
    fprintf('SIMULATION_TIME = 300.0;\n');
    fprintf('TIME_STEP = 0.1;\n');
    fprintf('SLIP_PROBABILITY = 0.25;\n');
    fprintf('SLIP_SEVERITY = 0.4;\n');
    fprintf('FORWARD_VELOCITY = 0.025;\n');
    fprintf('VERTICAL_VELOCITY = 0.005;\n');
    fprintf('ANGULAR_VELOCITY = 0.008;\n');
    fprintf('PITCH_RATE = 0.003;\n');
    fprintf('PROCESS_NOISE_VAR = 0.05;\n');
    fprintf('MEASUREMENT_NOISE_VAR = 0.15;\n');
    fprintf('INITIAL_COVARIANCE = 0.2;\n');
    fprintf('SLIP_THRESHOLD = 0.4;\n');
    fprintf('MIN_SLIP_DURATION = 0.5;\n');
    fprintf('WHEEL_SINKAGE_FACTOR = 0.15;\n');
    fprintf('TERRAIN_TYPE = ''martian_regolith'';\n');
    fprintf('TERRAIN_ROUGHNESS = 0.12;\n');
    fprintf('GRAVITY = 3.711;\n');
    fprintf('ATMOSPHERIC_PRESSURE = 0.006;\n');
    fprintf('DUST_STORM_FACTOR = 1.0;\n');
    fprintf('TEMPERATURE_EFFECT = 0.95;\n');
    fprintf('WHEEL_WEAR_FACTOR = 0.85;\n');
    
    error('Please configure all required parameters before running the simulation.');
end

fprintf('========================================================\n');
fprintf('    ROVER EKF STATE ESTIMATION SIMULATION\n');
fprintf('    User-Configured Rover Parameters\n');
fprintf('========================================================\n\n');

fprintf('Rover Configuration:\n');
fprintf('  - Mass: %.1f kg\n', ROVER_MASS);
fprintf('  - Wheel Radius: %.3f m (%.1f cm diameter)\n', ROVER_WHEEL_RADIUS, ROVER_WHEEL_RADIUS*2*100);
fprintf('  - Wheelbase: %.1f m\n', ROVER_WHEEL_BASE);
fprintf('  - Track Width: %.1f m\n', ROVER_TRACK_WIDTH);
fprintf('  - Number of Wheels: %d\n', NUM_WHEELS);
fprintf('  - Max Speed: %.3f m/s\n', ROVER_MAX_SPEED);
fprintf('  - Actual Speed: %.3f m/s\n', FORWARD_VELOCITY);
fprintf('  - Terrain Type: %s\n', TERRAIN_TYPE);
fprintf('  - Gravity: %.3f m/s²\n', GRAVITY);
fprintf('  - Simulation Time: %.1f seconds\n', SIMULATION_TIME);
fprintf('  - Time Step: %.1f seconds\n', TIME_STEP);
fprintf('\n');

%% =========================== SIMULATION SETUP ===========================

% Time vector
time_vector = 0:TIME_STEP:SIMULATION_TIME-TIME_STEP;
n_time_steps = length(time_vector);

% State Variables
% State vector: [x, y, z, phi, P_z]
% x, y, z: position coordinates in meters
% phi: orientation angle in radians
% P_z: rover pitch angle in radians (terrain-specific parameter)
n_states = 5;
true_states = zeros(n_time_steps, n_states);
estimated_states = zeros(n_time_steps, n_states);

% Control inputs (based on user configuration)
v_cmd = FORWARD_VELOCITY;        % Forward velocity command
v_z_cmd = VERTICAL_VELOCITY;     % Vertical velocity command  
omega_cmd = ANGULAR_VELOCITY;    % Angular velocity command
P_z_dot_cmd = PITCH_RATE;        % Pitch rate command

%% =========================== SLIP EVENT GENERATION ===========================

% Generate realistic slip events based on terrain type and probability
base_slip_rate = SLIP_PROBABILITY;

% Adjust slip probability based on terrain type
switch TERRAIN_TYPE
    case 'rocky'
        terrain_slip_factor = 0.7;  % Less slip on rocky terrain
    case 'sandy'
        terrain_slip_factor = 1.5;  % More slip on sandy terrain
    case 'smooth'
        terrain_slip_factor = 0.3;  % Very little slip on smooth terrain
    case 'martian_regolith'
        terrain_slip_factor = 1.8;  % High slip on fine Martian soil
    case 'rocky_mars'
        terrain_slip_factor = 1.2;  % Moderate slip on rocky Martian terrain
    case 'sandy_mars'
        terrain_slip_factor = 2.2;  % Very high slip on sandy dunes
    case 'icy_mars'
        terrain_slip_factor = 2.5;  % Extreme slip on icy polar regions
    case 'lunar_regolith'
        terrain_slip_factor = 0.8;  % Lower gravity, different slip characteristics
    otherwise
        terrain_slip_factor = 1.0;  % Default terrain
end

effective_slip_rate = base_slip_rate * terrain_slip_factor;
expected_slip_events = round(effective_slip_rate * n_time_steps);

% Generate slip events
slip_events = [];
for i = 1:expected_slip_events
    slip_time_idx = round(10 + rand() * (n_time_steps - 20));
    slip_events = [slip_events; slip_time_idx];
end
slip_events = unique(slip_events);

fprintf('Slip Event Generation:\n');
fprintf('  - Terrain Type: %s (factor: %.1f)\n', TERRAIN_TYPE, terrain_slip_factor);
fprintf('  - Expected Slip Events: %d\n', expected_slip_events);
fprintf('  - Generated Slip Events: %d\n', length(slip_events));
fprintf('  - Slip Times: ');
for i = 1:length(slip_events)
    fprintf('%.1f ', time_vector(slip_events(i)));
end
fprintf('seconds\n\n');

%% =========================== EKF INITIALIZATION ===========================

% Initial state
x_est = [0; 0; 0; 0; 0];              % Estimated state
P = eye(n_states) * INITIAL_COVARIANCE; % State covariance matrix

% Process noise covariance (Q matrix)
Q = eye(n_states) * PROCESS_NOISE_VAR;

% Measurement noise covariance (R matrix)
R = eye(n_states) * MEASUREMENT_NOISE_VAR;

% Storage for slip detection
slip_detected = zeros(n_time_steps, 1);
innovation_magnitude = zeros(n_time_steps, 1);
slip_times = [];

fprintf('EKF Initialization Complete.\n');
fprintf('Starting simulation...\n\n');

%% =========================== MAIN SIMULATION LOOP ===========================

for k = 1:n_time_steps
    %% Generate True State Trajectory
    if k == 1
        true_states(k, :) = [0, 0, 0, 0, 0];
    else
        % Check if slip occurs at this time step
        slip_factor = 1.0;
        if ismember(k, slip_events)
            slip_factor = SLIP_SEVERITY;  % Reduced motion during slip
            slip_times = [slip_times; k];
        end
        
        % Add terrain roughness effect
        roughness_factor = 1.0 + (rand() - 0.5) * TERRAIN_ROUGHNESS;
        
        % Mars environmental effects
        dust_effect = DUST_STORM_FACTOR;
        temp_effect = TEMPERATURE_EFFECT;
        wear_effect = WHEEL_WEAR_FACTOR;
        
        % Gravity effect on traction (Mars vs Earth)
        gravity_traction_factor = GRAVITY / 9.81;  % Reduced traction on Mars due to lower gravity
        
        % Wheel sinkage effect (6-wheeled rocker-bogie system distributes load)
        sinkage_effect = 1.0 - (WHEEL_SINKAGE_FACTOR * slip_factor / NUM_WHEELS);
        
        % Combined effective velocity (6-wheeled Mars rover dynamics)
        v_effective = v_cmd * slip_factor * roughness_factor * dust_effect * temp_effect * wear_effect * gravity_traction_factor * sinkage_effect;
        
        % State transition model (rover kinematics)
        true_states(k, 1) = true_states(k-1, 1) + TIME_STEP * v_effective * cos(true_states(k-1, 4));
        true_states(k, 2) = true_states(k-1, 2) + TIME_STEP * v_effective * sin(true_states(k-1, 4));
        true_states(k, 3) = true_states(k-1, 3) + TIME_STEP * v_z_cmd;
        true_states(k, 4) = true_states(k-1, 4) + TIME_STEP * omega_cmd;
        true_states(k, 5) = true_states(k-1, 5) + TIME_STEP * P_z_dot_cmd;
    end
    
    %% EKF Prediction Step
    if k > 1
        % State prediction using control inputs
        x_pred = x_est;
        x_pred(1) = x_est(1) + TIME_STEP * v_cmd * cos(x_est(4));
        x_pred(2) = x_est(2) + TIME_STEP * v_cmd * sin(x_est(4));
        x_pred(3) = x_est(3) + TIME_STEP * v_z_cmd;
        x_pred(4) = x_est(4) + TIME_STEP * omega_cmd;
        x_pred(5) = x_est(5) + TIME_STEP * P_z_dot_cmd;
        
        % Jacobian of state transition (F matrix)
        F = eye(n_states);
        F(1, 4) = -TIME_STEP * v_cmd * sin(x_est(4));
        F(2, 4) = TIME_STEP * v_cmd * cos(x_est(4));
        
        % Covariance prediction
        P = F * P * F' + Q;
        
        x_est = x_pred;
    end
    
    %% Generate Noisy Measurement
    measurement_noise = mvnrnd(zeros(n_states, 1), R)';
    z = true_states(k, :)' + measurement_noise;
    
    %% EKF Update Step
    % Measurement model (direct observation)
    H = eye(n_states);
    
    % Innovation (residual)
    y = z - H * x_est;
    innovation_magnitude(k) = norm(y);
    
    % Innovation covariance
    S = H * P * H' + R;
    
    % Kalman gain
    K = P * H' / S;
    
    % State update
    x_est = x_est + K * y;
    
    % Covariance update (Joseph form for numerical stability)
    P = (eye(n_states) - K * H) * P;
    
    %% Store Results
    estimated_states(k, :) = x_est';
    
    %% Slip Detection Algorithm
    if innovation_magnitude(k) > SLIP_THRESHOLD
        slip_detected(k) = 1;
    end
end

%% =========================== PERFORMANCE ANALYSIS ===========================

actual_slip_events = length(slip_times);
detected_slip_events = sum(slip_detected);

% Calculate detection metrics
if actual_slip_events > 0
    true_positives = 0;
    for i = 1:length(slip_times)
        slip_idx = slip_times(i);
        if slip_idx <= length(slip_detected) && slip_detected(slip_idx) == 1
            true_positives = true_positives + 1;
        end
    end
    detection_rate = (true_positives / actual_slip_events) * 100;
else
    detection_rate = 0;
end

false_alarm_rate = (detected_slip_events / n_time_steps) * 100;

% Calculate estimation accuracy
position_error = sqrt(sum((true_states(:, 1:3) - estimated_states(:, 1:3)).^2, 2));
mean_position_error = mean(position_error);
rms_position_error = sqrt(mean(position_error.^2));

fprintf('==========================================================\n');
fprintf('EKF MARS ROVER SIMULATION RESULTS\n');
fprintf('==========================================================\n');
fprintf('Rover Configuration:\n');
fprintf('  - Terrain Type: %s\n', TERRAIN_TYPE);
fprintf('  - Mass: %.1f kg\n', ROVER_MASS);
fprintf('  - Wheel Radius: %.3f m\n', ROVER_WHEEL_RADIUS);
fprintf('  - Forward Speed: %.2f m/s\n', FORWARD_VELOCITY);
fprintf('\nSimulation Parameters:\n');
fprintf('  - Duration: %.1f seconds\n', SIMULATION_TIME);
fprintf('  - Time Steps: %d\n', n_time_steps);
fprintf('  - Update Rate: %.1f Hz\n', 1/TIME_STEP);
fprintf('\nSlip Detection Performance:\n');
fprintf('  - Actual Slip Events: %d\n', actual_slip_events);
fprintf('  - Detected Slip Events: %d\n', detected_slip_events);
fprintf('  - Detection Rate: %.1f%%\n', detection_rate);
fprintf('  - False Alarm Rate: %.1f%%\n', false_alarm_rate);
fprintf('\nEstimation Accuracy:\n');
fprintf('  - Mean Position Error: %.4f m\n', mean_position_error);
fprintf('  - RMS Position Error: %.4f m\n', rms_position_error);
fprintf('==========================================================\n\n');

%% =========================== VISUALIZATION ===========================

if SAVE_PLOTS
    fprintf('Generating research paper plots...\n');
    
    % Main EKF State Estimation Plot (Research Paper Format)
    figure('Position', [100, 100, 800, 1000]);
    
    % State labels
    state_labels = {'x (m)', 'y (m)', 'z (m)', 'φ (rad)', 'P_z (rad)'};
    
    % Find slip detected times for plotting
    slip_detected_times = find(slip_detected == 1);
    
    for i = 1:n_states
        subplot(5, 1, i);
        
        % Plot true state (red solid line)
        plot(time_vector, true_states(:, i), 'r-', 'LineWidth', 2, 'DisplayName', 'True State');
        hold on;
        
        % Plot estimated state (blue dashed line)
        plot(time_vector, estimated_states(:, i), 'b--', 'LineWidth', 2, 'DisplayName', 'Estimated State');
        
        % Mark slip detected points (black circles)
        if ~isempty(slip_detected_times)
            for j = 1:length(slip_detected_times)
                idx = slip_detected_times(j);
                if idx <= length(time_vector)
                    plot(time_vector(idx), true_states(idx, i), 'ko', 'MarkerSize', 8, 'MarkerFaceColor', 'k');
                    if j == 1 && i == 1  % Add legend only once
                        plot(time_vector(idx), true_states(idx, i), 'ko', 'MarkerSize', 8, 'MarkerFaceColor', 'k', 'DisplayName', 'Slip Detected');
                    end
                end
            end
        end
        
        % Formatting to match research paper
        ylabel(state_labels{i}, 'FontSize', 12, 'FontWeight', 'bold');
        grid on;
        xlim([0, SIMULATION_TIME]);
        
        % Set y-axis limits based on data range
        y_range = max(true_states(:, i)) - min(true_states(:, i));
        if y_range > 0
            ylim([min(true_states(:, i)) - 0.1*y_range, max(true_states(:, i)) + 0.1*y_range]);
        end
        
        % Legend on first subplot
        if i == 1
            legend('FontSize', 10);
        end
        
        % X-axis label only on bottom subplot
        if i == n_states
            xlabel('Time (seconds)', 'FontSize', 12, 'FontWeight', 'bold');
        end
    end
    
    % Main title
    if exist('OCTAVE_VERSION', 'builtin')
        % Octave workaround for sgtitle
        axes('Position', [0 0 1 1], 'Visible', 'off');
        title_str = sprintf('Mars Rover EKF State Estimation - %s Terrain', upper(TERRAIN_TYPE));
        text(0.5, 0.95, title_str, 'FontSize', 16, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
    else
        title_str = sprintf('Mars Rover EKF State Estimation - %s Terrain', upper(TERRAIN_TYPE));
        sgtitle(title_str, 'FontSize', 16, 'FontWeight', 'bold');
    end
    
    % Save the plot
    print('-dpng', sprintf('-r%d', PLOT_RESOLUTION), 'mars_rover_ekf_estimation.png');
    fprintf('Main plot saved as mars_rover_ekf_estimation.png\n');
    
    % If running in Octave, also try to save as PDF
    if exist('OCTAVE_VERSION', 'builtin')
        try
            print('-dpdf', 'mars_rover_ekf_estimation.pdf');
            fprintf('Plot also saved as mars_rover_ekf_estimation.pdf\n');
        catch
            fprintf('PDF save failed (normal in some Octave installations)\n');
        end
    end
    
    if SHOW_ANALYSIS
        % Additional Analysis Plot
        figure('Position', [200, 200, 1000, 800]);
        
        % Innovation magnitude and slip detection
        subplot(2, 3, 1);
        plot(time_vector, innovation_magnitude, 'g-', 'LineWidth', 1.5);
        hold on;
        plot([0, SIMULATION_TIME], [SLIP_THRESHOLD, SLIP_THRESHOLD], 'r--', 'LineWidth', 2);
        xlabel('Time (s)');
        ylabel('Innovation Magnitude');
        title('Slip Detection via Innovation');
        legend('Innovation', 'Threshold', 'Location', 'northeast');
        grid on;
        
        % Position tracking
        subplot(2, 3, 2);
        plot(time_vector, true_states(:, 1), 'r-', time_vector, estimated_states(:, 1), 'b--', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('X Position (m)');
        title('X Position Tracking');
        legend('True', 'Estimated', 'Location', 'northeast');
        grid on;
        
        subplot(2, 3, 3);
        plot(time_vector, true_states(:, 2), 'r-', time_vector, estimated_states(:, 2), 'b--', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('Y Position (m)');
        title('Y Position Tracking');
        legend('True', 'Estimated', 'Location', 'northeast');
        grid on;
        
        % Estimation error
        subplot(2, 3, 4);
        plot(time_vector, position_error, 'm-', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('Position Error (m)');
        title('Position Estimation Error');
        grid on;
        
        % Rover trajectory
        subplot(2, 3, 5);
        plot(true_states(:, 1), true_states(:, 2), 'r-', 'LineWidth', 2);
        hold on;
        plot(estimated_states(:, 1), estimated_states(:, 2), 'b--', 'LineWidth', 2);
        xlabel('X Position (m)');
        ylabel('Y Position (m)');
        title('Rover Trajectory');
        legend('True Path', 'Estimated Path', 'Location', 'northeast');
        grid on;
        axis equal;
        
        % Slip event timeline
        subplot(2, 3, 6);
        slip_timeline = zeros(size(time_vector));
        slip_timeline(slip_events) = 1;
        detect_timeline = slip_detected;
        
        plot(time_vector, slip_timeline, 'r-', 'LineWidth', 2);
        hold on;
        plot(time_vector, detect_timeline, 'b--', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('Slip Event');
        title('Slip Events vs Detection');
        legend('Actual Slip', 'Detected Slip', 'Location', 'northeast');
        grid on;
        ylim([-0.1, 1.1]);
        
        if exist('OCTAVE_VERSION', 'builtin')
            % Octave workaround for sgtitle
            axes('Position', [0 0 1 1], 'Visible', 'off');
            analysis_title = sprintf('Mars Rover EKF Performance Analysis - %s Terrain', upper(TERRAIN_TYPE));
            text(0.5, 0.95, analysis_title, 'FontSize', 14, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
        else
            analysis_title = sprintf('Mars Rover EKF Performance Analysis - %s Terrain', upper(TERRAIN_TYPE));
            sgtitle(analysis_title, 'FontSize', 14, 'FontWeight', 'bold');
        end
        
        print('-dpng', sprintf('-r%d', PLOT_RESOLUTION), 'mars_rover_ekf_analysis.png');
        fprintf('Analysis plot saved as mars_rover_ekf_analysis.png\n');
    end
end

fprintf('\nSimulation complete!\n');
fprintf('Files saved in matlab/ directory.\n');
fprintf('Research paper format plots generated successfully.\n\n');

%% =========================== RESEARCH NOTES ===========================
% This simulation is designed for Mars rover slip detection research
% 
% Key Research Parameters:
% - Terrain Type: Affects slip probability and rover dynamics
% - Slip Severity: Models different levels of wheel slippage
% - Innovation Threshold: Critical for slip detection sensitivity
% - Process/Measurement Noise: Represents sensor and model uncertainties
% 
% Applications:
% - Single-wheel test bench validation
% - Slip detection algorithm development
% - EKF parameter tuning for Mars rovers
% - Terrain-specific navigation strategies
% 
% For different rover configurations, modify the USER CONFIGURATION section
% at the top of this file. 