int photodiodePin = A4;     // Pin connected to photodiode
int ledPin = 9;             // Pin connected to LED
float faultThreshold = 3.0; // Voltage threshold for fault detection
unsigned long faultStartTime = 0; // Time when voltage goes below threshold
bool faultDetected = false;

void setup() {
  Serial.begin(9600);       // Start Serial output at 9600 baud rate
  pinMode(ledPin, OUTPUT);  // Set LED pin as an output
  digitalWrite(ledPin, HIGH); // Turn LED on at start
  Serial.println("\nVoltage(V):");
  Serial.println("--------------------------------------------------");
}

void loop() {
    int anaValue = analogRead(photodiodePin);  // Read photodiode value
    float voltage = 5 - (anaValue / 1024.0) * 5;  // Convert value to voltage
    Serial.println(String(voltage, 2) + "V");     // Print voltage to Serial Monitor

    // Check if voltage is below the fault threshold
    if (voltage < faultThreshold) {
        if (faultStartTime == 0) {
            faultStartTime = millis(); // Record the current time
        } 
        else if (millis() - faultStartTime >= 30000) {  // Check for 5 minutes (300000 ms)
            if (!faultDetected) {
                Serial.println("Fault Detected: Voltage below threshold for 10 minutes");
                Serial.println("SEND_EMAIL");  // Signal the computer to send an email
                faultDetected = true;  // Mark fault as detected
            }
        }
    } else {
        if (faultDetected) {
            Serial.println("Fault Cleared: Voltage above threshold, restarting monitoring.");
            faultDetected = false; // Reset fault detection flag
        }
        faultStartTime = 0; // Reset fault detection timer
    }

    delay(2000);  // Wait for 2 seconds before taking the next reading
}
