/*
  Project: Passap-E6000-hacked-and-rebuilt
  File: Passap E6000 - Arduino - Motor Controller.ino
  Version: 12, this version is stable and runs without errors
  Date: 27.12.2023
  Author: Irene Wolf

  published on https://hackaday.io/project/163701-passap-e6000-rebuilt-and-replaced-console

  ----------------------------------------------------------------------
  IMPORTANT:
  This file replaces earlier versions such as 
  "passap_project_motor_arduino_Version_20.6.21".
  For full change history, see CHANGELOG.md or the GitHub Releases page.
  ----------------------------------------------------------------------


This release introduces major improvements and stability updates to the motor controller code:

- Updated project metadata: version 12, stable on **Raspberry Pi 4**.
- Added new commands: **setStopp / sbStopp** for safer stop handling.
- Introduced dedicated functions:
  - `drive_left()` / `drive_right()` for direction control
  - `on_stopp()` for safe stop with error reporting
  - `on_drive_left()` and `on_drive_right()` as new event handlers
- Expanded **MCP23017 support**:
  - New methods for LEDs, port reading, pull-ups, and interrupt configuration
- Improved pin definitions and descriptions (e.g. reed switches, drive LED).
- Refactored interrupt handling and code structure for better clarity.

✅ This version is more robust, modular, and reliable for long-term use.
*/


#include <Wire.h>
#include <MCP23017.h>     // von Wolle nicht Adafruit
#include "CmdMessenger.h"

#define Serial Serial
// max baudrate for nano
const int BAUD_RATE = 19200;
CmdMessenger c = CmdMessenger(Serial, ',', ';', '/');


// Potentiometer
#define PIN_POTI                       A6

// RJ45 (straight trough)
#define PIN_COLOURCHANGE               4
#define PIN_DIRECTION_CHANGE_RIGHT     3       // reed right, changes direction from left to right
#define PIN_DIRECTION_CHANGE_LEFT      10      // reed left, changes direction from right to left
#define PIN_FREQUENCY                  6
#define PIN_DRIVE                      7       // switch on red LED
#define PIN_DIRECTION_FU               5       // Input from FU, feedback direction RTL, LTR
#define PIN_RESET_FU                   8
#define PIN_EMERGENCY_STOPP            9       // input Pin

#define PIN_RESET_MCP                  11


///////////////////////////////////////////////////////////////////////////////

//constant and variables Arduino - mcp 23017 - Raspberry Pi --> Motor Electra 4600

///////////////////////////////////////////////////////////////////////////////

#define MCP_ADDRESS 0x20 // (A2/A1/A0 = LOW) 

#define MCP_IODIRA  0x00  // I/O direction register
#define MCP_IODIRB  0x01

#define MCP_GPINTENA 0x04 // Interrupt-on-change pins A
#define MCP_GPINTENB 0x05 // Interrupt-on-change pins B

#define MCP_DEFVALA 0x06  // Default value register A
#define MCP_DEFVALB 0x07

#define MCP_INTCONA 0x08  // Interrupt-on-change control register A
#define MCP_INTCONB 0x09

#define MCP_INTCAPA 0x10  // Interrupt captured value for port register A
#define MCP_INTCAPB 0x11  // Interrupt captured value for port register B

#define MCP_IOCONA 0x0A   // I/O expander configuration register A
#define MCP_IOCONB 0x0B

#define MCP_GPPUA 0x0C    // GPIO pull-up resistor register A
#define MCP_GPPUB 0x0D

#define MCP_GPIOA 0x12    // General purpose I/O port register A
#define MCP_GPIOB 0x13    // General purpose I/O port register B

#define MCP_OLATA 0x14    // Output latch register 0 A
#define MCP_OLATB 0x15    // Output latch register 0 B

#define MCP23017_INT_ERR 255 // Interrupt error

// USB CmdMessenger commands, communication between Arduino and Raspberry Pi 4 --> console
enum {
  slowDownSpeed, 
  sbSlowDownSpeed,
  setColourChange, 
  sbColourChange,
  setRowEndStopp, 
  sbRowEndStopp,
  setFormStopp,
  sbFormStopp,
  setDrive_left, 
  sbDrive_left,
  setDrive_right, 
  sbDrive_right,
  setStopp,
  sbStopp,
};

