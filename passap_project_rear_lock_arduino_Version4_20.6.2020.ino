/* Project "Passap-E6000-hacked-and-rebuilt", Version 4, 20.6.2020
    
    Part: Rear Lock Passap E6000

    published under Hackaday
    https://hackaday.io/project/163701-passap-e6000-rebuilt-and-replaced-console 

    created by Irene Wolf
 */


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

#define PIN_CREF        9          // Sensor links
#define PIN_CSENSE      10         // Sensor rechts
#define PIN_NEEDLE_LTR  11         // Magnet: Pattern LTR
#define PIN_NEEDLE_RTL  12         // Magnet: Pattern RTL



// Variables direction VNB
volatile int csenseNow = 0;
volatile int crefNow = 0;

int currentCursorPosition = 100;
int patternPos = 0;

int needle = 0;


int rightEnd = 70;      // right end knitting
int leftEnd = 110;      // left end Knitting

// if direction change
boolean patternChange_R = true;
boolean patternChange_L = true;

volatile boolean interrupted = false;

int offset_RTL = 26; // add offset
int offset_LTR = 15; // add offset

volatile int state = 0;

///////////////////////////////////////////////////////////////////////////////

//Funktionen Arduino - Raspberry Pi

///////////////////////////////////////////////////////////////////////////////


// if called, Raspberry Pi sends a pattern row to arduino
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

// if called, Raspberry Pi sends an a row, where no needle will be selected
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

// if called, Raspberry Pi sends the O-Position to calibrate
void on_set_null_pos(void){
  int new_currentCursorPosition = c.readBinArg<int>();
  c.sendCmdStart(sbNPos);
  c.sendCmdBinArg((int)currentCursorPosition);
  currentCursorPosition = 100;
  c.sendCmdBinArg((int)currentCursorPosition);
  c.sendCmdEnd();
  delay(5);
}

// if called, Raspberry Pi sends left end
void on_set_leftEnd(){
  leftEnd= c.readBinArg<int>();
  c.sendBinCmd(sbLeEnd, leftEnd);
  delay(5);
}

// if called, Raspberry Pi sends right end
void on_set_rightEnd(){
  rightEnd = c.readBinArg<int>();
  c.sendBinCmd(sbRiEnd, rightEnd);
  delay(5);
  }

// if called, Arduino sends pattern (needle) position to Raspberry Pi
void on_sendNPos(void){
  c.sendBinCmd(sendNPos, patternPos);
  delay(5);
}


void attach_callbacks() {
  c.attach(sPat, on_sPat);
  c.attach(setEmptyPat, on_setEmptyPat);
  c.attach(getNPos, on_sendNPos);
  c.attach(setNPos, on_set_null_pos);
  c.attach(setLeEnd, on_set_leftEnd);
  c.attach(setRiEnd, on_set_rightEnd); 
}

///////////////////////////////////////////////////////////////////////////////

// Interrupt Routine

///////////////////////////////////////////////////////////////////////////////

// if CSENSE is interrupted 3 ist added to the state of crefNow
// in this way it is possible to recognize which sensor triggered the interrupt first

void interrupt_CSENSE() {
  
  interrupted = true;
  
  crefNow = digitalRead(PIN_CREF);
  csenseNow = digitalRead(PIN_CSENSE); 
  state = ((crefNow + 3) * 10) + csenseNow;
}


// if the sensor CREF triggered the interrupt, 1 is added to the state of crefNow

void interrupt_CREF() {
  
  interrupted = true;
  
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);
  state = ((crefNow + 1) * 10) + csenseNow;  

  // lock drives from left to right, needle position is set, pattern position is set -1
  if(state==10){

    if((patternPos<=leftEnd)&&(patternPos>=rightEnd)){
      needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));    
      digitalWrite(PIN_NEEDLE_LTR, needle);
    }
    else {
      digitalWrite(PIN_NEEDLE_LTR, 1);
    }
    
    currentCursorPosition -= 1;   
    patternPos -=1; 
  }

  // lock drives from right to left, pattern position is set +1
  if(state==20){
    currentCursorPosition += 1;
    patternPos += 1;
  }
}


///////////////////////////////////////////////////////////////////////////////

// Setup

///////////////////////////////////////////////////////////////////////////////  


void setup(){
  Serial.begin(115200); 
  while(!Serial);
  attach_callbacks();
  

  // Setup Input-Pins
  pinMode(PIN_CSENSE, INPUT_PULLUP);
  pinMode(PIN_CREF, INPUT_PULLUP);
  
  // Setup magnet
  pinMode(PIN_NEEDLE_RTL, OUTPUT);
  pinMode(PIN_NEEDLE_LTR, OUTPUT);
  
  // Setup PHOTO SENSOR pin change interrupt
  attachInterrupt(digitalPinToInterrupt(PIN_CSENSE), interrupt_CSENSE, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_CREF), interrupt_CREF, CHANGE);
  
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

      // drives right to left
      // set needle according to pattern
      case 30: {
        if ((patternPos<=leftEnd)&&(patternPos>=rightEnd)){
          needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));     
          digitalWrite(PIN_NEEDLE_RTL, needle);
        }
        else {
          digitalWrite(PIN_NEEDLE_RTL, 1);
        }
      }
      break;

      // direction change right side, set offset
      case 41:{        
        
        if (patternChange_R == true){
          patternChange_R = false;
          patternChange_L = true;
          patternPos = currentCursorPosition -126; // currentCursorPosition - 100 " 25"

        }
      }
      break;
      
      
      /////////////////////// von links nach rechts
      
      // direction change left, set offset
      case 40: {
        if (patternChange_L == true){
          patternChange_R = true;
          patternChange_L = false;
          patternPos = currentCursorPosition - 116;   // currentCursorPosition - 100 + 15;
         
        }
      }
      break;    

      default: break;

    }
  }
  
 c.feedinSerialData();  
}
