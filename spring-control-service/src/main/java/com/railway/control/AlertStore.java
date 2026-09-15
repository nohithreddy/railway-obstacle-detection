package com.railway.control;

import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class AlertStore {

    private final Map<String, StoredAlert> alertsByEventId = new ConcurrentHashMap<>();
    private final Map<String, EmergencyResponse> emergencyByEventId = new ConcurrentHashMap<>();
    private final List<AuditEntry> auditLog = new CopyOnWriteArrayList<>();

    public StoredAlert save(PortalAlert alert) {
        StoredAlert stored = new StoredAlert(alert, Instant.now());
        alertsByEventId.put(alert.eventId(), stored);
        audit("ALERT_RECEIVED", alert.eventId());
        return stored;
    }

    public StoredAlert findById(String eventId) {
        StoredAlert stored = alertsByEventId.get(eventId);
        if (stored == null) {
            throw new AlertNotFoundException(eventId);
        }
        return stored;
    }

    public List<StoredAlert> list(String trainId) {
        return alertsByEventId.values().stream()
                .filter(stored -> trainId == null || stored.alert().trainId().equals(trainId))
                .sorted(Comparator.comparing(StoredAlert::receivedAt).reversed())
                .toList();
    }

    public EmergencyResponse activateEmergencyResponse(String eventId) {
        findById(eventId);
        EmergencyResponse response = new EmergencyResponse(eventId, "EMERGENCY_RESPONSE_ACTIVATED", Instant.now());
        emergencyByEventId.put(eventId, response);
        audit("EMERGENCY_RESPONSE_ACTIVATED", eventId);
        return response;
    }

    public TrainStatus trainStatus(String trainId) {
        List<StoredAlert> trainAlerts = list(trainId);
        if (trainAlerts.isEmpty()) {
            throw new TrainNotFoundException(trainId);
        }
        StoredAlert latest = trainAlerts.get(0);
        boolean emergencyActive = emergencyByEventId.containsKey(latest.alert().eventId());
        return new TrainStatus(trainId, trainAlerts.size(), emergencyActive, latest);
    }

    public List<AuditEntry> auditLog() {
        return auditLog.reversed();
    }

    private void audit(String action, String resourceId) {
        auditLog.add(new AuditEntry(action, resourceId, Instant.now()));
    }
}
