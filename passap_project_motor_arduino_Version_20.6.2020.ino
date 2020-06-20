/* Project "Passap-E6000-hacked-and-rebuilt", Version 4, 20.6.2020
    
    Part: Motor Controller Passap E6000

    project published under Hackaday
    https://hackaday.io/project/163701-passap-e6000-rebuilt-and-replaced-console 

    created by Irene Wolf
 */



#include "CmdMessenger.h"
#include "Arduino.h"

#define Serial Serial

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
};


const int BAUD_RATE = 19200;

CmdMessenger c = CmdMessenger(Serial, ',', ';', '/');



///////////////////////////////////////////////////////////////////////////////

// PIN

///////////////////////////////////////////////////////////////////////////////


// SWITCHES
# define COLOUR_SWITCH          4           // wenn ich etwas ändern möchte, dann hier (Colour switch vertauschen mit End_Row_Stopp switch)
# define END_ROW_STOPP_SWITCH   5
# define DRIVE_RIGHT_SWITCH     9
# define RESET_SWITCH          10
# define DRIVE_LEFT_SWITCH      13
# define STOPP_SWITCH           19


//LED
# define YELLOW_COLOURCHANGE_LED  6
# define GREEN_ENDSTOPP_LED       7
# define GREY_DRIVE_RIGHT_LED     8
//# define BLUE_LED               11      // new works with reset
# define WHITE_DRIVE_LEFT_LED     12

                                          //Important: PIN 18 is PIN_DRIVE && RED_LED

// Potentiometer
#define PIN_POTI   14                     // A0


// RJ45 (straight trough)
#define PIN_FREQUENCY       3
#define PIN_DRIVE_RIGHT     15
#define PIN_DRIVE_LEFT      16
#define PIN_COLOURCHANGE    17
#define PIN_DRIVE           18            // switch on red LED
#define PIN_DIRECTION_FU    2             // Input from FU, feedback direction RTL, LTR
#define PIN_RESET           11

///////////////////////////////////////////////////////////////////////////////

// Variabels

///////////////////////////////////////////////////////////////////////////////


// value potentiometer
int analogValue;
int value;

// Feedback FU
int directionChanged_FeedbackFu;


// Variable used for millis debounce
long TimeOfLastDebounce = 0;  // holds the last time the drive switch was pressed
long TimeOfLastDebounceCol = 0; // holds the last time the override switch was pressed
long TimeOfLastDebounceRight = 0;
long TimeOfLastDebounceLeft = 0;
long TimeOfLastDebounceEndStopp = 0;
long TimeOfLastDebounceReset = 0;


long DelayOfDebounce = 200;  // amount of time that needs to be experied between presses


boolean previousDrive;
boolean previousColourChange;
boolean previousRight;
boolean previousLeft;
boolean previousEndStopp;
boolean previousReset;
boolean previousDirectionFu;

boolean readingDrive;
boolean readingColourChange;
boolean readingRight;
boolean readingLeft;
boolean readingEndStopp;
boolean readingReset;
boolean readingDirectionFu;


// Variable used to save the state of the switches
// Needed so the counter only goes +1 for each keypress
volatile boolean stateDrive;
volatile boolean stateColourChange;
volatile boolean stateRight;
volatile boolean stateLeft;
volatile boolean stateEndStopp;
volatile boolean stateReset;
volatile boolean stateDirectionFu;



boolean colourChange;


volatile int statePoti;




/////////////////////////////

//Methods Rspberry Pi - Arduino Motor

////////////////////////////

void drive_right(){
  stateRight = HIGH;
  stateLeft = LOW;
  digitalWrite (GREY_DRIVE_RIGHT_LED, stateRight);
  digitalWrite (WHITE_DRIVE_LEFT_LED, stateLeft);
  digitalWrite (PIN_DRIVE_RIGHT, HIGH); 
  statePoti = 0;
}

void drive_left(){
  stateLeft = HIGH;
  stateRight = LOW;
  digitalWrite (WHITE_DRIVE_LEFT_LED, stateLeft);
  digitalWrite (GREY_DRIVE_RIGHT_LED, stateRight);
  digitalWrite (PIN_DRIVE_LEFT, HIGH);
  statePoti = 0;
}

void on_drive_left(void){
  drive_left();
  c.sendCmd(sbDrive_left, "new_drive_left");
  delay(5);
}

void on_drive_right(void){
  drive_right();
  c.sendCmd(sbDrive_left, "new_drive_right");
  delay(5);
}


void on_form_stopp(void){
  stateDrive = LOW;
  digitalWrite (PIN_DRIVE, stateDrive); 
  c.sendCmd(sbFormStopp, "form_stopp");
  delay(5);
}

