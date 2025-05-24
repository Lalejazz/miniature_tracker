/**
 * TypeScript interfaces for miniature tracker data models
 */

export enum PaintingStatus {
  WANT_TO_BUY = "want_to_buy",
  PURCHASED = "purchased", 
  ASSEMBLED = "assembled",
  PRIMED = "primed",
  GAME_READY = "game_ready",
  PARADE_READY = "parade_ready"
}

export interface MiniatureBase {
  name: string;
  faction: string;
  model_type: string;
  status: PaintingStatus;
  notes?: string;
}

export interface MiniatureCreate extends MiniatureBase {}

export interface MiniatureUpdate {
  name?: string;
  faction?: string;
  model_type?: string;
  status?: PaintingStatus;
  notes?: string;
}

export interface Miniature extends MiniatureBase {
  id: string;
  created_at: string;
  updated_at: string;
}

// UI Helper types
export interface StatusInfo {
  label: string;
  color: string;
  description: string;
}

export const STATUS_INFO: Record<PaintingStatus, StatusInfo> = {
  [PaintingStatus.WANT_TO_BUY]: {
    label: "Want to Buy",
    color: "#6b7280",
    description: "On wishlist"
  },
  [PaintingStatus.PURCHASED]: {
    label: "Purchased", 
    color: "#3b82f6",
    description: "Bought but not assembled"
  },
  [PaintingStatus.ASSEMBLED]: {
    label: "Assembled",
    color: "#f59e0b", 
    description: "Built and ready for primer"
  },
  [PaintingStatus.PRIMED]: {
    label: "Primed",
    color: "#8b5cf6",
    description: "Primer applied"
  },
  [PaintingStatus.GAME_READY]: {
    label: "Game Ready",
    color: "#10b981",
    description: "Painted enough for tabletop"
  },
  [PaintingStatus.PARADE_READY]: {
    label: "Parade Ready", 
    color: "#ef4444",
    description: "Fully detailed and complete"
  }
}; 