// mcp23017 interrupt arduino 
int interruptPin = 2;
volatile bool event;
volatile bool flag;
byte intCapReg;

// button state motor controller
volatile boolean state_drive;
volatile boolean state_driveLeft;
volatile boolean state_driveRight;
volatile boolean state_endStopp;
volatile boolean state_colourChange;
volatile boolean state_Reset;
volatile boolean flag_endStopp_left;
volatile boolean flag_endStopp_right;

// LED motor controller
int drive_LED = 0;              // red
int drive_left_LED = 1;         // white-yellow
int drive_right_LED = 2;        // white
int endStopp_LED = 3;           // green
int colourChange_LED = 4;       // yellow
int reset_LED = 5;              // blue

// value potentiometer
int analogValue;
int valuePoti;
volatile int statePoti;


/*
 * You can choose if you want to use the reset function or not.
 * If you don't need it, you can save one pin.
 */
MCP23017 myMCP(MCP_ADDRESS,11); // Pin 11 is used as reset pin
//MCP23017 myMCP(MCP_ADDRESS); // alternative option not using the reset pin


/////////////////////////////

// Interrupt routine

////////////////////////////

// Handles incoming events and dispatches them to the appropriate function
// flag is reset when the interrupt has been processed 
// all interrupts are ignored until then
void eventHappened(){
  if (flag == true){ 
    event = true;
    flag = false;
  }
}


/////////////////////////////
// mcp 23017
////////////////////////////

// Updates all MCP23017-controlled LEDs on Bank A at once
void mcp_setAll_LED(uint8_t state){
  uint8_t gpio_A;
  if(state == HIGH){
    gpio_A = B11111111;
  }
  else if(state==LOW){
    gpio_A = B00000000;
  }
  mcp_writeRegister(MCP_GPIOA, gpio_A);
}

// returns value
uint8_t mcp_getIntCapB(){
  uint8_t value = 0;
  value = mcp_readRegister(MCP_INTCAPB);
  return value;
}

// returns value
uint8_t mcp_getPort_B(){
  uint8_t value = 0;
  value = mcp_readRegister(MCP_GPIOB);
  return value;
}

// Configures MCP23017 port B interrupt behavior with default values
void mcp_setInterruptOnDefValDevPort_B(uint8_t val, uint8_t state){   // interrupt pins, port, DEFVALB
  uint8_t ioDirB = val; 
  uint8_t gpIntEnB = val;
  uint8_t intConB = val;
  uint8_t defValB = state;
  
  mcp_writeRegister(MCP_IODIRB, ioDirB);
  mcp_writeRegister(MCP_GPINTENB,gpIntEnB);
  mcp_writeRegister(MCP_INTCONB, intConB);
  mcp_writeRegister(MCP_DEFVALB, defValB);
}

// Enables pull-up resistors on MCP23017 port B
void mcp_setPortPullUp_B(uint8_t val){
  uint8_t gppuB = val;
  mcp_writeRegister(MCP_GPPUB, gppuB);
}


/////////////////////////////
//Methods Rspberry Pi 4 - Arduino Motor
////////////////////////////

// Activates the motor drive in the left direction
void drive_left(){
  state_driveLeft = HIGH;
  state_driveRight = LOW;    
   
  mcp_digitalWrite(drive_left_LED, state_driveLeft);
  mcp_digitalWrite(drive_right_LED,state_driveRight);
  digitalWrite(PIN_DIRECTION_CHANGE_LEFT, HIGH);
  delay(50);
  digitalWrite(PIN_DIRECTION_CHANGE_LEFT, LOW);

  statePoti = 0;
}

// Activates the motor drive in the right direction
void drive_right(){   
  state_driveLeft = LOW;
  state_driveRight = HIGH;  
   
  mcp_digitalWrite(drive_right_LED, state_driveRight);
  mcp_digitalWrite(drive_left_LED, state_driveLeft);
  digitalWrite(PIN_DIRECTION_CHANGE_RIGHT, HIGH);
  delay(50);
  digitalWrite(PIN_DIRECTION_CHANGE_RIGHT, LOW);

  statePoti = 0;
}

