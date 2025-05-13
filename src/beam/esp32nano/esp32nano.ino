#include <WiFi.h>

// wifi credentials here
const char* ssid = "";
const char* password = "";

// esp32 connected to WiFi and starts web server on port 80
WiFiServer server(80);

void setup() {
    delay(1000);

    Serial.begin(9600);
    Serial.print("HERE");

    pinMode(5, INPUT_PULLUP);   // sensor 1 on pin 5

    WiFi.begin(ssid, password);
    Serial.print("Connecting to wifi");

    while (WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }

    Serial.println("WiFI Connected!");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    server.begin();
}

void loop() {
    WiFiClient client = server.accept();
    
    if (client){
        Serial.println("New client.");
        String current_line = "";

        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
                Serial.write(c);
                if (c == '\n') {

                    if (current_line.length() == 0){
                      //end of HTTP request
                      int sensor_1 = digitalRead(5);
  
                      client.println("HTTP/1.1 200 OK");
                      client.println("Content-Type: application/json");
                      client.println();
  
                      client.println("{\"sensor_1\": " + String(sensor_1) + "}");
  
                      break;
                    }
                    else {
                      current_line = "";
                    }
                    
                }
            }
        }
        client.stop();
        Serial.println("Client disconnected");
    }

}