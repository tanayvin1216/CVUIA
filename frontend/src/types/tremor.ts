export type Handedness = "Left" | "Right" | null;

export interface TremorPayload {
  level: number;
  magnitude: number;
  frequency: number;
  hand: Handedness;
  samples: number;
  timestamp: number;
}

export const ZERO_PAYLOAD: TremorPayload = {
  level: 0,
  magnitude: 0,
  frequency: 0,
  hand: null,
  samples: 0,
  timestamp: 0,
};