// Safely stops the motor and reports a stop condition or error
void on_stopp(void){
  state_drive = LOW;
  digitalWrite(PIN_DRIVE, state_drive); 
  mcp_digitalWrite(drive_LED, state_drive);
  c.sendCmd(sbStopp, "failure, stopp");
  delay(5);
}

// Event handler that triggers driving the motor to the left
void on_drive_left(void){
  drive_left();
  c.sendCmd(sbDrive_left, "new_drive_left");
  delay(5);
}

// Event handler that triggers driving the motor to the right
void on_drive_right(void){
  c.sendCmd(sbDrive_right, "driveRight");
  drive_right();  
  delay(5);
}

// Event handler for a form/shape stop condition (specific end stop)
void on_form_stopp(void){
  state_endStopp = c.readBinArg<bool>();
  mcp_digitalWrite(endStopp_LED, state_endStopp); 
  c.sendCmd(sbFormStopp, "form_stopp");
  delay(5);
}

// Handles a command to reduce motor speed gradually (potentiometer)
void on_setSpeed_slowDown(){
  statePoti = c.readBinArg<int>();
  c.sendBinCmd(slowDownSpeed, statePoti);
  delay(5);
}

// Handles a command to trigger a color-change operation
void on_setColourChange(){
  state_colourChange = c.readBinArg<bool>();
  
  mcp_digitalWrite(colourChange_LED, state_colourChange);
  digitalWrite (PIN_COLOURCHANGE, !state_colourChange);
  
  c.sendBinCmd(sbColourChange,state_colourChange);
  delay(5);
}

// Handles an event when the row end stop is reached
void on_setRowEndStopp(){
  state_endStopp = c.readBinArg<bool>();
  mcp_digitalWrite(endStopp_LED, state_endStopp);
  
  c.sendBinCmd(sbRowEndStopp, state_endStopp);
  delay(5);
}

// Registers callbacks to event handlers for external commands
void attach_callbacks(){
  c.attach(slowDownSpeed, on_setSpeed_slowDown);
  c.attach(setColourChange, on_setColourChange);
  c.attach(setRowEndStopp, on_setRowEndStopp);
  c.attach(setFormStopp, on_form_stopp);
  c.attach(setDrive_left, on_drive_left);
  c.attach(setDrive_right, on_drive_right);
  c.attach(setStopp, on_stopp);
}

// Arduino initialization function; sets up pins, interrupts, and communication
void setup(){ 
  Serial.begin(BAUD_RATE);
  attach_callbacks();
  
  while(!Serial);
  Wire.begin();

  // potentiometer
  valuePoti = 0; 
  
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), eventHappened, RISING);

  // setup I/O Expander Configuration Register, SEQOP=HIGH, INTPOL=active HIGH (page 18)
  // SEQOP: Sequential Operation mode bit 5:
  // 1 =  Sequential operation disabled, address pointer does not increment.
  // 0 =  Sequential operation enabled, address pointer increments
  // INTPOL: This bitsets the polarity of the INT output pin.
  // 1 =  Active-high.
  // 0 =  Active-low.
  mcp_writeRegister(MCP_IOCONB, B00100010);
  mcp_writeRegister(MCP_IOCONA, B00100010);
  delay(10);
  
  // setup I/O Direction Register
  // A: Output
  // B: Input
  mcp_writeRegister(MCP_IODIRA, B00000000);
  mcp_writeRegister(MCP_IODIRB, B11111111);
  delay(10);
  
  mcp_setAll_LED(HIGH);
  delay(1000); 
  mcp_setAll_LED(LOW);
  delay(1000);
  
  mcp_setInterruptOnDefValDevPort_B(B00111111, B00111111);    // interrupt pins, port, DEFVALB

  event=false;
  flag=true;

  state_drive = LOW;
  state_driveLeft = HIGH;
  state_driveRight = LOW;
  state_endStopp = LOW;
  state_colourChange = LOW;
  state_Reset = LOW;
  statePoti = 0;

  flag_endStopp_left = 1;
  flag_endStopp_right = 1;

  // setup RJ45 Input
  pinMode(PIN_DIRECTION_FU, INPUT_PULLUP); 
  // drive signal
  pinMode(PIN_EMERGENCY_STOPP, INPUT);
  
  pinMode(PIN_POTI, INPUT);

  pinMode(PIN_COLOURCHANGE, OUTPUT);
  digitalWrite(PIN_COLOURCHANGE, HIGH);
  
  pinMode(PIN_DIRECTION_CHANGE_RIGHT, OUTPUT);
  digitalWrite(PIN_DIRECTION_CHANGE_RIGHT, HIGH);
  
  pinMode(PIN_DIRECTION_CHANGE_LEFT, OUTPUT);
  digitalWrite(PIN_DIRECTION_CHANGE_LEFT, LOW);
  
  pinMode(PIN_FREQUENCY, OUTPUT);
  digitalWrite(PIN_FREQUENCY, valuePoti);
  
  pinMode(PIN_DRIVE, OUTPUT);
  digitalWrite(PIN_DRIVE, LOW);

  pinMode(PIN_RESET_FU, OUTPUT);
  digitalWrite(PIN_RESET_FU, LOW);
  
  pinMode(PIN_RESET_MCP, OUTPUT);
  digitalWrite(PIN_RESET_MCP, HIGH);
}  

