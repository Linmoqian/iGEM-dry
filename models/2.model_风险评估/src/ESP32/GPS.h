/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#pragma once

void gpsInit(unsigned long baudRate, int rxPin, int txPin);
bool readGps(double& latitudeDeg, double& longitudeDeg);
