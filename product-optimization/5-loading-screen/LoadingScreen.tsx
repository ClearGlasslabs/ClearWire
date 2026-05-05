import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

type Props = {
  brand?: string;
  monogram?: string;
  durationMs?: number;
  onComplete?: () => void;
};

const STATUS_LINES = [
  "AUTH :: handshake",
  "KERNEL :: secure-boot",
  "INTEL :: streams sync",
  "OPS :: runtime ready",
];

const HEADER_TAGS = [
  "SYS-ID 7741",
  "CLASSIFIED // INTERNAL",
  "CHANNEL 04",
];

export default function LoadingScreen({
  brand = "CLEARGLASS",
  monogram = "CG",
  durationMs = 4200,
  onComplete,
}: Props) {
  const [progress, setProgress] = useState(0);
  const [statusIdx, setStatusIdx] = useState(0);
  const [now, setNow] = useState(() => new Date());
  const reduce = useReducedMotion();

  useEffect(() => {
    const start = performance.now();
    let raf = 0;
    const tick = (t: number) => {
      const elapsed = t - start;
      const eased = easeOutQuart(Math.min(elapsed / durationMs, 1));
      setProgress(eased * 100);
      if (elapsed < durationMs) {
        raf = requestAnimationFrame(tick);
      } else {
        onComplete?.();
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [durationMs, onComplete]);

  useEffect(() => {
    const id = setInterval(() => {
      setStatusIdx((i) => (i + 1) % STATUS_LINES.length);
      setNow(new Date());
    }, 900);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={`${brand} initializing, ${Math.round(progress)} percent`}
      className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-[#050507] font-mono text-neutral-300 selection:bg-red-600/40"
    >
      <BackdropGrid />
      <ScanLine reduce={!!reduce} />
      <Vignette />

      <header className="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between px-6 py-5 text-[10px] tracking-[0.35em] text-neutral-500 sm:px-10">
        <span className="text-red-500/80">{brand}</span>
        <span className="hidden gap-6 sm:flex">
          {HEADER_TAGS.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </span>
        <time
          dateTime={now.toISOString()}
          className="tabular-nums text-neutral-500"
        >
          {fmtTime(now)}
        </time>
      </header>

      <main className="relative flex flex-col items-center">
        <HexLogo monogram={monogram} reduce={!!reduce} />

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="mt-10 text-center"
        >
          <div className="text-[10px] tracking-[0.6em] text-neutral-500">
            INITIALIZING
          </div>
          <div className="mt-2 text-sm tracking-[0.25em] text-neutral-200">
            SECURE INTELLIGENCE RUNTIME
          </div>
        </motion.div>

        <ProgressBar value={progress} />

        <div className="mt-3 flex h-4 items-center gap-3 text-[10px] tracking-[0.3em] text-neutral-500">
          <span className="tabular-nums text-red-500">
            {progress.toFixed(1).padStart(5, "0")}%
          </span>
          <span className="h-px w-6 bg-neutral-700" />
          <motion.span
            key={statusIdx}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="text-neutral-400"
          >
            {STATUS_LINES[statusIdx]}
          </motion.span>
        </div>
      </main>

      <footer className="pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between px-6 py-5 text-[10px] tracking-[0.35em] text-neutral-600 sm:px-10">
        <span>NODE 04 / SECTOR 7</span>
        <span className="hidden sm:block">
          ENC AES-256 · CHANNEL VERIFIED
        </span>
        <span className="text-red-500/80">OPERATIONAL</span>
      </footer>
    </div>
  );
}

function HexLogo({
  monogram,
  reduce,
}: {
  monogram: string;
  reduce: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
      className="relative h-44 w-44 sm:h-56 sm:w-56"
    >
      <motion.div
        animate={
          reduce
            ? undefined
            : { rotate: 360, transition: { duration: 24, repeat: Infinity, ease: "linear" } }
        }
        className="absolute inset-0"
      >
        <svg viewBox="0 0 200 200" className="h-full w-full">
          <defs>
            <radialGradient id="hexGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(255,40,60,0.45)" />
              <stop offset="60%" stopColor="rgba(255,40,60,0.08)" />
              <stop offset="100%" stopColor="rgba(255,40,60,0)" />
            </radialGradient>
          </defs>
          <circle cx="100" cy="100" r="92" fill="url(#hexGlow)" />
          <polygon
            points="100,12 178,55 178,145 100,188 22,145 22,55"
            fill="none"
            stroke="rgba(255,40,60,0.65)"
            strokeWidth="1"
          />
          <polygon
            points="100,28 165,62 165,138 100,172 35,138 35,62"
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="1"
          />
          {Array.from({ length: 6 }).map((_, i) => {
            const a = (Math.PI / 3) * i - Math.PI / 2;
            const x = 100 + Math.cos(a) * 92;
            const y = 100 + Math.sin(a) * 92;
            return (
              <line
                key={i}
                x1="100"
                y1="100"
                x2={x}
                y2={y}
                stroke="rgba(255,40,60,0.08)"
                strokeWidth="1"
              />
            );
          })}
        </svg>
      </motion.div>

      <motion.div
        animate={
          reduce
            ? undefined
            : { rotate: -360, transition: { duration: 36, repeat: Infinity, ease: "linear" } }
        }
        className="absolute inset-3"
      >
        <svg viewBox="0 0 200 200" className="h-full w-full">
          <circle
            cx="100"
            cy="100"
            r="78"
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="1"
            strokeDasharray="2 6"
          />
          <circle
            cx="100"
            cy="100"
            r="78"
            fill="none"
            stroke="rgba(255,40,60,0.6)"
            strokeWidth="1.2"
            strokeDasharray="48 442"
          />
        </svg>
      </motion.div>

      <motion.div
        animate={
          reduce
            ? undefined
            : {
                opacity: [1, 0.86, 1, 0.92, 1],
                transition: { duration: 3.2, repeat: Infinity, ease: "easeInOut" },
              }
        }
        className="absolute inset-0 flex items-center justify-center"
      >
        <span
          className="select-none text-4xl font-light tracking-[0.18em] text-neutral-100 sm:text-5xl"
          style={{
            textShadow:
              "0 0 16px rgba(255,40,60,0.55), 0 0 2px rgba(255,255,255,0.4)",
          }}
        >
          {monogram}
        </span>
      </motion.div>
    </motion.div>
  );
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="mt-10 w-72 sm:w-96">
      <div className="relative h-px w-full bg-neutral-800">
        <motion.div
          className="absolute inset-y-0 left-0 bg-red-500"
          style={{ width: `${value}%` }}
          transition={{ ease: [0.22, 1, 0.36, 1] }}
        />
        <motion.div
          className="absolute -top-[2px] h-[5px] w-[5px] rounded-full bg-red-500"
          style={{
            left: `calc(${value}% - 2.5px)`,
            boxShadow: "0 0 12px rgba(255,40,60,0.9)",
          }}
        />
      </div>
      <div className="mt-2 flex justify-between text-[9px] tracking-[0.4em] text-neutral-600">
        <span>00</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>
  );
}

function BackdropGrid() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.18]"
      style={{
        backgroundImage:
          "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
        backgroundSize: "48px 48px",
        maskImage:
          "radial-gradient(ellipse at center, black 40%, transparent 75%)",
        WebkitMaskImage:
          "radial-gradient(ellipse at center, black 40%, transparent 75%)",
      }}
    />
  );
}

function ScanLine({ reduce }: { reduce: boolean }) {
  if (reduce) return null;
  return (
    <motion.div
      aria-hidden
      initial={{ y: "-10%" }}
      animate={{ y: "110%" }}
      transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
      className="pointer-events-none absolute inset-x-0 h-[120px]"
      style={{
        background:
          "linear-gradient(to bottom, transparent, rgba(255,40,60,0.06), transparent)",
      }}
    />
  );
}

function Vignette() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0"
      style={{
        background:
          "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.85) 100%)",
      }}
    />
  );
}

function easeOutQuart(t: number) {
  return 1 - Math.pow(1 - t, 4);
}

function fmtTime(d: Date) {
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())} UTC`;
}
