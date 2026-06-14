# AI-Powered Railway Obstacle Detection and Intelligent Train Control System

## Abstract

Railway safety depends on rapid detection of track intrusions and reliable driver assistance. This paper proposes an AI-powered obstacle detection and intelligent control system combining LiDAR, laser sensors, camera vision, thermal imaging, GPS/IMU localization, YOLOv8 object detection, distance estimation, and real-time decision logic. Obstacles are classified as small, medium, or large, and the control response ranges from driver warning to automatic emergency braking.

## Keywords

Railway safety, YOLOv8, LiDAR, obstacle detection, intelligent transport systems, emergency braking, IoT.

## Introduction

Traditional railway inspection and driver visibility are limited by speed, weather, track geometry, and night operation. The proposed system assists train drivers and control rooms by fusing multiple sensors and continuously evaluating collision risk.

## Methodology

The system captures synchronized camera frames, thermal images, LiDAR scans, GPS coordinates, and IMU orientation. YOLOv8 identifies object classes, while LiDAR and stereo depth estimate distance and size. The decision engine calculates risk from object class, confidence, object dimensions, track position, train speed, and time to collision.

## System Design

The architecture contains edge AI processing, railway portal APIs, notification services, event logging, and 3D visualization. Small obstacles generate warnings, medium obstacles request driver decision, and large obstacles trigger emergency braking.

## Expected Results

The expected outcome is reduced driver reaction time, better control-room visibility, structured event logging, and a practical simulation framework for railway obstacle detection research.

## Future Work

Future enhancements include certified brake integration, cooperative train-to-train alerts, sensor redundancy, radar fusion, weather-adaptive perception models, and formal safety validation.
