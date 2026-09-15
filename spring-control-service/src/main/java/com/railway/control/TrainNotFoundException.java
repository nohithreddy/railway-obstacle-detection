package com.railway.control;

public class TrainNotFoundException extends RuntimeException {
    public TrainNotFoundException(String trainId) {
        super("No alerts recorded for trainId=" + trainId);
    }
}
