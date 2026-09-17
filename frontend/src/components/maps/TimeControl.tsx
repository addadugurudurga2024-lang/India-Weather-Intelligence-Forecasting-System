import React, { useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Calendar,
  Zap
} from 'lucide-react';

interface TimeControlProps {
  dates: string[];
  selectedDate: string;
  onDateChange: (date: string) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  speedMs: number;
  onSpeedChange: (speedMs: number) => void;
  isForecast?: boolean;
}

export const TimeControl: React.FC<TimeControlProps> = ({
  dates,
  selectedDate,
  onDateChange,
  isPlaying,
  onTogglePlay,
  speedMs,
  onSpeedChange,
  isForecast = false
}) => {
  const timerRef = useRef<number | null>(null);

  const currentIndex = dates.indexOf(selectedDate);
  const safeIndex = currentIndex >= 0 ? currentIndex : dates.length - 1;

  // Animation cycle
  useEffect(() => {
    if (!isPlaying || dates.length <= 1) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = window.setInterval(() => {
      const nextIdx = (safeIndex + 1) % dates.length;
      onDateChange(dates[nextIdx]);
    }, speedMs);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, safeIndex, dates, speedMs, onDateChange]);

  const handlePrev = () => {
    if (safeIndex > 0) {
      onDateChange(dates[safeIndex - 1]);
    } else {
      onDateChange(dates[dates.length - 1]);
    }
  };

  const handleNext = () => {
    if (safeIndex < dates.length - 1) {
      onDateChange(dates[safeIndex + 1]);
    } else {
      onDateChange(dates[0]);
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const idx = parseInt(e.target.value, 10);
    if (idx >= 0 && idx < dates.length) {
      onDateChange(dates[idx]);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)',
      background: 'var(--bg-surface-glass)',
      backdropFilter: 'blur(12px)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-3) var(--space-4)',
      boxShadow: 'var(--shadow-md)',
      width: '100%',
      maxWidth: '620px'
    }}>
      {/* Top row: Date indicator and playback controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Calendar size={16} style={{ color: isForecast ? 'var(--accent-warning)' : 'var(--accent-primary)' }} />
          <span style={{ fontSize: 'var(--font-sm)', fontWeight: 800, color: 'var(--text-primary)' }}>
            {selectedDate}
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
            Day {safeIndex + 1} of {dates.length}
          </span>
          {isForecast && (
            <span className="badge badge-warning" style={{ fontSize: '10px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Zap size={10} /> Holdout Forecast
            </span>
          )}
        </div>

        {/* Play / Step buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            onClick={handlePrev}
            className="btn btn-secondary btn-icon"
            style={{ width: '28px', height: '28px', padding: 0 }}
            title="Previous Day"
            aria-label="Previous Day"
          >
            <ChevronLeft size={16} />
          </button>

          <button
            onClick={onTogglePlay}
            className={`btn ${isPlaying ? 'btn-primary' : 'btn-secondary'}`}
            style={{
              padding: '4px 12px',
              fontSize: 'var(--font-xs)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              height: '28px'
            }}
            title={isPlaying ? 'Pause Animation' : 'Play Temporal Animation'}
            aria-label={isPlaying ? 'Pause Animation' : 'Play Temporal Animation'}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            <span>{isPlaying ? 'Pause' : 'Animate'}</span>
          </button>

          <button
            onClick={handleNext}
            className="btn btn-secondary btn-icon"
            style={{ width: '28px', height: '28px', padding: 0 }}
            title="Next Day"
            aria-label="Next Day"
          >
            <ChevronRight size={16} />
          </button>

          <button
            onClick={() => onDateChange(dates[0])}
            className="btn btn-ghost btn-icon"
            style={{ width: '28px', height: '28px', padding: 0 }}
            title="Reset to First Date"
            aria-label="Reset to First Date"
          >
            <RotateCcw size={14} />
          </button>

          {/* Speed selector */}
          <div style={{ display: 'flex', gap: '2px', marginLeft: '6px', borderLeft: '1px solid var(--border-subtle)', paddingLeft: '8px' }}>
            {[
              { label: '1x', ms: 1200 },
              { label: '2x', ms: 600 },
              { label: '4x', ms: 300 }
            ].map((sp) => (
              <button
                key={sp.label}
                onClick={() => onSpeedChange(sp.ms)}
                style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '2px 5px',
                  borderRadius: '3px',
                  border: '1px solid',
                  borderColor: speedMs === sp.ms ? 'var(--accent-primary)' : 'var(--border-subtle)',
                  background: speedMs === sp.ms ? 'var(--accent-primary)' : 'transparent',
                  color: speedMs === sp.ms ? '#fff' : 'var(--text-tertiary)',
                  cursor: 'pointer'
                }}
              >
                {sp.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Date scrubber slider */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', minWidth: '60px' }}>
          {dates[0]}
        </span>
        <input
          type="range"
          min="0"
          max={dates.length - 1}
          value={safeIndex}
          onChange={handleSliderChange}
          style={{
            flex: 1,
            accentColor: isForecast ? 'var(--accent-warning)' : 'var(--accent-primary)',
            cursor: 'pointer',
            height: '6px'
          }}
          aria-label="Timeline scrubber"
        />
        <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', minWidth: '60px', textAlign: 'right' }}>
          {dates[dates.length - 1]}
        </span>
      </div>
    </div>
  );
};
