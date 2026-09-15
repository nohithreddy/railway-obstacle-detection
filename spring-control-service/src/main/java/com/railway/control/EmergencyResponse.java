package com.railway.control;

import java.time.Instant;

public record EmergencyResponse(String eventId, String protocol, Instant activatedAt) {
}
