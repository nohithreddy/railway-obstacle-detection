import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import { Bell, Radio, ShieldAlert, TrainFront, TriangleAlert } from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "";

const demoEvents = [
  {
    event_id: "demo-small",
    reading: { object_type: "debris", distance_m: 145, confidence: 0.84, latitude: 17.385, longitude: 78.4867 },
    decision: { risk_level: "small", action: "WARN_DRIVER", brake_status: "released", message: "Small obstacle detected. Warning issued." },
  },
  {
    event_id: "demo-medium",
    reading: { object_type: "person", distance_m: 82, confidence: 0.93, latitude: 17.386, longitude: 78.4872 },
    decision: { risk_level: "medium", action: "REQUEST_DRIVER_DECISION", brake_status: "released", message: "Driver decision required." },
  },
  {
    event_id: "demo-large",
    reading: { object_type: "truck", distance_m: 48, confidence: 0.96, latitude: 17.387, longitude: 78.4878 },
    decision: { risk_level: "large", action: "AUTO_BRAKE", brake_status: "applied", message: "Emergency brake applied." },
  },
];

function riskColor(risk) {
  return { small: "#f2c94c", medium: "#f2994a", large: "#eb5757" }[risk] || "#8fd6ff";
}

function TrackScene({ events }) {
  const latest = events[events.length - 1] || demoEvents[0];
  const markers = events.slice(-8).map((event, index) => ({
    ...event,
    z: -Math.min(event.reading.distance_m / 8, 34),
    x: (index % 3 - 1) * 0.55,
  }));

  return (
    <Canvas camera={{ position: [0, 8, 12], fov: 50 }}>
      <color attach="background" args={["#071014"]} />
      <ambientLight intensity={0.55} />
      <directionalLight position={[5, 9, 5]} intensity={1.2} />
      <mesh position={[0, -0.08, -12]}>
        <boxGeometry args={[3.2, 0.08, 44]} />
        <meshStandardMaterial color="#1d2b2f" />
      </mesh>
      {[-0.9, 0.9].map((x) => (
        <mesh key={x} position={[x, 0.06, -12]}>
          <boxGeometry args={[0.12, 0.16, 44]} />
          <meshStandardMaterial color="#c9d6d2" metalness={0.4} roughness={0.35} />
        </mesh>
      ))}
      {Array.from({ length: 18 }).map((_, i) => (
        <mesh key={i} position={[0, 0.02, 8 - i * 2.4]}>
          <boxGeometry args={[2.4, 0.08, 0.18]} />
          <meshStandardMaterial color="#5e6f68" />
        </mesh>
      ))}
      <mesh position={[0, 0.55, 5.4]}>
        <boxGeometry args={[1.25, 0.8, 2.2]} />
        <meshStandardMaterial color="#2f80ed" />
      </mesh>
      <Text position={[0, 1.25, 5.4]} fontSize={0.28} color="#ffffff">TRAIN-001</Text>
      <mesh position={[0, 0.02, -10]}>
        <ringGeometry args={[3.4, 3.45, 64]} />
        <meshBasicMaterial color="#27ae60" transparent opacity={0.35} />
      </mesh>
      <mesh position={[0, 0.025, -18]}>
        <ringGeometry args={[5.4, 5.45, 64]} />
        <meshBasicMaterial color="#f2c94c" transparent opacity={0.28} />
      </mesh>
      <mesh position={[0, 0.03, -26]}>
        <ringGeometry args={[7.2, 7.25, 64]} />
        <meshBasicMaterial color="#eb5757" transparent opacity={0.24} />
      </mesh>
      {markers.map((event) => (
        <group key={event.event_id} position={[event.x, 0.5, event.z]}>
          <mesh>
            <sphereGeometry args={[0.38, 32, 16]} />
            <meshStandardMaterial color={riskColor(event.decision.risk_level)} emissive={riskColor(event.decision.risk_level)} emissiveIntensity={0.3} />
          </mesh>
          <Text position={[0, 0.75, 0]} fontSize={0.22} color="#ffffff">
            {event.reading.object_type}
          </Text>
        </group>
      ))}
      <Text position={[-3.2, 0.25, -32]} fontSize={0.24} color={riskColor(latest.decision.risk_level)}>
        {latest.decision.action}
      </Text>
      <OrbitControls enablePan={false} minDistance={7} maxDistance={20} />
    </Canvas>
  );
}

function App() {
  const [events, setEvents] = useState(demoEvents);
  const latest = events[events.length - 1];
  const riskCounts = useMemo(
    () => events.reduce((acc, event) => ({ ...acc, [event.decision.risk_level]: (acc[event.decision.risk_level] || 0) + 1 }), {}),
    [events]
  );

  useEffect(() => {
    if (!API_URL) return undefined;

    const timer = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/events`);
        if (response.ok) {
          const data = await response.json();
          if (data.length) setEvents(data);
        }
      } catch {
        setEvents((current) => current);
      }
    }, 1500);
    return () => clearInterval(timer);
  }, []);

  return (
    <main>
      <aside>
        <div className="brand"><TrainFront size={26} /> Railway Control</div>
        <section className="status">
          <div><Radio size={18} /> Live telemetry</div>
          <strong>{latest.reading.object_type}</strong>
          <span>{latest.reading.distance_m}m ahead | {(latest.reading.confidence * 100).toFixed(0)}% confidence</span>
        </section>
        <section className={`risk ${latest.decision.risk_level}`}>
          <ShieldAlert size={24} />
          <div>
            <span>Risk</span>
            <strong>{latest.decision.risk_level.toUpperCase()}</strong>
          </div>
        </section>
        <div className="metrics">
          <div><span>Small</span><strong>{riskCounts.small || 0}</strong></div>
          <div><span>Medium</span><strong>{riskCounts.medium || 0}</strong></div>
          <div><span>Large</span><strong>{riskCounts.large || 0}</strong></div>
        </div>
        <section className="action">
          <TriangleAlert size={20} />
          <p>{latest.decision.message}</p>
          <button>{latest.decision.brake_status === "applied" ? "Brake Applied" : "Acknowledge"}</button>
        </section>
      </aside>
      <section className="visual">
        <TrackScene events={events} />
      </section>
      <aside className="events">
        <div className="panel-title"><Bell size={18} /> Event Log</div>
        {events.slice(-8).reverse().map((event) => (
          <article key={event.event_id}>
            <b>{event.reading.object_type}</b>
            <span>{event.decision.risk_level} | {event.decision.action}</span>
            <small>{event.reading.latitude}, {event.reading.longitude}</small>
          </article>
        ))}
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
