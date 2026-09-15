package com.railway.control;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class PortalAlertControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private String alertJson(String eventId, String trainId) throws Exception {
        return objectMapper.writeValueAsString(new PortalAlert(
                eventId, trainId, "person", "medium", 17.385, 78.4867, 72.5, "REQUEST_DRIVER_DECISION"
        ));
    }

    @Test
    void acceptsValidAlertAndAllowsLookup() throws Exception {
        mockMvc.perform(post("/api/portal/alerts")
                        .contentType("application/json")
                        .content(alertJson("evt-1", "TRAIN-001")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accepted").value(true))
                .andExpect(jsonPath("$.eventId").value("evt-1"));

        mockMvc.perform(get("/api/portal/alerts/evt-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.alert.trainId").value("TRAIN-001"));
    }

    @Test
    void rejectsInvalidAlert() throws Exception {
        String invalid = """
                {"trainId": "TRAIN-001", "objectType": "person"}
                """;
        mockMvc.perform(post("/api/portal/alerts")
                        .contentType("application/json")
                        .content(invalid))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("validation_failed"));
    }

    @Test
    void returnsNotFoundForUnknownAlert() throws Exception {
        mockMvc.perform(get("/api/portal/alerts/does-not-exist"))
                .andExpect(status().isNotFound());
    }

    @Test
    void activatesEmergencyResponseAndReflectsInTrainStatus() throws Exception {
        mockMvc.perform(post("/api/portal/alerts")
                .contentType("application/json")
                .content(alertJson("evt-2", "TRAIN-002")));

        mockMvc.perform(post("/api/portal/emergency-response/evt-2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.protocol").value("EMERGENCY_RESPONSE_ACTIVATED"));

        mockMvc.perform(get("/api/portal/trains/TRAIN-002/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.emergencyActive").value(true))
                .andExpect(jsonPath("$.totalAlerts").value(1));
    }

    @Test
    void emergencyResponseForUnknownEventReturnsNotFound() throws Exception {
        mockMvc.perform(post("/api/portal/emergency-response/missing-event"))
                .andExpect(status().isNotFound());
    }

    @Test
    void unknownTrainStatusReturnsNotFound() throws Exception {
        mockMvc.perform(get("/api/portal/trains/UNKNOWN-TRAIN/status"))
                .andExpect(status().isNotFound());
    }
}
