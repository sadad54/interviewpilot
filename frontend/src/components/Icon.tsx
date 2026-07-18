import type { SVGProps } from "react";

export type IconName =
  | "arrow-right"
  | "brain"
  | "check"
  | "chevron-down"
  | "message"
  | "mic"
  | "refresh"
  | "sparkles"
  | "stop"
  | "target"
  | "user"
  | "volume";

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
  size?: number;
}

const paths: Record<IconName, React.ReactNode> = {
  "arrow-right": <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
  brain: <><path d="M9.5 4.5A3 3 0 0 0 4 6.2a3 3 0 0 0 .3 5.6A3.1 3.1 0 0 0 7 17.5a3 3 0 0 0 5 2.2V5a3 3 0 0 0-2.5-.5Z"/><path d="M14.5 4.5A3 3 0 0 1 20 6.2a3 3 0 0 1-.3 5.6 3.1 3.1 0 0 1-2.7 5.7 3 3 0 0 1-5 2.2V5a3 3 0 0 1 2.5-.5Z"/><path d="M8 9a3 3 0 0 0 4 0M16 9a3 3 0 0 1-4 0M8 14a3 3 0 0 1-1 3.5M16 14a3 3 0 0 0 1 3.5"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  "chevron-down": <path d="m7 10 5 5 5-5"/>,
  message: <><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"/><path d="M8 9h8M8 13h5"/></>,
  mic: <><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5M8 22h8"/></>,
  refresh: <><path d="M20 7v5h-5"/><path d="M4 17v-5h5"/><path d="M6.1 9a7 7 0 0 1 11.7-2.6L20 12M4 12l2.2 5.6A7 7 0 0 0 17.9 15"/></>,
  sparkles: <><path d="m12 3-1.1 3.2a3 3 0 0 1-1.9 1.9L6 9.2l3 1.1a3 3 0 0 1 1.9 1.9L12 15.4l1.1-3.2a3 3 0 0 1 1.9-1.9l3-1.1-3-1.1a3 3 0 0 1-1.9-1.9Z"/><path d="m5 15-.6 1.7a2 2 0 0 1-1.2 1.2l-1.7.6 1.7.6a2 2 0 0 1 1.2 1.2L5 22l.6-1.7a2 2 0 0 1 1.2-1.2l1.7-.6-1.7-.6a2 2 0 0 1-1.2-1.2Z"/></>,
  stop: <rect x="6" y="6" width="12" height="12" rx="2"/>,
  target: <><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></>,
  user: <><circle cx="12" cy="8" r="4"/><path d="M4 22a8 8 0 0 1 16 0"/></>,
  volume: <><path d="M11 5 6 9H2v6h4l5 4Z"/><path d="M15 9a4 4 0 0 1 0 6M18 6a8 8 0 0 1 0 12"/></>,
};

export default function Icon({ name, size = 20, ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      {...props}
    >
      {paths[name]}
    </svg>
  );
}
