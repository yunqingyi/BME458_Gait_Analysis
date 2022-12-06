/*
  Gait Analysis Arduino Firmware

  Digital input for 4 pressure sensors
  Analog input for 2 EMG channels
  I2C for 2 accelerometers
  On serial port print each set of data out in a single line, separated by commas.

  modified 29 Nov 2022
  by Tim Shi, Grace Yi
*/

#include "Wire.h" // This library allows you to communicate with I2C devices.

#define SYSTEM_FREQUENCY 100
#define ACCE_CALI_COEFF_X 1.0f*9.8f/15000
#define ACCE_CALI_COEFF_Y 1.0f*9.8f/15000
#define ACCE_CALI_COEFF_Z 1.0f*9.8f/15000
#define PRESSURE_THRESH 200


const int emg_L_pin = A0;
const int emg_R_pin = A1;
const int emg_calibrate_pin = 4;

const int pressure_L_F_pin = A2;
const int pressure_L_B_pin = A3;
const int pressure_R_F_pin = A4;
const int pressure_R_B_pin = A5;

const int pressure_L_F_pin_digi = 12;
const int pressure_L_B_pin_digi = 13;
const int pressure_R_F_pin_digi = 7;
const int pressure_R_B_pin_digi = 8;
const int velocity_calibrate_pin = 4;



float vel_cal_x_l = 0.0;
float vel_cal_y_l = 0.0;
float vel_cal_z_l = 0.0;
float vel_cal_x_r = 0.0;
float vel_cal_y_r = 0.0;
float vel_cal_z_r = 0.0;

int emg_cal_l = 0;
int emg_cal_r = 0;


//send to PC
int pressure_L_F = 0;
int pressure_L_B = 0;
int pressure_R_F = 0;
int pressure_R_B = 0;
int emg_L = 0;
int emg_R = 0;
float vel_L_X = 0.0;
float vel_L_Z = 0.0;
float vel_R_X = 0.0;
float vel_R_Z = 0.0;
int avg_emg_L = 0.0;
int avg_emg_R = 0.0;


// Accelerometer initialization

const int MPU_ADDR_L = 0x68; // I2C address of the MPU-6050. If AD0 pin is set to HIGH, the I2C address will be 0x69.
const int MPU_ADDR_R = 0x69; // I2C address of the MPU-6050. If AD0 pin is set to HIGH, the I2C address will be 0x69.

int16_t raw_acc_x_l, raw_acc_y_l, raw_acc_z_l; // variables for accelerometer raw data
float acc_x_l, acc_y_l, acc_z_l;
float pre_acc_x_l, pre_acc_y_l, pre_acc_z_l;
float vel_x_l, vel_y_l, vel_z_l;

int16_t raw_acc_x_r, raw_acc_y_r, raw_acc_z_r; // variables for accelerometer raw data
float acc_x_r, acc_y_r, acc_z_r;
float pre_acc_x_r, pre_acc_y_r, pre_acc_z_r;
float vel_x_r, vel_y_r, vel_z_r;

// int16_t gyro_x, gyro_y, gyro_z; // variables for gyro raw data
// int16_t temperature; // variables for temperature data

void acceInit(){
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR_L); // Begins a transmission to the I2C slave (GY-521 board)
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  Wire.begin();
  Wire.beginTransmission(MPU_ADDR_R); // Begins a transmission to the I2C slave (GY-521 board)
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);


}

void acceRead(){

  Wire.beginTransmission(MPU_ADDR_L);
  Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H) [MPU-6000 and MPU-6050 Register Map and Descriptions Revision 4.2, p.40]
  Wire.endTransmission(false); // the parameter indicates that the Arduino will send a restart. As a result, the connection is kept active.
  Wire.requestFrom(MPU_ADDR_L, 3*2, true); // request a total of 7*2=14 registers
  
  // "Wire.read()<<8 | Wire.read();" means two registers are read and stored in the same variable
  raw_acc_x_l = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  raw_acc_y_l = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  raw_acc_z_l = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)

  pre_acc_x_l = acc_x_l;
  pre_acc_y_l = acc_y_l;
  pre_acc_z_l = acc_z_l;
  acc_x_l = raw_acc_x_l*ACCE_CALI_COEFF_X;
  acc_y_l = raw_acc_y_l*ACCE_CALI_COEFF_Y;
  acc_z_l = raw_acc_z_l*ACCE_CALI_COEFF_Z;

  Wire.beginTransmission(MPU_ADDR_R);
  Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H) [MPU-6000 and MPU-6050 Register Map and Descriptions Revision 4.2, p.40]
  Wire.endTransmission(false); // the parameter indicates that the Arduino will send a restart. As a result, the connection is kept active.
  Wire.requestFrom(MPU_ADDR_R, 3*2, true); // request a total of 7*2=14 registers
  
  // "Wire.read()<<8 | Wire.read();" means two registers are read and stored in the same variable
  raw_acc_x_r = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  raw_acc_y_r = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  raw_acc_z_r = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)

  pre_acc_x_r = acc_x_r;
  pre_acc_y_r = acc_y_r;
  pre_acc_z_r = acc_z_r;
  acc_x_r = raw_acc_x_r*ACCE_CALI_COEFF_X;
  acc_y_r = raw_acc_y_r*ACCE_CALI_COEFF_Y;
  acc_z_r = raw_acc_z_r*ACCE_CALI_COEFF_Z;

  if(digitalRead(velocity_calibrate_pin)){
    vel_cal_x_l = vel_x_l;
    vel_cal_y_l = vel_y_l;
    vel_cal_z_l = vel_z_l;
    vel_cal_x_r = vel_x_r;
    vel_cal_y_r = vel_y_r;
    vel_cal_z_r = vel_z_r;
  }


  /** We don't use the gyro and temperature info
  temperature = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 (TEMP_OUT_H) and 0x42 (TEMP_OUT_L)
  gyro_x = Wire.read()<<8 | Wire.read(); // reading registers: 0x43 (GYRO_XOUT_H) and 0x44 (GYRO_XOUT_L)
  gyro_y = Wire.read()<<8 | Wire.read(); // reading registers: 0x45 (GYRO_YOUT_H) and 0x46 (GYRO_YOUT_L)
  gyro_z = Wire.read()<<8 | Wire.read(); // reading registers: 0x47 (GYRO_ZOUT_H) and 0x48 (GYRO_ZOUT_L)
  **/
}

