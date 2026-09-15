package com.railway.control;

import java.time.Instant;

public record AuditEntry(String action, String resourceId, Instant timestamp) {
}
