package com.railway.control;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/portal")
public class PortalAlertController {

    @PostMapping("/alerts")
    public ResponseEntity<Map<String, Object>> receiveAlert(@Valid @RequestBody PortalAlert alert) {
        return ResponseEntity.ok(Map.of(
                "accepted", true,
                "eventId", alert.eventId(),
                "riskLevel", alert.riskLevel(),
                "receivedAt", Instant.now().toString()
        ));
    }

    @PostMapping("/emergency-response/{eventId}")
    public ResponseEntity<Map<String, Object>> activateEmergencyResponse(@PathVariable String eventId) {
        return ResponseEntity.ok(Map.of(
                "eventId", eventId,
                "protocol", "EMERGENCY_RESPONSE_ACTIVATED",
                "activatedAt", Instant.now().toString()
        ));
    }

    public record PortalAlert(
            @NotBlank String eventId,
            @NotBlank String trainId,
            @NotBlank String objectType,
            @NotBlank String riskLevel,
            @NotNull Double latitude,
            @NotNull Double longitude,
            @NotNull Double distanceM,
            @NotBlank String action
    ) {
    }
}
