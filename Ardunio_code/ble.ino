// Global includes
#include <ArduinoJson.h>

// BLE Beacon Receiver
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include "BLEBeacon.h"

//#define BLE_VERBOSE // used to print operational messages

BLEScan* pBLEScan;

uint16_t beconUUID = 0xFEAA;
#define ENDIAN_CHANGE_U16(x) ((((x)&0xFF00)>>8) + (((x)&0xFF)<<8))

String beaconJsonArray="";

int beaconCount=0;
int beaconValidCount=0;
int beaconScanCount=0;
int BeaconScanTime=1;   // seconds


#define MAX_BEACON_JSON 10  // maximum 10 packet send at once

//--------------- number of beacon records in json ----------------
int haveBeaconData() {
  return beaconValidCount;
}

//--------------- setup the JSON ooutput string header ----------------
void buildBeaconJsonHeader() {
  beaconJsonArray = "\"beacons\": [";
//  beaconJsonArray = "[";
}

//--------------- complete the JSON ooutput string block ----------------
String buildBeaconJson() {

  String tmp;

  beaconJsonArray += "]";
  
  // reset array
  beaconValidCount=0;
  
  return beaconJsonArray;
}

//------------------- BLE CALLBACK -------------------

class anaAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      
        //Serial.printf("\nAdv Dev: %s \n", advertisedDevice.toString().c_str());
        
        beaconCount++;
        
        String jBeacon = parseBeacon(advertisedDevice);

        // if valid beacon add it to our list
        if (jBeacon.length()>0) {

            // make sure we have a header at the least
            if (beaconValidCount==0) {
                // reset array
                buildBeaconJsonHeader();
            }
            else {
              // continue the array
              beaconJsonArray += ",";
            }
            
            // add json string to our array
            beaconJsonArray += jBeacon;
            beaconValidCount++;
        }
    }
};


String hexToString(uint8_t *buff,int len) {

    char hexchars[] = "0123456789ABCDEF";
    
    String retval="";
    
    for (int i=0;i<len;i++) {
        retval += hexchars[buff[i]>>4];
        retval += hexchars[buff[i]&0x0F];
    }

    return retval;
}

String  parseBeacon(BLEAdvertisedDevice dev) {

      bool validBeacon=false;

      // vars used in building json object
      StaticJsonDocument<400> jBLEDoc;
      char jChar[800] = "";

      // clear the json object
      jBLEDoc.clear();
      
      jBLEDoc["mac"] = String(dev.getAddress().toString().c_str());  // get the beacon mac addr
      jBLEDoc["rssi"] = String(dev.getRSSI());    // record rssi power

#ifdef BLE_VERBOSE  
      String macStr = "[" + String(dev.getAddress().toString().c_str()) + "]: ";
      Serial.print(macStr);
#endif
      std::string strServiceData = dev.getServiceData();
      uint8_t cServiceData[100];
      strServiceData.copy((char *)cServiceData, strServiceData.length(), 0);

//      debug
//      Serial.println("Payload: "+hexToString(cServiceData,strServiceData.length()));
//      Serial.println("ServiceUUID: "+String(dev.getServiceDataUUID().toString().c_str()));
//      Serial.print("Name:");
//      Serial.print(String(dev.getName().c_str()));
//      Serial.print(" RSSI:");
//      Serial.println(dev.getRSSI(););
      
      if (dev.getServiceDataUUID().equals(BLEUUID(beconUUID))==true) {  // found Eddystone UUID

          //jBLEDoc["serviceUUID"] = String(dev.getServiceDataUUID().toString().c_str());
          //jBLEDoc["payload"] = hexToString(cServiceData,strServiceData.length());
#ifdef BLE_VERBOSE  
        Serial.println("Eddystone-Payload: "+hexToString(cServiceData,strServiceData.length()));
#endif
          // later we move this part to the cloud too
          switch(cServiceData[0]) {
            
              case 0x00:
                  jBLEDoc["msgtype"] = "Eddystone-UID";
                  validBeacon=true;
                  break;
              case 0x10: // not supported for now
                  jBLEDoc["msgtype"] = "Eddystone-URL";
                  validBeacon=true;
                  break;
              case 0x20:
                  jBLEDoc["msgtype"] = "Eddystone-TLM";
                  validBeacon=true;
                  break;
              default:
                  jBLEDoc["msgtype"] = "ERROR UUID";
          }

       } 
       
       else { // not Eddystone
        
        if (dev.haveManufacturerData()==true) {
          std::string strManufacturerData = dev.getManufacturerData();
          
          uint8_t cManufacturerData[100];
          strManufacturerData.copy((char *)cManufacturerData, strManufacturerData.length(), 0);
#ifdef BLE_VERBOSE  
          Serial.println("Man-Payload: "+hexToString(cManufacturerData,strManufacturerData.length()));
#endif          
          // is it iBeacon ?
//          if (strManufacturerData.length()==25 && cManufacturerData[0] == 0x4C  && cManufacturerData[1] == 0x00 ) {
          if (cManufacturerData[0] == 0x4C  && cManufacturerData[1] == 0x00 ) { // look for APPLE ID
            //jBLEDoc["payload"] = hexToString(cManufacturerData,strManufacturerData.length());
            jBLEDoc["msgtype"] = "iBeacon";
            validBeacon=true;
/*            
            BLEBeacon oBeacon = BLEBeacon();
            oBeacon.setData(strManufacturerData);
            Serial.printf("ID: %04X Major: %d Minor: %d UUID: %s Power: %d\n",oBeacon.getManufacturerId(),ENDIAN_CHANGE_U16(oBeacon.getMajor()),ENDIAN_CHANGE_U16(oBeacon.getMinor()),oBeacon.getProximityUUID().toString().c_str(),oBeacon.getSignalPower());
*/            
          } 
         } 
         
         else {
#ifdef BLE_VERBOSE  
           Serial.printf("No Beacon Advertised ServiceDataUUID: %d %s \n", dev.getServiceDataUUID().bitSize(), dev.getServiceDataUUID().toString().c_str());
#endif           
         }
     }

     if (validBeacon) {
          serializeJson(jBLEDoc, jChar); 
#ifdef BLE_VERBOSE  
          Serial.printf("BLE JSON (%d): %s\n",jBLEDoc.memoryUsage(),jChar);
#endif         
     }
     
     return String(jChar);
}


void initBeacon() {
      // Initialize the BLE driver and configure the callback
      BLEDevice::init("");
      pBLEScan = BLEDevice::getScan(); //create new scan
      pBLEScan->setAdvertisedDeviceCallbacks(new anaAdvertisedDeviceCallbacks(),true); // we want duplicates
      pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
      pBLEScan->setInterval(100); //msec
      pBLEScan->setWindow(99);  // msec less or equal setInterval value
}


void scanBeacons() {

      BLEScanResults foundDevices = pBLEScan->start(BeaconScanTime, false);

      beaconScanCount = foundDevices.getCount();
#ifdef BLE_VERBOSE  
      Serial.print("Devices found: ");
      Serial.print(beaconScanCount);
      Serial.println(" Scan done!");
#endif      
      pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory
      BLEGetTimeout=false;
}
