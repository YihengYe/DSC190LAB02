/*
  Group xx

*/

// Global includes
#include <ArduinoJson.h>
#include <Ticker.h>

// wifi comms includes
#include <WiFi.h>
#include <HTTPClient.h>

// BLE Beacon Receiver

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>


// local includes

// check device MAC table to get wifi password
#define MAN_SSID "Mans So HOT"
#define MAN_PSWD "Du83887199"  

// --------------------------------------------------------------------


// --------------------------------------------------------------------

static volatile bool wifiConnected = false;
String localSSID, localPSWD;
String regURL;
String postStr;

static volatile bool tog = false;
static volatile int userCount = 0;
static volatile bool BLEGetTimeout = false;

Ticker ble_scantimer;
const float blescan_period = 10; //seconds

// -------------------------------------------------------

void set_blescan() {
  BLEGetTimeout = true;
}

/*********************** SETUP ******************************/
void setup(){

  // configure the i/o
  Serial.begin(115200);

  delay(50);
  Serial.println("DSC190 IoT Web call example");
  
  WiFi.onEvent(WiFiEvent);
  WiFi.mode(WIFI_MODE_STA);

  scanWiFiNetworks();

  localSSID = MAN_SSID;
  localPSWD = MAN_PSWD;
  
  // setup STA mode
  WiFi.mode(WIFI_MODE_STA);
  Serial.println("Trying SSID: " + localSSID + " (" + localPSWD + ")");

  delay(50);
  // connect to the local wifi
  WiFi.begin(localSSID.c_str(), localPSWD.c_str());

  // show MAC address
  Serial.println();
  Serial.println("my MAC:"+getMacStr());

  // wait till we are connected
  while (!wifiConnected)
      ; 
      
  Serial.println("BLE Initialized");
  initBeacon();
  ble_scantimer.attach(blescan_period, set_blescan);

}

// ------------------------------ MAIN LOOP --------------------------------
void loop(){

String jStr;

    // scan beacons every period
    if (BLEGetTimeout) {
      scanBeacons();
    }

    
    // check if there is data to look at
    if (haveBeaconData()) {
        jStr =  buildBeaconJson();
        Serial.println(jStr);
    }
    
    String lat ="32.8656561";
    String lon= "-117.2378478";
   
    String url = "http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py";
    String devmac = getMacStr();
    String devip=getIPStr();
//    String gid = "3";
    String cmd = "{\"cmd\": \"LOG\", \"devmac\":\""+devmac+"\",\"ip\": \""+devip+"\",\"dev_lat\": \""+lat+"\",\"dev_long\": \""+lon+"\", \"gid\": \"03\"," + jStr +"}";


//    Serial.println(cmd);
      
    String rs=String(WiFi.RSSI());
    String jLOG="\"cmd\": \"LOGDEV\", \"RSSI\":\""+rs+"\", \"mac\":\""+\
              devmac+"\", \"gid\": \"03\"";
    String jLoad2="{"+jLOG+"}";
    postJsonHTTP(url, cmd);
    postJsonHTTP(url, jLoad2);
    delay(10000);
}
