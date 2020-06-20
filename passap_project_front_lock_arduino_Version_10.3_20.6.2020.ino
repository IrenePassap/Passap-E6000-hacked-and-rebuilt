/* Project "Passap-E6000-hacked-and-rebuilt", Version 4, 20.6.2020
    
    Part: Front Lock Passap E6000

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
  getCursorPos,
  sendCursorPos,
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
#define PIN_RIGHT             2
#define PIN_LEFT              3
#define PIN_DIRECTIONCHANGE   4


// Variables direction VNB
volatile int csenseNow = 0;
volatile int crefNow = 0;

int currentCursorPosition = 100;
int patternPos = 0;


int needle =0;


int rightEnd = 70;     // right end pattern
int leftEnd = 110;      // left end pattern


// patternChange_R means, change of direction, right side
// patternChange_L means, change of direction, left side
boolean patternChange_R = true;
boolean patternChange_L = true;

volatile boolean interrupted = false;

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
  c.sendCmdBinArg((int)currentCursorPosition);
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
  

// patternPos indicates the exact needle position, needle indicates state 0 or 1
void on_sendNPos(void){
  c.sendBinCmd(sendNPos, patternPos);
  //c.sendCmdEnd();
  delay(5);
} 

// currentCursorPosition
void on_sendCursorPos(void){
  c.sendBinCmd(sendCursorPos, currentCursorPosition);
  delay(5);
} 



// The commands must be attached to the method
void attach_callbacks() {
  c.attach(sPat, on_sPat);
  c.attach(setEmptyPat, on_setEmptyPat);
  c.attach(getNPos, on_sendNPos);
  c.attach(setNPos, on_set_null_pos);
  c.attach(setLeEnd, on_set_leftEnd);
  c.attach(setRiEnd, on_set_rightEnd);
  c.attach(getCursorPos, on_sendCursorPos);
}

///////////////////////////////////////////////////////////////////////////////

// Interrupt Routines

///////////////////////////////////////////////////////////////////////////////

// Pin CSENSE (light sensor) has changed state and triggered an interrupt
// The switch statement in the loop method requires unique cases. Therefore, I add 3 to the state of the 
// light sensor CREF and multiply the result by 10. Thereafter, the state of 
// the light sensor CSENSE is added.
// In this way, 4 different codes can be generated: 30, 31, 40, 41

void interrupt_CSENSE() {
  
  interrupted = true;  // flag
  
  crefNow = digitalRead(PIN_CREF);
  csenseNow = digitalRead(PIN_CSENSE); 
  state = ((crefNow + 3) * 10) + csenseNow;
}

// Pin CREF (light sensor) has changed state and triggered an interrupt
// The switch statement in the loop method requires unique cases. Therefore, I add 1 to the state of the 
// light sensor CREF and multiply the result by 10. Thereafter, the state of 
// the light sensor CSENSE is added.
// In this way, 4 different codes can be generated: 10, 11, 20, 21

void interrupt_CREF() {
  
  interrupted = true;  // flag
  
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);
  state = ((crefNow + 1) * 10) + csenseNow;

  // counting up, sets needle according to the pattern, , sends a signal to Raspberry Pi 
  if(state==10) {
    if ((patternPos<=leftEnd) && (patternPos>=rightEnd)){ 
      needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));    
      digitalWrite(PIN_NEEDLE_RTL, needle);
      }
    else if (patternPos == (leftEnd + 15)){
      digitalWrite(PIN_NEEDLE_RTL, 1);
      digitalWrite(PIN_LEFT, HIGH);
      digitalWrite(PIN_LEFT, LOW);
    }
    else if (patternPos == (rightEnd - 20)){
      digitalWrite(PIN_NEEDLE_RTL, 1);
      digitalWrite(PIN_DIRECTIONCHANGE, HIGH);
      digitalWrite(PIN_DIRECTIONCHANGE, LOW);       
    }       
    else {
      digitalWrite(PIN_NEEDLE_RTL, 1);
    }

    currentCursorPosition += 1;   
    patternPos +=1;           
  }

  // counting down, , sends a signal to Raspberry Pi 
  if(state==20){
    currentCursorPosition -= 1;
    patternPos -= 1;  
  
    if (patternPos == (rightEnd - 15)){
      digitalWrite(PIN_RIGHT, HIGH);
      digitalWrite(PIN_RIGHT, LOW);
      }
  }
}


///////////////////////////////////////////////////////////////////////////////

// Setup

///////////////////////////////////////////////////////////////////////////////  


void setup(){
  Serial.begin(115200); 
  while(!Serial);
  attach_callbacks();
  
  pinMode(PIN_LEFT, OUTPUT);
  digitalWrite(PIN_LEFT, LOW);

  pinMode(PIN_RIGHT, OUTPUT);
  digitalWrite(PIN_RIGHT, LOW);

  pinMode(PIN_DIRECTIONCHANGE, OUTPUT);
  digitalWrite(PIN_DIRECTIONCHANGE, LOW);



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
      
      // offset change, direction change, new form right to left
      case 40: {
        if (patternChange_R == true){
          
          patternChange_L = true;
          patternChange_R = false;
          patternPos = currentCursorPosition - 126;   // currentCursorPosition - 100 + 22;  
        }
      }
      break;


      case 30: {
        if ((patternPos<=leftEnd)&&(patternPos>=rightEnd)) {
          needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));     
          digitalWrite(PIN_NEEDLE_LTR, needle);
        }
        else {
          needle = 1;
          digitalWrite(PIN_NEEDLE_LTR, needle);
        }        
      }
      break;


      // offset change, direction change, new form left to right
      case 41:{              
        if (patternChange_L == true){
          
          patternChange_L = false;
          patternChange_R = true; 
         
          patternPos = currentCursorPosition -116; // currentCursorPosition - 112 " 12"      
        }
      }
      break;


      default: break;
    }
  }

  c.feedinSerialData();   
}
