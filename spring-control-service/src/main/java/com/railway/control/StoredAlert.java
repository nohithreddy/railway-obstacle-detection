package com.railway.control;

import java.time.Instant;

public record StoredAlert(PortalAlert alert, Instant receivedAt) {
}
