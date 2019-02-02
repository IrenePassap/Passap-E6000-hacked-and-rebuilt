// Passap E6000 Project
// Author: IrenePassap
// version 1.2.2019


#include "CmdMessenger.h"
#include "Arduino.h" 

#define Serial SerialUSB
                                                                                                                                                                                                           
byte patternArray[25]={0};
int series_length;
byte pat;

enum {
  sPat,         // incomming Data from Raspberry  
  sbPat,         // get data from Raspberry and send data back
  setEmptyPat,
  sbEmptyPat,
  setNPos,
  sbNPos,
  getNPos,
  sendNPos,
  sRowCount,
  sbRowCount,
  setLeEnd,
  sbLeEnd,
  setRiEnd,
  sbRiEnd,
};

CmdMessenger c = CmdMessenger(Serial, ',',';','/');

///////////////////////////////////////////////////////////////////////////////

//Konstanten und Variablen Arduino - Passap E6000


///////////////////////////////////////////////////////////////////////////////

// GPIO Pins
#define PIN_CREF        9          // Sensor left
#define PIN_CSENSE      10         // Sensor right
#define PIN_NEEDLE_RTL  11         // Magnet: Pattern RTL (right to left)
#define PIN_NEEDLE_LTR  12         // Magnet: Pattern LTR (left to right)


// GPIO communication with Raspi, generates an interrupt on Raspi
#define PIN_OUT 2


// Variables direction VNB
volatile int csenseNow = 0;
volatile int crefNow = 0;

int currentCursorPosition = 100;
int patternPos = 0;
int patternRow = 0;   // counts only the pattern rows

int needle =0;
int rowCount = 0;     // counts every knitted row
int rowCountOld = 0;

int rightEnd = 0;     // right end pattern
int leftEnd = 0;      // left end pattern

// patternChange_R means, change of direction, right side
// patternChange_L means, change of direction, left side
boolean patternChange_R = true;
boolean patternChange_L = true;

volatile boolean interrupted = false;

// When changing direction, the needle position must be adjusted. 
//From right to left, the pushers on the left side of the lock are selected. 
//From left to right, the pushers are selected on the right side of the lock.
int offset_RTL = 26; // add offset  
int offset_LTR = 15; // add offset

volatile int state = 0;

///////////////////////////////////////////////////////////////////////////////

//Methods Arduino - Raspberry Pi

///////////////////////////////////////////////////////////////////////////////


// get new knit pattern row
void on_sPat(void){
    
    series_length = c.readInt16Arg();

    c.sendCmdStart(sbPat);
  
    for (int i = 0; i < 23; i++){           
      pat=c.readBinArg<byte>();
      patternArray[i] = pat;
      c.sendCmdBinArg(patternArray[i]);
    }  
    c.sendCmdEnd();
    delay(5);
}

// get an empty knit pattern row, no needle will knit
void on_setEmptyPat(void){

  series_length = c.readInt16Arg();

  c.sendCmdStart(sbEmptyPat);
  
  for (int i = 0; i < 23; i++){
    pat=c.readBinArg<byte>();
    patternArray[i] = pat;
    c.sendCmdBinArg(patternArray[i]);
  }    
 c.sendCmdEnd();
 delay(5);
}

// set the 0 Position to calibrate
void on_set_null_pos(void){
  int new_currentCursorPosition = c.readBinArg<int>();
  c.sendCmdStart(sbNPos);
  c.sendCmdBinArg((int)currentCursorPosition);
  currentCursorPosition = 100;
  //c.sendCmdBinArg((int)currentCursorPosition);
  c.sendCmdEnd();
  delay(5);
}

// sets the desired left end needle position of the knitting
// not used at the moment
void on_set_leftEnd(){
  leftEnd= c.readBinArg<int>();
  c.sendBinCmd(sbLeEnd, leftEnd);
  delay(5);
}

// sets the desired right end needle position of the knitting
// not used at the moment 
void on_set_rightEnd(){
  rightEnd = c.readBinArg<int>();
  c.sendBinCmd(sbRiEnd, rightEnd);
  delay(5);
  }

// row counter
void on_sRowCount(void){
  rowCountOld = rowCount;
  rowCount = c.readBinArg<int>();
  c.sendCmdStart(sbRowCount);
  c.sendCmdBinArg((int)rowCountOld);
  c.sendCmdBinArg((int)rowCount);
  c.sendCmdEnd();
  delay(5);
}

// patternPos indicates the exact needle position, needle indicates state 0 or 1
void on_sendNPos(void){
  c.sendBinCmd(sendNPos, patternPos);
  delay(5);
}

