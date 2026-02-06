/**
 * Network Types for Related Party Transaction Visualization
 *
 * Type definitions for D3.js force-directed graph showing company relationships
 */

export type EntityType = 'company' | 'subsidiary' | 'associate' | 'joint_venture';

export type TransactionType =
  | 'sales'
  | 'purchases'
  | 'loans_given'
  | 'loans_taken'
  | 'advances'
  | 'investments'
  | 'guarantees';

export interface NetworkNode {
  /** Unique identifier for the node */
  id: string;

  /** Display name of the entity */
  name: string;

  /** Type of entity */
  type: EntityType;

  /** Total transaction value in crores */
  totalTransactions: number;

  /** Number of transactions */
  transactionCount: number;

  /** Optional D3.js positioning properties (added by simulation) */
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  vx?: number;
  vy?: number;
}

export interface NetworkLink {
  /** Source node ID */
  source: string | NetworkNode;

  /** Target node ID */
  target: string | NetworkNode;

  /** Type of transaction */
  transactionType: TransactionType;

  /** Transaction amount in crores */
  amount: number;

  /** Display label for the link */
  label: string;

  /** Optional: Link value for thickness calculation */
  value?: number;
}

export interface RelatedPartyNetworkData {
  /** Array of network nodes */
  nodes: NetworkNode[];

  /** Array of network links */
  links: NetworkLink[];

  /** Company name for display */
  companyName: string;

  /** Total RPT amount across all transactions (in crores) */
  totalRPTAmount: number;

  /** Fiscal year of the data */
  fiscalYear: string;

  /** Optional: Number of unique related parties */
  relatedPartyCount?: number;
}

/**
 * Configuration for visual encoding in the network graph
 */
export interface NetworkVisualConfig {
  /** Node size range (min, max) in pixels */
  nodeSizeRange: [number, number];

  /** Link thickness range (min, max) in pixels */
  linkThicknessRange: [number, number];

  /** Colors for different entity types */
  entityColors: Record<EntityType, string>;

  /** Colors for different transaction types */
  transactionColors: Record<TransactionType, string>;

  /** Force simulation parameters */
  forceStrength: {
    link: number;
    charge: number;
    collide: number;
  };

  /** Zoom extent [min, max] */
  zoomExtent: [number, number];
}

/**
 * Default visual configuration
 */
export const DEFAULT_NETWORK_CONFIG: NetworkVisualConfig = {
  nodeSizeRange: [15, 50],
  linkThicknessRange: [1, 8],
  entityColors: {
    company: '#3b82f6',      // Blue
    subsidiary: '#10b981',   // Green
    associate: '#f59e0b',    // Yellow
    joint_venture: '#8b5cf6' // Purple
  },
  transactionColors: {
    sales: '#6b7280',         // Gray
    purchases: '#6b7280',     // Gray
    loans_given: '#f97316',   // Orange
    loans_taken: '#f97316',   // Orange
    advances: '#3b82f6',      // Blue
    investments: '#3b82f6',   // Blue
    guarantees: '#ef4444'     // Red
  },
  forceStrength: {
    link: 100,
    charge: -300,
    collide: 40
  },
  zoomExtent: [0.5, 3]
};

/**
 * Tooltip data structure
 */
export interface NetworkTooltipData {
  type: 'node' | 'link';
  title: string;
  details: Array<{ label: string; value: string }>;
  x: number;
  y: number;
}
