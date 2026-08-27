/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#include <Arduino.h>
#include <cstdlib>
#include <cstring>
#include "GPS.h"

static HardwareSerial gpsSerial(1);

static bool hasValidChecksum(const char* sentence) {
    const char* checksum = strchr(sentence, '*');
    if (sentence[0] != '$' || checksum == nullptr || strlen(checksum) < 3) {
        return false;
    }

    uint8_t value = 0;
    for (const char* current = sentence + 1; current < checksum; ++current) {
        value ^= static_cast<uint8_t>(*current);
    }
    return value == strtoul(checksum + 1, nullptr, 16);
}

static bool parseCoordinate(const char* text, char direction, double& result) {
    char* end = nullptr;
    const double raw = strtod(text, &end);
    if (end == text || *end != '\0') {
        return false;
    }

    const int degrees = static_cast<int>(raw / 100.0);
    const double minutes = raw - degrees * 100.0;
    if (minutes >= 60.0) {
        return false;
    }

    result = degrees + minutes / 60.0;
    if (direction == 'S' || direction == 'W') {
        result = -result;
    }
    return true;
}

static bool parseRmc(const char* sentence, double& latitudeDeg, double& longitudeDeg) {
    char messageType[6] = {};
    char status = 'V';
    char latitude[16] = {};
    char latitudeDirection = '\0';
    char longitude[16] = {};
    char longitudeDirection = '\0';

    const int fields = sscanf(
        sentence,
        "$%5[^,],%*[^,],%c,%15[^,],%c,%15[^,],%c",
        messageType,
        &status,
        latitude,
        &latitudeDirection,
        longitude,
        &longitudeDirection
    );
    if (
        fields != 6 || strcmp(messageType + 2, "RMC") != 0 || status != 'A'
        || (latitudeDirection != 'N' && latitudeDirection != 'S')
        || (longitudeDirection != 'E' && longitudeDirection != 'W')
    ) {
        return false;
    }

    return hasValidChecksum(sentence)
        && parseCoordinate(latitude, latitudeDirection, latitudeDeg)
        && parseCoordinate(longitude, longitudeDirection, longitudeDeg)
        && latitudeDeg >= -90.0 && latitudeDeg <= 90.0
        && longitudeDeg >= -180.0 && longitudeDeg <= 180.0;
}

void gpsInit(unsigned long baudRate, int rxPin, int txPin) {
    gpsSerial.begin(baudRate, SERIAL_8N1, rxPin, txPin);
    gpsSerial.setTimeout(20);
}

bool readGps(double& latitudeDeg, double& longitudeDeg) {
    while (gpsSerial.available() > 0) {
        char sentence[96];
        const size_t length = gpsSerial.readBytesUntil('\n', sentence, sizeof(sentence) - 1);
        sentence[length] = '\0';
        if (parseRmc(sentence, latitudeDeg, longitudeDeg)) {
            return true;
        }
    }
    return false;
}