void on_setSpeed_slowDown(){
  statePoti = c.readBinArg<int>();
  c.sendBinCmd(slowDownSpeed, statePoti);
  delay(5);
}


void on_setColourChange(){
  stateColourChange = c.readBinArg<bool>();
  digitalWrite (YELLOW_COLOURCHANGE_LED, stateColourChange);
  digitalWrite (PIN_COLOURCHANGE, !stateColourChange);
  c.sendBinCmd(sbColourChange,stateColourChange);
  delay(5);
}

void on_setRowEndStopp(){
  stateEndStopp = c.readBinArg<bool>();
  digitalWrite(GREEN_ENDSTOPP_LED, stateEndStopp);
  c.sendBinCmd(sbRowEndStopp, stateEndStopp);
  delay(5);
}


void attach_callbacks(){
  c.attach(slowDownSpeed, on_setSpeed_slowDown);
  c.attach(setColourChange, on_setColourChange);
  c.attach(setRowEndStopp, on_setRowEndStopp);
  c.attach(setFormStopp, on_form_stopp);
  c.attach(setDrive_left, on_drive_left);
  c.attach(setDrive_right, on_drive_right);
}


////////////////////////////////////////////////////

// SETUP

//////////////////////////////////////////////////////


void setup() {
  Serial.begin(BAUD_RATE);
  attach_callbacks();

  // potentiometer
  value = 0;

  pinMode(PIN_POTI, INPUT);                   // setup Poti

  pinMode(PIN_FREQUENCY, OUTPUT);             // RJ 45    // cable PWM violett
  digitalWrite(PIN_FREQUENCY, value);

  // colour
  pinMode(COLOUR_SWITCH, INPUT);              // lock goes in colour changer
  
  pinMode(PIN_COLOURCHANGE, OUTPUT);          // RJ45: colour change
  digitalWrite(PIN_COLOURCHANGE, HIGH);
  digitalWrite(PIN_COLOURCHANGE, LOW);
  digitalWrite(PIN_COLOURCHANGE, HIGH);

  pinMode(YELLOW_COLOURCHANGE_LED, OUTPUT);   // colour change, yellow LED
  digitalWrite(YELLOW_COLOURCHANGE_LED, LOW);
  digitalWrite(YELLOW_COLOURCHANGE_LED, HIGH);
  digitalWrite(YELLOW_COLOURCHANGE_LED, LOW);
  
  // drive right
  pinMode(DRIVE_RIGHT_SWITCH, INPUT);         // switch drive right

  pinMode(PIN_DRIVE_RIGHT, OUTPUT);           // RJ45: drive right, grey LED
  digitalWrite(PIN_DRIVE_RIGHT, LOW);
  digitalWrite(PIN_DRIVE_RIGHT, HIGH);
  digitalWrite(PIN_DRIVE_RIGHT, LOW);

  pinMode(GREY_DRIVE_RIGHT_LED, OUTPUT);      // drive right LED, grey (white/green) LED
  digitalWrite(GREY_DRIVE_RIGHT_LED, LOW);  

  // drive left
  pinMode(DRIVE_LEFT_SWITCH, INPUT);          // switch drive left
  
  pinMode(PIN_DRIVE_LEFT, OUTPUT);            // RJ45: drive left
  digitalWrite(PIN_DRIVE_LEFT, HIGH);
  digitalWrite(PIN_DRIVE_LEFT, LOW);
  digitalWrite(PIN_DRIVE_LEFT, HIGH);

  pinMode(WHITE_DRIVE_LEFT_LED, OUTPUT);      // drive left LED, white LED
  digitalWrite(WHITE_DRIVE_LEFT_LED, HIGH);
  digitalWrite(WHITE_DRIVE_LEFT_LED, LOW);
  digitalWrite(WHITE_DRIVE_LEFT_LED, HIGH);

  // Row end
  pinMode(END_ROW_STOPP_SWITCH, INPUT);       // switch lock stops end of row left and right
  
  pinMode(GREEN_ENDSTOPP_LED, OUTPUT);        // end stopp, green LED
  digitalWrite(GREEN_ENDSTOPP_LED, LOW);
  digitalWrite(GREEN_ENDSTOPP_LED, HIGH);
  digitalWrite(GREEN_ENDSTOPP_LED, LOW);

  // drive signal
  pinMode(STOPP_SWITCH, INPUT);               // switch drive/stopp, connected with red LED
  
  pinMode(PIN_DRIVE, OUTPUT);                 // RJ45: drive signal
  digitalWrite(PIN_DRIVE, LOW);

  // reset
  pinMode(RESET_SWITCH, INPUT);              // switch reset
  
  pinMode(PIN_RESET, OUTPUT);                  // RJ45: reset signal, connected with blue LED
  digitalWrite(PIN_RESET, LOW);


  // setup RJ45 Input
  pinMode(PIN_DIRECTION_FU, INPUT_PULLUP);

  stateDrive = LOW;
  stateColourChange = LOW;
  stateRight = LOW;
  stateLeft = HIGH;
  stateEndStopp = LOW;
  stateDirectionFu = LOW;
  stateReset = LOW;
  statePoti = 0;
  directionChanged_FeedbackFu = 0;
}

