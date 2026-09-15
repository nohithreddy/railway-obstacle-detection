package com.railway.control;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

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
