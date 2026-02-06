/**
 * Network Transformer Utility
 *
 * Transforms backend RPT (Related Party Transaction) data into D3.js-compatible
 * node/link structure for force-directed graph visualization
 */

import {
  NetworkNode,
  NetworkLink,
  RelatedPartyNetworkData,
  EntityType,
  TransactionType,
} from '@/lib/types/network';

/**
 * Backend RPT data structure (from analysis results)
 */
interface BackendRPTData {
  subsidiaries?: Array<{
    name: string;
    sales?: number;
    purchases?: number;
    loans_given?: number;
    loans_taken?: number;
    advances?: number;
    investments?: number;
    guarantees?: number;
  }>;
  associates?: Array<{
    name: string;
    sales?: number;
    purchases?: number;
    loans_given?: number;
    loans_taken?: number;
    advances?: number;
    investments?: number;
    guarantees?: number;
  }>;
  joint_ventures?: Array<{
    name: string;
    sales?: number;
    purchases?: number;
    loans_given?: number;
    loans_taken?: number;
    advances?: number;
    investments?: number;
    guarantees?: number;
  }>;
}

/**
 * Convert lakhs to crores
 */
function lakhsToCrores(lakhs: number): number {
  return Math.round((lakhs / 100) * 100) / 100; // Round to 2 decimal places
}

/**
 * Format amount for display
 */
export function formatAmount(crores: number): string {
  if (crores >= 1000) {
    return `₹${(crores / 1000).toFixed(2)}K Cr`;
  }
  return `₹${crores.toFixed(2)} Cr`;
}

/**
 * Transform backend RPT data to network graph structure
 */
export function transformRPTToNetwork(
  rptData: BackendRPTData | null | undefined,
  companyName: string,
  fiscalYear: string
): RelatedPartyNetworkData {
  if (!rptData) {
    return {
      nodes: [],
      links: [],
      companyName,
      totalRPTAmount: 0,
      fiscalYear,
      relatedPartyCount: 0,
    };
  }

  const nodes: NetworkNode[] = [];
  const links: NetworkLink[] = [];
  let totalRPTAmount = 0;

  // Create central company node
  const companyNodeId = 'company-0';
  nodes.push({
    id: companyNodeId,
    name: companyName,
    type: 'company',
    totalTransactions: 0, // Will be calculated later
    transactionCount: 0,  // Will be calculated later
  });

  // Helper function to process entity group (subsidiaries, associates, JVs)
  const processEntityGroup = (
    entities: Array<{
      name: string;
      sales?: number;
      purchases?: number;
      loans_given?: number;
      loans_taken?: number;
      advances?: number;
      investments?: number;
      guarantees?: number;
    }> | undefined,
    entityType: EntityType
  ) => {
    if (!entities || entities.length === 0) return;

    entities.forEach((entity, index) => {
      const nodeId = `${entityType}-${index}`;
      let entityTotal = 0;
      let entityTransactionCount = 0;

      // Transaction types to check
      const transactionTypes: Array<{
        key: keyof typeof entity;
        type: TransactionType;
        label: string;
      }> = [
        { key: 'sales', type: 'sales', label: 'Sales' },
        { key: 'purchases', type: 'purchases', label: 'Purchases' },
        { key: 'loans_given', type: 'loans_given', label: 'Loans Given' },
        { key: 'loans_taken', type: 'loans_taken', label: 'Loans Taken' },
        { key: 'advances', type: 'advances', label: 'Advances' },
        { key: 'investments', type: 'investments', label: 'Investments' },
        { key: 'guarantees', type: 'guarantees', label: 'Guarantees' },
      ];

      // Create links for each transaction type
      transactionTypes.forEach(({ key, type, label }) => {
        const amountInLakhs = entity[key];
        if (amountInLakhs && amountInLakhs > 0) {
          const amountInCrores = lakhsToCrores(amountInLakhs as number);
          entityTotal += amountInCrores;
          entityTransactionCount++;
          totalRPTAmount += amountInCrores;

          // Determine link direction based on transaction type
          const isOutgoing = ['sales', 'loans_given', 'advances', 'investments', 'guarantees'].includes(type);

          links.push({
            source: isOutgoing ? companyNodeId : nodeId,
            target: isOutgoing ? nodeId : companyNodeId,
            transactionType: type,
            amount: amountInCrores,
            label: `${label}: ${formatAmount(amountInCrores)}`,
            value: amountInCrores, // For link thickness scaling
          });
        }
      });

      // Create node if entity has any transactions
      if (entityTotal > 0) {
        nodes.push({
          id: nodeId,
          name: entity.name,
          type: entityType,
          totalTransactions: entityTotal,
          transactionCount: entityTransactionCount,
        });
      }
    });
  };

  // Process all entity groups
  processEntityGroup(rptData.subsidiaries, 'subsidiary');
  processEntityGroup(rptData.associates, 'associate');
  processEntityGroup(rptData.joint_ventures, 'joint_venture');

  // Update company node with total transactions
  const companyNode = nodes.find((n) => n.id === companyNodeId);
  if (companyNode) {
    companyNode.totalTransactions = totalRPTAmount;
    companyNode.transactionCount = links.length;
  }

  return {
    nodes,
    links,
    companyName,
    totalRPTAmount: Math.round(totalRPTAmount * 100) / 100,
    fiscalYear,
    relatedPartyCount: nodes.length - 1, // Exclude company node
  };
}

/**
 * Get node radius based on transaction volume
 */
export function getNodeRadius(
  totalTransactions: number,
  minRadius: number,
  maxRadius: number,
  maxTransactionInData: number
): number {
  if (maxTransactionInData === 0) return minRadius;

  // Scale radius proportionally
  const scale = totalTransactions / maxTransactionInData;
  return minRadius + scale * (maxRadius - minRadius);
}

/**
 * Get link thickness based on transaction amount
 */
export function getLinkThickness(
  amount: number,
  minThickness: number,
  maxThickness: number,
  maxAmountInData: number
): number {
  if (maxAmountInData === 0) return minThickness;

  // Scale thickness proportionally
  const scale = amount / maxAmountInData;
  return minThickness + scale * (maxThickness - minThickness);
}

/**
 * Calculate distance between nodes based on transaction amount
 * Higher transaction amounts = closer nodes
 */
export function getLinkDistance(amount: number, maxAmountInData: number): number {
  const minDistance = 50;
  const maxDistance = 200;

  if (maxAmountInData === 0) return maxDistance;

  // Inverse relationship: higher amount = shorter distance
  const scale = 1 - amount / maxAmountInData;
  return minDistance + scale * (maxDistance - minDistance);
}

/**
 * Get entity type label for display
 */
export function getEntityTypeLabel(type: EntityType): string {
  const labels: Record<EntityType, string> = {
    company: 'Company',
    subsidiary: 'Subsidiary',
    associate: 'Associate',
    joint_venture: 'Joint Venture',
  };
  return labels[type];
}

/**
 * Get transaction type label for display
 */
export function getTransactionTypeLabel(type: TransactionType): string {
  const labels: Record<TransactionType, string> = {
    sales: 'Sales',
    purchases: 'Purchases',
    loans_given: 'Loans Given',
    loans_taken: 'Loans Taken',
    advances: 'Advances',
    investments: 'Investments',
    guarantees: 'Guarantees',
  };
  return labels[type];
}
