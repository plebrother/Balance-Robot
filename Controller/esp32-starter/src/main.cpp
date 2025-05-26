// 继续调或者不要outerloop(就可以用更稳定的balance,还是说都可以用？) //p should be close to 0
//correct speedCmPerSecond; deg to speed; stop turning ocasionally; why chrono works and micros() doesn't
#include <Arduino.h>
#include <SPI.h>
#include <TimerInterrupt_Generic.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <step.h>
#include "PIDController.h" 

// === PIN DEFINITIONS ===
#define STEPPER1_DIR_PIN  16
#define STEPPER1_STEP_PIN 17
#define STEPPER2_DIR_PIN  4
#define STEPPER2_STEP_PIN 14
#define STEPPER_EN_PIN    15
#define TOGGLE_PIN        32

// === CONSTANTS ===
const int PRINT_INTERVAL = 500;
const int LOOP_INTERVAL = 10;
const int STEPPER_INTERVAL_US = 20;
const float kx = 20.0;
const float VREF = 4.096;

const float alpha = 0.98;
const float alphaEMA = 0.1;

const float wheelDiameter = 6.7;
const float wheelCircumference = PI * wheelDiameter;
const int stepsPerRevolution = 200 * 16;
const float trackWidth = 12.4;

const float vDesired = 30; //adjust to close to speedCmPerSecond
//const float dbcompensation = 70;  // Minimum speed in rad/s to prevent stalling

// === OBJECTS ===
ESP32Timer ITimer(3);
Adafruit_MPU6050 mpu;

step step1(STEPPER_INTERVAL_US, STEPPER1_STEP_PIN, STEPPER1_DIR_PIN);
step step2(STEPPER_INTERVAL_US, STEPPER2_STEP_PIN, STEPPER2_DIR_PIN);

PID balancePid(9000,5,50,0);//(9000, 5, 30, 0); //(9000, 17, 80, 0); //adjust
PID speedPid(1, 6, 1, vDesired); // (1.0, 0.38, 0.23, 0); //adjust 0.38 1 以及 下面的2个
PID yawPid(3.0, 0.0, 0.0, 0.0);

// === GLOBAL STATE ===
float filteredAngle = 0.0, previousFilteredAngle = 0.0;
float emaSpeed1 = 0.0, emaSpeed2 = 0.0;
float speedCmPerSecond = 0.0;
float speedCmPerSecond1 = 0.0, speedCmPerSecond2 = 0.0;
float rotationalSpeedRadPerSecond = 0.0;
float turnSetpoint = 0.0;
// const float deadBand = 1;
bool motorsEnabled = true;

static unsigned long startTime = millis(); // for testing

// === ISR ===
bool IRAM_ATTR TimerHandler(void *timerNo) {
  static bool toggle = false;
  step1.runStepper();
  step2.runStepper();
  digitalWrite(TOGGLE_PIN, toggle);
  toggle = !toggle;
  return true;
}

// === SETUP ===
void setup() {
  Serial.begin(115200);
  pinMode(TOGGLE_PIN, OUTPUT);

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1){
      delay(10);
    };
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);

  if (!ITimer.attachInterruptInterval(STEPPER_INTERVAL_US, TimerHandler)) {
    Serial.println("Failed to start stepper interrupt");
    while (1) delay(10);
  }
  Serial.println("Initialised Interrupt for Stepper");

  step1.setAccelerationRad(10.0); //adjust
  step2.setAccelerationRad(10.0);
  
  pinMode(STEPPER_EN_PIN, OUTPUT);
  digitalWrite(STEPPER_EN_PIN, false);  // Enable motors

  //Set up ADC and SPI
  /*pinMode(ADC_CS_PIN, OUTPUT);
  digitalWrite(ADC_CS_PIN, HIGH);
  SPI.begin(ADC_SCK_PIN, ADC_MISO_PIN, ADC_MOSI_PIN, ADC_CS_PIN);*/

  yawPid.isYawFn(true);

}