void loop() {
  
  // Potentiometer and speed FU
  switch(statePoti){                
    case 0: {    
      analogValue = analogRead(PIN_POTI);  // read the input on analog pin
      value = map(analogValue, 0, 1023, 0, 255);    //Map value 0-1023 to 0-255 (PWM)
      analogWrite(PIN_FREQUENCY,value);            //send PWM Value to FU
    }
    break;
    
    case 1: {
      analogWrite(PIN_FREQUENCY,85); 
    }
    break;
    
    case 2: {
      while(value>100){
        value = value-10;
        analogWrite(PIN_FREQUENCY,value); 
      }
    }
    break;

    default: break;
  }   


  // Stopp - Drive   
  readingDrive = digitalRead(STOPP_SWITCH);
  
  if (readingDrive == LOW && previousDrive == HIGH && ((millis() - TimeOfLastDebounce) > DelayOfDebounce)){
      stateDrive = !stateDrive;
      digitalWrite (PIN_DRIVE, stateDrive);         // turns on the red LED
      TimeOfLastDebounce = millis();
    }
  previousDrive = readingDrive;


  // Colour changer
  readingColourChange = digitalRead(COLOUR_SWITCH);
  
  if (readingColourChange == LOW && previousColourChange == HIGH && ((millis() - TimeOfLastDebounceCol) > DelayOfDebounce)){
      stateColourChange = !stateColourChange;
      digitalWrite (YELLOW_COLOURCHANGE_LED, !stateColourChange);
      digitalWrite (PIN_COLOURCHANGE, stateColourChange);
      TimeOfLastDebounceCol = millis();      
    }
    
  previousColourChange = readingColourChange;


  // Impuls new direction left
  readingRight = digitalRead(DRIVE_RIGHT_SWITCH);

  if (readingRight == LOW && previousRight == HIGH && ((millis() - TimeOfLastDebounceRight) > DelayOfDebounce)) { 
    drive_left();
    TimeOfLastDebounceRight = millis();
    } 
  else { 
    digitalWrite (PIN_DRIVE_RIGHT, LOW);
    }
  previousRight = readingRight;


  // Impuls new direction right 
  readingLeft = digitalRead(DRIVE_LEFT_SWITCH);
     
  if (readingLeft == LOW && previousLeft == HIGH && ((millis() - TimeOfLastDebounceLeft) > DelayOfDebounce)) { 
    drive_right();
    TimeOfLastDebounceLeft = millis();
    }  
  else { 
    digitalWrite (PIN_DRIVE_LEFT, LOW);
    }
  previousLeft = readingLeft;
  

  // Impuls reset 
  readingReset = digitalRead(RESET_SWITCH);
  
  if (readingReset == LOW && previousReset == HIGH && ((millis() - TimeOfLastDebounceReset) > DelayOfDebounce)){
      
      digitalWrite (PIN_RESET, HIGH);         // turns on the blue LED
      TimeOfLastDebounceReset = millis();
    }

  else {
    digitalWrite (PIN_RESET, LOW);
  }
  
  previousReset = readingReset;

  
  readingEndStopp = digitalRead(END_ROW_STOPP_SWITCH);
  
  if (readingEndStopp == LOW && previousEndStopp == HIGH && ((millis() - TimeOfLastDebounceEndStopp) > DelayOfDebounce)){
    stateEndStopp = !stateEndStopp;
    digitalWrite (GREEN_ENDSTOPP_LED, stateEndStopp);         // turns on the yellow LED
    TimeOfLastDebounceEndStopp = millis();
    }
  previousEndStopp = readingEndStopp;

  
  directionChanged_FeedbackFu = 0;
  readingDirectionFu = digitalRead(PIN_DIRECTION_FU);
  
  if(readingDirectionFu != previousDirectionFu){
    stateDirectionFu = !stateDirectionFu;
 
    previousDirectionFu = readingDirectionFu;
    directionChanged_FeedbackFu = 1;
  }

  if (stateEndStopp == HIGH && directionChanged_FeedbackFu == 1){
    stateDrive = LOW;
    digitalWrite (PIN_DRIVE, stateDrive); 
  }

  c.feedinSerialData();
  
}
