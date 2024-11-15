#include "HX711.h"

// Motor A connections for L298N motor driver
int enA = 6;      // PWM pin for speed control
int in1 = 7;      // Direction control pin
int in2 = 8;      // Direction control pin

// Encoder connections
#define ENCODER_A 4  // Interrupt-capable pin on the Mega for Channel A
#define ENCODER_B 5  // Pin for Channel B

// Load Cell HX711 connections
const int LOADCELL_DOUT_PIN = 2;  // DOUT from HX711
const int LOADCELL_SCK_PIN = 3;   // SCK from HX711

HX711 scale;

// Current Sensor ACS712 connection
const int CURRENT_SENSOR_PIN = A0;

// Variables to track encoder counts and motor speed
volatile long encoderCount = 0;
volatile long lastEncoderCount = 0;
volatile bool direction = true;  // true = forward, false = reverse

// Constant motor speed (PWM value: 0 to 255)
const int MOTOR_SPEED = 150; // Adjust as needed for your application

// Timer variables
unsigned long lastToggleTime = 0; // Time of the last direction change
unsigned long lastDataTime = 0;   // Time of the last data collection
const unsigned long toggleInterval = 5000; // 5 seconds in milliseconds
const unsigned long dataInterval = 100;    // 100ms data collection interval
bool motorDirectionForward = true; // Start with forward direction

// Data collection variables
unsigned long testStartTime = 0;
long expectedRotation = 0;
float slipPercentage = 0.0;
bool dataLogging = true;

// Calibration constants (adjust based on your setup)
const float LOAD_CELL_CALIBRATION = 1.0; // Calibration factor for load cell
const float CURRENT_SENSOR_ZERO = 512.0; // Zero current reading (adjust for your sensor)
const float CURRENT_SENSOR_SENSITIVITY = 0.1; // Sensitivity in A/ADC unit

// Test configuration
const int TEST_DURATION = 30000; // 30 seconds test duration (0 = infinite)
const bool ENABLE_SLIP_DETECTION = true;
const float SLIP_THRESHOLD = 5.0; // Slip threshold percentage

void setup() {
  Serial.begin(57600);  // Initialize Serial Monitor
  
  // Wait for serial connection
  while (!Serial) {
    delay(10);
  }
  
  // Print CSV header
  printCSVHeader();
  
  // Motor setup
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  
  // Initialize motor in a stopped state
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  
  // Encoder setup
  pinMode(ENCODER_A, INPUT);
  pinMode(ENCODER_B, INPUT);
  
  // Attach interrupts to encoder Channel A
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, CHANGE);

  // Load cell setup
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(LOAD_CELL_CALIBRATION);
  scale.tare(); // Reset the scale to 0
  
  // Initialize test start time
  testStartTime = millis();
  lastDataTime = testStartTime;
  
  Serial.println("# Test bench initialized. Starting data collection...");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if test duration is complete
  if (TEST_DURATION > 0 && (currentTime - testStartTime) > TEST_DURATION) {
    stopTest();
    return;
  }

  // Toggle motor direction every 5 seconds
  if (currentTime - lastToggleTime >= toggleInterval) {
    motorDirectionForward = !motorDirectionForward; // Switch direction
    lastToggleTime = currentTime; // Reset the timer
    
    // Log direction change
    Serial.print("# Direction changed to: ");
    Serial.println(motorDirectionForward ? "Forward" : "Reverse");
  }

  // Run the motor at constant speed in the current direction
  runMotorConstantSpeed(motorDirectionForward);
  
  // Collect and log data at specified intervals
  if (currentTime - lastDataTime >= dataInterval) {
    collectAndLogData(currentTime);
    lastDataTime = currentTime;
  }
  
  // Check for slip detection
  if (ENABLE_SLIP_DETECTION && abs(slipPercentage) > SLIP_THRESHOLD) {
    Serial.print("# SLIP DETECTED! Slip percentage: ");
    Serial.print(slipPercentage);
    Serial.println("%");
  }
}

void printCSVHeader() {
  Serial.println("# Mars Rover Single Wheel Test Bench Data");
  Serial.println("# Timestamp(ms),ElapsedTime(ms),EncoderCount,ExpectedRotation,SlipPercentage,Direction,LoadCellReading,CurrentSensor,MotorCurrent(A),Comments");
}

void collectAndLogData(unsigned long currentTime) {
  // Calculate elapsed time
  unsigned long elapsedTime = currentTime - testStartTime;
  
  // Calculate expected rotation based on time and motor speed
  // This is a simplified calculation - adjust based on your wheel specifications
  long timeDelta = currentTime - lastDataTime;
  long expectedDelta = (long)((float)timeDelta * MOTOR_SPEED / 255.0 * 0.1); // Simplified calculation
  expectedRotation += motorDirectionForward ? expectedDelta : -expectedDelta;
  
  // Calculate slip percentage
  if (expectedRotation != 0) {
    slipPercentage = ((float)(expectedRotation - encoderCount) / (float)abs(expectedRotation)) * 100.0;
  } else {
    slipPercentage = 0.0;
  }
  
  // Read sensors
  long loadCellReading = 0;
  if (scale.is_ready()) {
    loadCellReading = scale.read();
  }
  
  int currentSensorRaw = analogRead(CURRENT_SENSOR_PIN);
  float motorCurrent = (currentSensorRaw - CURRENT_SENSOR_ZERO) * CURRENT_SENSOR_SENSITIVITY;
  
  // Print data in CSV format
  Serial.print(currentTime);
  Serial.print(",");
  Serial.print(elapsedTime);
  Serial.print(",");
  Serial.print(encoderCount);
  Serial.print(",");
  Serial.print(expectedRotation);
  Serial.print(",");
  Serial.print(slipPercentage, 2);
  Serial.print(",");
  Serial.print(motorDirectionForward ? "1" : "0");
  Serial.print(",");
  Serial.print(loadCellReading);
  Serial.print(",");
  Serial.print(currentSensorRaw);
  Serial.print(",");
  Serial.print(motorCurrent, 3);
  Serial.print(",");
  
  // Add comments for special conditions
  if (abs(slipPercentage) > SLIP_THRESHOLD) {
    Serial.print("SLIP_DETECTED");
  } else if (abs(currentTime - lastToggleTime) < 200) {
    Serial.print("DIRECTION_CHANGE");
  } else {
    Serial.print("NORMAL");
  }
  
  Serial.println();
}

// Function to run the motor at a constant speed
void runMotorConstantSpeed(bool forward) {
  analogWrite(enA, MOTOR_SPEED); // Set motor speed to constant value
  
  if (forward) {
    // Forward direction
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  } else {
    // Reverse direction
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  }
}

// Function to stop the test
void stopTest() {
  // Stop the motor
  analogWrite(enA, 0);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  
  Serial.println("# Test completed!");
  Serial.print("# Total encoder count: ");
  Serial.println(encoderCount);
  Serial.print("# Final slip percentage: ");
  Serial.print(slipPercentage, 2);
  Serial.println("%");
  
  // Stop further execution
  while (true) {
    delay(1000);
  }
}

// Interrupt Service Routine (ISR) for the encoder Channel A
void encoderISR() {
  // Read Channel B to determine direction
  direction = (digitalRead(ENCODER_A) == digitalRead(ENCODER_B));
  
  // Update encoder count based on direction
  if (direction) {
    encoderCount++;
  } else {
    encoderCount--;
  }
} 