/*
COMMUNICATONS FUNCTIONS

*/

#include "WiFi.h"
#include "ArduinoJson.h"

void WiFiEvent(WiFiEvent_t event, system_event_info_t info) {

  switch(event){
    case SYSTEM_EVENT_STA_START:
      Serial.println("Station Mode Started");
      break;
      
    case SYSTEM_EVENT_STA_CONNECTED:
        Serial.println("Connected to access point");
        break;

    case SYSTEM_EVENT_STA_GOT_IP:
      Serial.println("Connected to :" + String(WiFi.SSID()));
      Serial.print("Got IP: ");
      Serial.println(WiFi.localIP());
      wifiConnected = true;      
      break;
      
    case SYSTEM_EVENT_STA_DISCONNECTED:
      Serial.println("Disconnected from station, attempting reconnection");
      WiFi.reconnect();
      break;
      
    default:
      break;
  }
}

String getMacStr() {
  
  char buffer[24];
  byte mac[6];                     // the MAC address
  
  WiFi.macAddress(mac);
  sprintf(buffer, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4],mac[5]);
  return buffer;
}


String getIPStr() {
  
  IPAddress ipAddress = WiFi.localIP();
  
  return  String(ipAddress[0]) + String(".") +\
          String(ipAddress[1]) + String(".") +\
          String(ipAddress[2]) + String(".") +\
          String(ipAddress[3])  ; 
}

void scanWiFiNetworks() {

  int numNames=0;

  Serial.println("scan start");

  // WiFi.scanNetworks will return the number of networks found
  numNames = WiFi.scanNetworks();
  Serial.println("scan done");
  if (numNames == 0) {
      Serial.println("no networks found");
  } 
  else {
      Serial.print(numNames);
      Serial.println(" networks found");
      
      for (int i = 0; i < numNames; ++i) {
          // Print SSID and RSSI for each network found
          Serial.print(i + 1);
          Serial.print(": ");
          Serial.print(WiFi.SSID(i));
          Serial.print(" (");
          Serial.print(WiFi.RSSI(i));
          Serial.print(")");
          Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":" LOCKED");
          delay(10);
      }
      
      Serial.println("");
  }

}


void  getGeoLocation() {

  StaticJsonDocument<2000> jDoc;
  
  // get geo location info
  String locStr = "https://ipapi.co/json";
  
  // debug info
  Serial.println("Getting Location: "+locStr);
  String loc = postJsonHTTP(locStr, "");

  // debug
  Serial.println(loc);

  // parse json (need zipcode and timzone)
  DeserializationError error = deserializeJson(jDoc, loc);
  
  // Test if parsing succeeds.
  if (!error) {
    // do something with data - example
    String c = jDoc["city"];
    Serial.println("Welcome to lovely "+c);
  }
  else {
    Serial.println("parseObject() failed");
  }
}


String  postJsonHTTP(String url, String jLoad) {

   HTTPClient httpC;
   String resp="";   
 
   // debug info
   Serial.println("POST: "+url);
   Serial.println("JSON: "+jLoad);

   
   httpC.begin(url);                        //Specify destination for HTTP request
   httpC.addHeader("content-type", "text/plain");

   int httpCode = httpC.POST(jLoad);              //Send the actual POST request
 
   if(httpCode>0){
 
    resp = httpC.getString();    //Get the response to the request
    
    Serial.print("POST Code: ");
    Serial.println(httpCode);   //Print return cbuildBeaconJsonode
    Serial.println(resp);       //Print request answer

   }
   else {
    resp = "ERROR";
    Serial.print("Error on sending POST: ");
    Serial.println(httpCode);
 
   }
 
   httpC.end();  //Free resources

   return resp;
 }
