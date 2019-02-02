// Passap E6000 Project
// Author: IrenePassap
// version 1.2.2019

// with English and German comments


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

// GPIO Pins links (nahe Rand)

#define PIN_CREF        9          // Sensor links
#define PIN_CSENSE      10         // Sensor rechts
#define PIN_NEEDLE_LTR  11         // Magnet: Pattern LTR
#define PIN_NEEDLE_RTL  12         // Magnet: Pattern RTL



// Variablen Richtung VNB
volatile int csenseNow = 0;
volatile int crefNow = 0;

int currentCursorPosition = 100;
int patternPos = 0;
int patternRow = 0;   // umfunktionieren

int needle = 0;
int rowCount = 0;     // neu Reihenzähler mit dem Reihenzähler könnte ich bestimmen, wann das Pattern wechseln soll
int rowCountOld = 0;

int rightEnd = 0;     // neu: Initialisieren MusterEnde rechts
int leftEnd = 0;      // neu: Initialisieren MusterEnde links

// patternChange_R bedeutet, Richtungswechsel neu rechts
boolean patternChange_R = true;
boolean patternChange_L = true;

volatile boolean interrupted = false;

int offset_RTL = 26; // addieren
int offset_LTR = 15; // addieren

volatile int state = 0;

///////////////////////////////////////////////////////////////////////////////

//Funktionen Arduino - Raspberry Pi

///////////////////////////////////////////////////////////////////////////////



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

void on_set_null_pos(void){
  int new_currentCursorPosition = c.readBinArg<int>();
  c.sendCmdStart(sbNPos);
  c.sendCmdBinArg((int)currentCursorPosition);
  currentCursorPosition = 100;
  c.sendCmdBinArg((int)currentCursorPosition);
  c.sendCmdEnd();
  delay(5);
}

void on_set_leftEnd(){
  leftEnd= c.readBinArg<int>();
  c.sendBinCmd(sbLeEnd, leftEnd);
  delay(5);
}
  
void on_set_rightEnd(){
  rightEnd = c.readBinArg<int>();
  c.sendBinCmd(sbRiEnd, rightEnd);
  delay(5);
  }


void on_sRowCount(void){
  rowCountOld = rowCount;
  rowCount = c.readBinArg<int>();
  c.sendCmdStart(sbRowCount);
  c.sendCmdBinArg((int)rowCountOld);
  c.sendCmdBinArg((int)rowCount);
  c.sendCmdEnd();
  delay(5);
}

// patternPos zeigt die genaue Nadelposition an, needle zeigt den Zustand 0 oder 1
void on_sendNPos(void){
  c.sendBinCmd(sendNPos, patternPos);
  delay(5);
}

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

// Interrupt Routine

///////////////////////////////////////////////////////////////////////////////

void interrupt_CSENSE() {
  
  interrupted = true;
  
  crefNow = digitalRead(PIN_CREF);
  csenseNow = digitalRead(PIN_CSENSE); 
  state = ((crefNow + 3) * 10) + csenseNow;
}


void interrupt_CREF() {
  
  interrupted = true;
  
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);
  state = ((crefNow + 1) * 10) + csenseNow;  

  if(state==10){

    needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));    
    digitalWrite(PIN_NEEDLE_LTR, needle);

    currentCursorPosition -= 1;   
    patternPos -=1; 
  }
  
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
  
  // Setup Magneten
  pinMode(PIN_NEEDLE_RTL, OUTPUT);
  pinMode(PIN_NEEDLE_LTR, OUTPUT);
  
  // Setup PHOTO SENSOR pin change interrupt
  attachInterrupt(digitalPinToInterrupt(PIN_CSENSE), interrupt_CSENSE, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_CREF), interrupt_CREF, CHANGE);
  
  csenseNow = digitalRead(PIN_CSENSE);
  crefNow = digitalRead(PIN_CREF);

  // Set Needle state
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

      // von rechts nach links
      // case 30: zählt hoch, wechsel von rechts nach links
      case 30: {
        if (needle>=0){
          needle = bitRead(patternArray[patternPos/8], 7-(patternPos%8));     
          digitalWrite(PIN_NEEDLE_RTL, needle);
        }
      }
      break;

      case 41:{        
        
        if (patternChange_R == true){
          patternChange_R = false;
          patternChange_L = true;
          patternPos = currentCursorPosition -122; // currentCursorPosition - 100 " 25"
          rowCount +=1;   // Richtungswechsel = Reihenzähler plus 1
        }
      }
      break;
      
      
      /////////////////////// von links nach rechts
      
      // Wechsel von links nach rechts
      case 40: {
        if (patternChange_L == true){
          patternChange_R = true;
          patternChange_L = false;
          patternPos = currentCursorPosition - 112;   // currentCursorPosition - 100 + 15;
          rowCount += 1;    // Arduino meldet neue Reihe, das muss unbedingt noch abgesichert werden durch err für frühzeitiges Schlittenwenden            
        }
      }
      break;    

      default: break;

    }
  }
  
 c.feedinSerialData();  
}
