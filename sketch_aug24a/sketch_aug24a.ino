#include <ESP8266WiFi.h>
int led1=5;

#define SendKey 0  

int port = 8888; 
WiFiServer server(port);

//Server connect to WiFi Network
const char *ssid = "DUONG VIP";  //Enter your wifi SSID
const char *password = "khongbiet";  //Enter your wifi Password

int count=0;
void setup() 
{
  Serial.begin(115200);
  pinMode(SendKey,INPUT_PULLUP);
  pinMode(led1,OUTPUT);
  Serial.println();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi
 
  // Wait for connection
  Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    delay(500);
  }

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
  Serial.print("Open Telnet and connect to IP:");
  Serial.print(WiFi.localIP());
  Serial.print(" on port ");
  Serial.println(port);
}


void loop() 
{
  WiFiClient client = server.available();

  if (client) {
    if(client.connected())
    {
      Serial.println("Client Connected");
    }

    while(client.connected()){
      while(client.available()>0){
        // read data from the connected client
       Serial.write(client.read());
       
        char c =client.read();
      
        if(c=='1'){
        digitalWrite(led1,HIGH);
        }
       if(c=='0'){
       digitalWrite(led1,LOW); 
    }
      
      }
    }
  }
    client.stop();   
  }