uint8_t mcp_readRegister(uint8_t reg){
  uint8_t regVal;
  Wire.beginTransmission(MCP_ADDRESS);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(MCP_ADDRESS, 1);
  regVal = Wire.read();
  return regVal;
}

// Writes directly to an MCP23017 hardware register
void mcp_writeRegister(uint8_t reg, uint8_t val){
  Wire.beginTransmission(MCP_ADDRESS);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
  delay(1);
}

// Sets the output state of a pin on the MCP23017
void mcp_digitalWrite(uint8_t pin, uint8_t value) {
  uint8_t gpio_A;
  uint8_t bit = pin;

  // read the current GPIO output latches
  uint8_t regAddr = MCP_OLATA;
  gpio_A = mcp_readRegister(regAddr);

  // set the pin and direction
  bitWrite(gpio_A, bit, value);

  // write the new GPIO
  mcp_writeRegister(MCP_GPIOA, gpio_A);
}

// Clears pending interrupts from the MCP23017 to reset state
void cleanInterrupt(){
  event = false;
  flag = true;
  EIFR=0x01; 
}

// Main interrupt handler; processes MCP23017 input changes
void handleInterrupt(){

  byte intFlagReg, eventPin; 
  
    intFlagReg = myMCP.getIntFlag(B);
    eventPin = log(intFlagReg)/log(2);

    intCapReg = myMCP.getIntCap(B);

    switch(eventPin){
      case 0: {  // red button & LED, drive
        if(intFlagReg == 1){
          state_drive = !state_drive; 
          mcp_digitalWrite(drive_LED, state_drive);
          
          digitalWrite(PIN_DRIVE, state_drive);
          }

          if(state_drive == HIGH){
          mcp_digitalWrite(reset_LED, LOW);
          }        
      }
      break;
      case 1: {  // white_y button & LED, drive left
        if(intFlagReg==2){
          drive_left();    
        }
      }
      break;
      case 2:{   // white button & LED, drive right 
        if(intFlagReg==4){
        drive_right();      
        } 
      }           
      break;
      case 4:{   // yellow button & LED, colour change
        if(intFlagReg==16){
          state_colourChange = !state_colourChange;
          mcp_digitalWrite(colourChange_LED, state_colourChange);
          digitalWrite(PIN_COLOURCHANGE, !state_colourChange);   // Low means override
        }
      }
      break;
      case 3:{   // green button & LED, end stopp
        if(intFlagReg==8){
          state_endStopp = !state_endStopp;
          mcp_digitalWrite(endStopp_LED, state_endStopp);
        }
      }
      break;
      case 5:{  // blue button, reset
        if(intFlagReg == 32){
          mcp_digitalWrite(reset_LED, HIGH);
          digitalWrite(PIN_RESET_FU, HIGH);
          delay(50);
          digitalWrite(PIN_RESET_FU, LOW);
  
          if(digitalRead(PIN_EMERGENCY_STOPP) == LOW){
            state_drive = LOW;   
            mcp_digitalWrite(drive_LED, state_drive);  
          }
        
          drive_right();
          drive_left();
        }
      }
      break;

      default: break;     
    }  
    cleanInterrupt();
}

