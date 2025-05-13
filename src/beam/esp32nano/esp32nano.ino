#include <WiFi.h>

const char* ssid = "SSIDHERE";
const char* password = "PASSWORDHERE";

WiFiServer server(80);

void setup() {
    
    Serial.begin(9600);
    pinMode(5, INPUT_PULLUP);   // sensor 1

    WiFi.begin(ssid, password);
    Serial.print("Connecting to wifi");

    while (Wifi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".")
    }

    Serial.println("\nConnected!");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    server.being();
}

void loop() {
    WiFiClient client = server.available();
    if (client){
        Serial.println("new client connected.");
        String current_line = "";

        while (client.connected()) {
            if (client.available()) {
                char c = client.read();

                if (c == '\n') {
                    //end of HTTP request
                    int sensor_1 = digitalRead(5);

                    client.println("HTTP/1.1 200 OK");
                    client.println("Content-Type: application/json");
                    client.println();

                    client.println("{\"sensor_1\": " + String(sensor_1) + "}");

                    break;
                }
            }
        }
        delay(1);
        client.stop();
        Serial.println("client disconnected")
    }

}