void velocityUpdate(){
  vel_x_l+=(acc_x_l-pre_acc_x_l)/SYSTEM_FREQUENCY;
  vel_y_l+=(acc_y_l-pre_acc_y_l)/SYSTEM_FREQUENCY;
  vel_z_l+=(acc_z_l-pre_acc_z_l)/SYSTEM_FREQUENCY;

  vel_x_r+=(acc_x_r-pre_acc_x_r)/SYSTEM_FREQUENCY;
  vel_y_r+=(acc_y_r-pre_acc_y_r)/SYSTEM_FREQUENCY;
  vel_z_r+=(acc_z_r-pre_acc_z_r)/SYSTEM_FREQUENCY;


  vel_L_X = vel_x_l-vel_cal_x_l;
  vel_L_Z = vel_y_l-vel_cal_y_l;
  vel_R_X = vel_x_r-vel_cal_x_r;
  vel_R_Z = vel_y_r-vel_cal_y_r;
}

void pressureAndEMGRead(){
  // pressure_L_F = digitalRead(pressure_L_F_pin_digi);
  // pressure_L_B = digitalRead(pressure_L_B_pin_digi);
  // pressure_R_F = digitalRead(pressure_R_F_pin_digi);
  // pressure_R_B = digitalRead(pressure_R_B_pin_digi);

  const int thres_l_f = 10;
  const int thres_l_b = 100;
  const int thres_r_f = 10;
  const int thres_r_b = 130;

  if(analogRead(pressure_L_F_pin)>thres_l_f) pressure_L_F = 1;
  else pressure_L_F = 0;
  if(analogRead(pressure_L_B_pin)>thres_l_b) pressure_L_B = 1;
  else pressure_L_B = 0;
  if(analogRead(pressure_R_F_pin)>thres_r_f) pressure_R_F = 1;
  else pressure_R_F = 0;
  if(analogRead(pressure_R_B_pin)>thres_r_b) pressure_R_B = 1;
  else pressure_R_B = 0;

  if(digitalRead(emg_calibrate_pin)){
    emg_cal_l = analogRead(emg_L_pin);
    emg_cal_r = analogRead(emg_R_pin);
  }

  emg_L = analogRead(emg_L_pin)-emg_cal_l;
  emg_R = analogRead(emg_R_pin)-emg_cal_r;

}




// the setup function runs once when you press reset or power the board
void setup() {
  // initialize serial readings
  Serial.begin(9600);
  // acceInit();
  // pinMode(pressure_L_F_pin_digi, INPUT);
  // pinMode(pressure_L_B_pin_digi, INPUT);
  // pinMode(pressure_R_F_pin_digi, INPUT);
  // pinMode(pressure_R_B_pin_digi, INPUT);
  pinMode(velocity_calibrate_pin, INPUT);
}

// the loop function runs over and over again forever
int counter = 0;
void loop() {
  
  // acceRead();
  // velocityUpdate();
  pressureAndEMGRead();

  counter++;
  Serial.print(String(counter));
  Serial.print(",");
  Serial.print(String(pressure_L_F));
  Serial.print(",");
  Serial.print(String(pressure_L_B));
  Serial.print(",");
  Serial.print(String(emg_L));
  Serial.print(",");

  Serial.print(String(pressure_R_F));
  Serial.print(",");
  Serial.print(String(pressure_R_B));
  Serial.print(",");
  Serial.print(String(emg_R));
  Serial.print(",");

  Serial.print(String(vel_L_X));
  Serial.print(",");
  Serial.print(String(vel_L_Z));
  Serial.print(",");
  Serial.print(String(vel_R_X));
  Serial.print(",");
  Serial.print(String(vel_R_Z));
  Serial.print(",");
  // Serial.print(String(avg_emg_L));
  // Serial.print(",");
  // Serial.print(String(avg_emg_R));
  // Serial.print(",");
  Serial.println();


  // delay(1000/SYSTEM_FREQUENCY);
  delay(50);
}
