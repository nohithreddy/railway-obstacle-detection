package com.railway.control;

public class AlertNotFoundException extends RuntimeException {
    public AlertNotFoundException(String eventId) {
        super("No alert found for eventId=" + eventId);
    }
}
