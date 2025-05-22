#include "PIDController.h"
#include <algorithm>
#include <chrono>
#include <cmath>

using namespace std::chrono;

PID::PID(double kp, double ki, double kd, double setpoint)
    : kp(kp), ki(ki), kd(kd), setpoint(setpoint),
      outputMin(-80.0), outputMax(80.0),
      prevError(0.0), integral(0.0),
      sampleTime(0.01), isYaw(false)
{
    lastTime = duration<double>(system_clock::now().time_since_epoch()).count();
}

void PID::setTunings(double kp, double ki, double kd) {
    this->kp = kp; this->ki = ki; this->kd = kd;
}

void PID::setSetpoint(double setpoint) {
    this->setpoint = setpoint;
}

void PID::setOutputLimits(double min, double max) {
    if (min >= max) return;
    outputMin = min; outputMax = max;
}

void PID::isYawFn(bool yn) {
    isYaw = yn;
}

double PID::compute(double input) {
    double currentTime = duration<double>(system_clock::now().time_since_epoch()).count();
    double dt = currentTime - lastTime;
    if (dt <= 0.0) dt = 1e-3;

    double error = setpoint - input;
    if (isYaw) {
        if (error > M_PI) error -= 2 * M_PI;
        else if (error < -M_PI) error += 2 * M_PI;
    }

    integral += error * dt;
    double derivative = (error - prevError) / dt;
    double output = kp * error + ki * integral + kd * derivative;

    output = std::max(outputMin, std::min(output, outputMax));
    prevError = error;
    lastTime = currentTime;

    return output;
}
