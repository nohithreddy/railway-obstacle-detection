package com.railway.control;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/portal")
public class PortalAlertController {

    private final AlertStore alertStore;

    public PortalAlertController(AlertStore alertStore) {
        this.alertStore = alertStore;
    }

    @PostMapping("/alerts")
    public ResponseEntity<Map<String, Object>> receiveAlert(@Valid @RequestBody PortalAlert alert) {
        StoredAlert stored = alertStore.save(alert);
        return ResponseEntity.ok(Map.of(
                "accepted", true,
                "eventId", alert.eventId(),
                "riskLevel", alert.riskLevel(),
                "receivedAt", stored.receivedAt().toString()
        ));
    }

    @GetMapping("/alerts")
    public List<StoredAlert> listAlerts(@RequestParam(required = false) String trainId) {
        return alertStore.list(trainId);
    }

    @GetMapping("/alerts/{eventId}")
    public StoredAlert getAlert(@PathVariable String eventId) {
        return alertStore.findById(eventId);
    }

    @PostMapping("/emergency-response/{eventId}")
    public ResponseEntity<EmergencyResponse> activateEmergencyResponse(@PathVariable String eventId) {
        return ResponseEntity.ok(alertStore.activateEmergencyResponse(eventId));
    }

    @GetMapping("/trains/{trainId}/status")
    public TrainStatus trainStatus(@PathVariable String trainId) {
        return alertStore.trainStatus(trainId);
    }

    @GetMapping("/audit-log")
    public List<AuditEntry> auditLog() {
        return alertStore.auditLog();
    }
}