// === LOOP ===
void loop() {
  static unsigned long printTimer = 0;
  static unsigned long loopTimer = 0;

  if (millis() > loopTimer) {

    loopTimer += LOOP_INTERVAL;

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    float pitch = atan2(a.acceleration.z, a.acceleration.x ) ;//- 1.2*PI/180; //could add bias
    //delay(300);
    float gyroPitchRate = g.gyro.y; //
    //Serial.println(g.gyro.z);
    float dt = LOOP_INTERVAL / 1000.0;

    filteredAngle = (1 - alpha) * pitch + alpha * (gyroPitchRate * dt + previousFilteredAngle);
    previousFilteredAngle = filteredAngle;

    float rawSpeed1 = step1.getSpeed() / 2000.0;
    Serial.print("raw speed: ");
    Serial.println(rawSpeed1);
    float rawSpeed2 = step2.getSpeed() / 2000.0;
    // Serial.println(rawSpeed1);
    emaSpeed1 = alphaEMA * rawSpeed1 + (1 - alphaEMA) * emaSpeed1;
    emaSpeed2 = alphaEMA * rawSpeed2 + (1 - alphaEMA) * emaSpeed2;

    float avgSpeed = (emaSpeed1 - emaSpeed2) / 2.0;
    float distancePerStep = wheelCircumference / stepsPerRevolution;
    speedCmPerSecond = avgSpeed * distancePerStep;

    speedCmPerSecond1 = emaSpeed1 * distancePerStep;
    speedCmPerSecond2 = emaSpeed2 * distancePerStep;
    rotationalSpeedRadPerSecond = (speedCmPerSecond1 + speedCmPerSecond2) / trackWidth;

    // === Outer loop: velocity PID ===
    
    speedPid.setSetpoint(vDesired);
    float speedOutput = speedPid.compute(speedCmPerSecond) ; 
    Serial.print("speed: ");
    Serial.println(speedOutput);

    

    /*float targetPitch = 0;
    if(vDesired < 0){ // vDesired = +2 or -2
       targetPitch = (speedOutput - 100) * 0.0006; //adjust
    }
    else{
       targetPitch = (speedOutput + 100) * 0.0006;
    } // adjust*/

    double targetPitch = speedOutput * 0.0003; 
    //targetPitch = -0.05; //skip pid
    balancePid.setSetpoint(targetPitch); // targetPitch is in rad. make targetPitch + 0.2rad or -0.2rad (let vDesired=1)
    //balancePid.setSetpoint(0);

    

    targetPitch = constrain(targetPitch, -0.3, 0.3);  // ±18 degrees
    

    Serial.print("targetPitch: ");
    Serial.println(targetPitch);

    Serial.print("filteredAngle: ");
    Serial.println(filteredAngle);

    float balanceOutput = balancePid.compute(filteredAngle) ;
    Serial.print("balance: ");
    Serial.println(balanceOutput);

    float yawCorrection = yawPid.compute(rotationalSpeedRadPerSecond);

    //if (abs(balanceOutput) < deadBand) balanceOutput = 0;
    // Apply deadband compensation to prevent motor stall
    
    //if (abs(balanceOutput) > 79 ) {
      //balanceOutput = copysign(dbcompensation, balanceOutput);
    //}

    step1.setAccelerationRad(-balanceOutput - turnSetpoint + yawCorrection);
    step2.setAccelerationRad(balanceOutput - turnSetpoint + yawCorrection);

    Serial.print("speedCmPerSecond: ");
    Serial.println(speedCmPerSecond);
    if (balanceOutput > 0) { // for pitch direction check
      step1.setTargetSpeedRad (-30.0); //can never reach, just to make it move or proportional to vDesired
      step2.setTargetSpeedRad(30.0);
    } else {
      step1.setTargetSpeedRad(30.0);
      step2.setTargetSpeedRad(-30.0);
    }
    
    //Serial.print(" | speedOut: ");
    //Serial.println(speedOutput);



    Serial.print(" | speedOut: ");
    Serial.println(speedOutput);

    //if (millis() - startTime > 1000) {
      //speedPid.setSetpoint(-0.02);  // Stop after 1 second
    //}

    

    //if (millis() - startTime > 2) {  // 1000 ms = 1 second
      //balancePid.setSetpoint(-0.02);  // Stop movement(adjust angle)
    //} // for testing
  }

  if (millis() > printTimer) {
  
    printTimer += PRINT_INTERVAL;
    Serial.print("Angle: ");
    Serial.print(filteredAngle * 180 / PI);
    Serial.print(" | Speed: ");
    Serial.print(speedCmPerSecond);
    Serial.print(" | Rotation: ");
    Serial.println(rotationalSpeedRadPerSecond);
    
  }
}

