import { useMemo } from "react";

function GaitTimeline({ frames = [], activeId, onSelect, eventMarkers = {}, text }) {
  const maxFrame = useMemo(() => {
    if (!frames.length) return 1;
    return Math.max(...frames.map((f) => Number(f.frame_index || 0)), 1);
  }, [frames]);

  if (!frames.length) return null;

  return (
    <div className="timeline-wrap">
      <div className="timeline-head">
        <strong>{text.timelineTitle || "Gait Timeline"}</strong>
        <span className="muted">{text.timelineHint || "Tap a marker/frame to inspect angles"}</span>
      </div>
      <div className="timeline-track">
        {frames.map((f) => {
          const left = `${((Number(f.frame_index || 0) / maxFrame) * 100).toFixed(2)}%`;
          const eventType = getEventType(Number(f.frame_index || 0), eventMarkers);
          return (
            <button
              key={f.id}
              className={`timeline-dot ${activeId === f.id ? "active" : ""} ${eventType}`}
              style={{ left }}
              onClick={() => onSelect(f.id)}
              title={`${text.frameLabel || "Frame"} ${f.frame_index}`}
            />
          );
        })}
      </div>
      <div className="timeline-legend">
        <span><i className="dot heel" /> {text.heelStrike || "Heel Strike"}</span>
        <span><i className="dot mid" /> {text.midStance || "Mid Stance"}</span>
        <span><i className="dot toe" /> {text.toeOff || "Toe Off"}</span>
      </div>
    </div>
  );
}

function getEventType(frame, markers) {
  if (markers?.initial_contact === frame) return "heel";
  if (markers?.mid_stance === frame) return "mid";
  if (markers?.toe_off === frame) return "toe";
  return "plain";
}

export default GaitTimeline;
