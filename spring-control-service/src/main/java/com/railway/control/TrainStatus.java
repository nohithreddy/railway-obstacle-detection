package com.railway.control;

public record TrainStatus(String trainId, int totalAlerts, boolean emergencyActive, StoredAlert latestAlert) {
}