// repeatedly checks for and handles events
void loop(){ 
  if(digitalRead(interruptPin) == HIGH){    // HIGH is default
    if (flag==true){
      intCapReg = mcp_getIntCapB();
      mcp_getPort_B();
    }    
  }
  
  if(event){
    delay(200);
    handleInterrupt();
  }

//  analogValue = analogRead(PIN_POTI);  // read the input on analog pin
//  valuePoti = map(analogValue, 0, 1023, 0, 255);    //Map value 0-1023 to 0-255 (PWM)
//  analogWrite(PIN_FREQUENCY,valuePoti);            //send PWM Value to FU

    
  // Potentiometer and speed FU
  switch(statePoti){                
    case 0: {    
      analogValue = analogRead(PIN_POTI);  // read the input on analog pin
      valuePoti = map(analogValue, 0, 1023, 0, 255);    //Map value 0-1023 to 0-255 (PWM)
      analogWrite(PIN_FREQUENCY,valuePoti);            //send PWM Value to FU
    }
    break;
    
    case 1: {
      analogWrite(PIN_FREQUENCY,140); 
    }
    break;
    
    case 2: {
      while(valuePoti>100){
        valuePoti = valuePoti-10;
        analogWrite(PIN_FREQUENCY,valuePoti); 
      }
    }
    break;

    default: break;
  } 

  if ((state_endStopp == HIGH) && (digitalRead(PIN_DIRECTION_FU) == HIGH)){
    if (flag_endStopp_right == 1){
      state_drive = LOW;
      digitalWrite (PIN_DRIVE, state_drive);
      mcp_digitalWrite(drive_LED, state_drive); 
      
      flag_endStopp_right = 0;
      flag_endStopp_left = 1;
      state_driveRight = HIGH;
      state_driveLeft = LOW;
      mcp_digitalWrite(drive_right_LED, state_driveRight);
      mcp_digitalWrite(drive_left_LED, state_driveLeft);
    }
  }

  else if ((state_endStopp == LOW) && (digitalRead(PIN_DIRECTION_FU) == HIGH)){
    if (flag_endStopp_right == 1){
      
      flag_endStopp_right = 0;
      flag_endStopp_left = 1;
      state_driveRight = HIGH;
      state_driveLeft = LOW;
      mcp_digitalWrite(drive_right_LED, state_driveRight);
      mcp_digitalWrite(drive_left_LED, state_driveLeft);
    }
  }
    
  if ((state_endStopp == HIGH) && (digitalRead(PIN_DIRECTION_FU) == LOW)){
    if (flag_endStopp_left == 1){
      state_drive = LOW;
      digitalWrite (PIN_DRIVE, state_drive);
      mcp_digitalWrite(drive_LED, state_drive);
      
      flag_endStopp_left = 0;
      flag_endStopp_right = 1;
      state_driveRight = LOW;
      state_driveLeft = HIGH;
      mcp_digitalWrite(drive_right_LED, state_driveRight);
      mcp_digitalWrite(drive_left_LED, state_driveLeft);
    }
  }
  
  else if ((state_endStopp == LOW) && (digitalRead(PIN_DIRECTION_FU) == LOW)){
    if (flag_endStopp_left == 1){
      
      flag_endStopp_left = 0;
      flag_endStopp_right = 1;
      state_driveRight = LOW;
      state_driveLeft = HIGH;
      mcp_digitalWrite(drive_right_LED, state_driveRight);
      mcp_digitalWrite(drive_left_LED, state_driveLeft);
    }
  }

  c.feedinSerialData();
}
