#ifndef PIDController_H
#define PIDController_H

class PID {
public:
    PID(double kp, double ki, double kd, double setpoint);
    void setTunings(double kp, double ki, double kd);
    void setSetpoint(double setpoint);
    void setOutputLimits(double min, double max);
    void isYawFn(bool yn);
    double compute(double input);

private:
    double kp, ki, kd;
    double setpoint;
    double outputMin, outputMax;
    double prevError, integral, lastTime;
    double sampleTime;
    bool isYaw;
};

#endif // PIDController_H