// The commands must be attached to the method
void attach_callbacks() {
  c.attach(sPat, on_sPat);
  c.attach(setEmptyPat, on_setEmptyPat);
  c.attach(sRowCount, on_sRowCount);
  c.attach(getNPos, on_sendNPos);
  c.attach(setNPos, on_set_null_pos);
  c.attach(setLeEnd, on_set_leftEnd);
  c.attach(setRiEnd, on_set_rightEnd);
  
}

///////////////////////////////////////////////////////////////////////////////

// Interrupt Routines

///////////////////////////////////////////////////////////////////////////////

// Pin CSENSE (light sensor) has changed state and triggered an interrupt
// The switch method requires a code. Therefore, I add 3 to the state of the 
// light sensor CREF and multiply the result by 10. Thereafter, the state of 
// the light sensor CSENSE is added.
// In this way, 4 different codes can be generated: 30, 31, 40, 41

void interrupt_CSENSE() {
  
  interrupted = true;
  
  crefNow = digitalRead(PIN_CREF);
  csenseNow = digitalRead(PIN_CSENSE); 
  state = ((crefNow + 3) * 10) + csenseNow;
}

// Pin CREF (light sensor) has changed state and triggered an interrupt
// The switch method requires a code. Therefore, I add 1 to the state of the 
// light sensor CREF and multiply the result by 10. Thereafter, the state of 
// the light sensor CSENSE is added.
// In this way, 4 different codes can be generated: 10, 11, 20, 21

void interrupt_CREF() {
  
  interrupted = true;
  
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);
  state = ((crefNow + 1) * 10) + csenseNow;
  
  if(state==10){
    if(needle>=0) {
      needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));    
      digitalWrite(PIN_NEEDLE_RTL, needle);
      }
      
    currentCursorPosition += 1;   
    patternPos +=1;  
  }
  
  if(state==20){
    currentCursorPosition -= 1;
    patternPos -= 1;
  }
}


///////////////////////////////////////////////////////////////////////////////

// Setup

///////////////////////////////////////////////////////////////////////////////  


void setup(){
  Serial.begin(115200); 
  while(!Serial);
  attach_callbacks();
  
  pinMode(PIN_OUT, OUTPUT);
  digitalWrite(PIN_OUT, LOW);

  // Setup Input-Pins
  pinMode(PIN_CSENSE, INPUT_PULLUP);
  pinMode(PIN_CREF, INPUT_PULLUP);
  
  // Setup magnets
  pinMode(PIN_NEEDLE_RTL, OUTPUT);
  pinMode(PIN_NEEDLE_LTR, OUTPUT);
  
  // Setup light sensors, pin change interrupt
  attachInterrupt(digitalPinToInterrupt(PIN_CSENSE), interrupt_CSENSE, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_CREF), interrupt_CREF, CHANGE);
  
  // State of the light sensors
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);

  // Set needle state
  digitalWrite(PIN_NEEDLE_RTL, HIGH);
  digitalWrite(PIN_NEEDLE_LTR, HIGH);
  
}


///////////////////////////////////////////////////////////////////////////////

//Loop

///////////////////////////////////////////////////////////////////////////////

void loop() {
      
  if (interrupted){
    interrupted = false;
    
    switch(state){
      
      // counting, offset change, direction change, new form right to left, sends a signal to Raspberry pPi 
      case 40: {
        if (patternChange_R == true){
          patternChange_L = true;
          patternChange_R = false;
          patternPos = currentCursorPosition - 122;   // currentCursorPosition - 100 + 15;
          rowCount += 1;    // Arduino meldet neue Reihe, das muss unbedingt noch abgesichert werden durch err für frühzeitiges Schlittenwenden
            
          digitalWrite(PIN_OUT, HIGH);
          digitalWrite(PIN_OUT, LOW); 
        }
      }
      break;

      // set needle
      case 30: {
        needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));     
        digitalWrite(PIN_NEEDLE_LTR, needle);
      }

      // counting, offset change, direction change, new form left to right, sends a signal to Raspberry pPi 
      case 41:{              
        if (patternChange_L == true){
          patternChange_L = false;
          patternChange_R = true;
          patternPos = currentCursorPosition -112; // currentCursorPosition - 100 " 25"
          rowCount +=1;   // Richtungswechsel = Reihenzähler plus 1
            
          digitalWrite(PIN_OUT, HIGH);
          digitalWrite(PIN_OUT, LOW); 
        }
      }
      break;

      default: break;
    }
  }
  
 c.feedinSerialData();  
}
