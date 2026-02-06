'use client';

/**
 * Related Party Network Component
 *
 * D3.js force-directed graph visualization showing company relationships
 * with related parties (subsidiaries, associates, joint ventures)
 */

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import {
  NetworkNode,
  NetworkLink,
  RelatedPartyNetworkData,
  DEFAULT_NETWORK_CONFIG,
  NetworkTooltipData,
} from '@/lib/types/network';
import {
  getNodeRadius,
  getLinkThickness,
  getLinkDistance,
  getEntityTypeLabel,
  getTransactionTypeLabel,
  formatAmount,
} from '@/lib/utils/networkTransformer';
import { Info, Maximize2, Minimize2 } from 'lucide-react';

interface RelatedPartyNetworkProps {
  data: RelatedPartyNetworkData;
  width?: number;
  height?: number;
}

export default function RelatedPartyNetwork({
  data,
  width = 800,
  height = 600,
}: RelatedPartyNetworkProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<NetworkTooltipData | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [dimensions, setDimensions] = useState({ width, height });

  // Update dimensions when fullscreen changes
  useEffect(() => {
    if (isFullscreen && containerRef.current) {
      setDimensions({
        width: window.innerWidth - 100,
        height: window.innerHeight - 200,
      });
    } else {
      setDimensions({ width, height });
    }
  }, [isFullscreen, width, height]);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    const { width: w, height: h } = dimensions;

    // Clear previous content
    svg.selectAll('*').remove();

    // Create container group for zoom
    const container = svg.append('g');

    // Calculate max values for scaling
    const maxTransactions = d3.max(data.nodes, (d) => d.totalTransactions) || 1;
    const maxAmount = d3.max(data.links, (d) => d.amount) || 1;

    // Clone nodes and links for D3 (to avoid mutating original data)
    const nodes: NetworkNode[] = data.nodes.map((d) => ({ ...d }));
    const links: NetworkLink[] = data.links.map((d) => ({
      ...d,
      value: getLinkDistance(d.amount, maxAmount),
    }));

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance((d: any) => getLinkDistance(d.amount, maxAmount))
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(w / 2, h / 2))
      .force(
        'collide',
        d3.forceCollide().radius((d: any) => {
          return (
            getNodeRadius(
              d.totalTransactions,
              DEFAULT_NETWORK_CONFIG.nodeSizeRange[0],
              DEFAULT_NETWORK_CONFIG.nodeSizeRange[1],
              maxTransactions
            ) + 10
          );
        })
      );

    // Create links
    const link = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', (d) => DEFAULT_NETWORK_CONFIG.transactionColors[d.transactionType])
      .attr('stroke-width', (d) =>
        getLinkThickness(
          d.amount,
          DEFAULT_NETWORK_CONFIG.linkThicknessRange[0],
          DEFAULT_NETWORK_CONFIG.linkThicknessRange[1],
          maxAmount
        )
      )
      .attr('stroke-opacity', 0.6)
      .style('cursor', 'pointer')
      .on('mouseover', function (event, d) {
        d3.select(this).attr('stroke-opacity', 1);

        const sourceNode = typeof d.source === 'object' ? d.source : nodes.find(n => n.id === d.source);
        const targetNode = typeof d.target === 'object' ? d.target : nodes.find(n => n.id === d.target);

        setTooltip({
          type: 'link',
          title: getTransactionTypeLabel(d.transactionType),
          details: [
            { label: 'From', value: sourceNode?.name || 'Unknown' },
            { label: 'To', value: targetNode?.name || 'Unknown' },
            { label: 'Amount', value: formatAmount(d.amount) },
          ],
          x: event.pageX,
          y: event.pageY,
        });
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-opacity', 0.6);
        setTooltip(null);
      });

    // Create nodes
    const node = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .style('cursor', 'pointer')
      .call(
        d3
          .drag<any, NetworkNode>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      );

    // Add circles to nodes
    node
      .append('circle')
      .attr('r', (d) =>
        getNodeRadius(
          d.totalTransactions,
          DEFAULT_NETWORK_CONFIG.nodeSizeRange[0],
          DEFAULT_NETWORK_CONFIG.nodeSizeRange[1],
          maxTransactions
        )
      )
      .attr('fill', (d) => DEFAULT_NETWORK_CONFIG.entityColors[d.type])
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseover', function (event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('stroke-width', 4)
          .attr('stroke', '#000');

        // Highlight connected links
        link
          .attr('stroke-opacity', (l: any) => {
            const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
            const targetId = typeof l.target === 'object' ? l.target.id : l.target;
            return sourceId === d.id || targetId === d.id ? 1 : 0.1;
          })
          .attr('stroke-width', (l: any) => {
            const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
            const targetId = typeof l.target === 'object' ? l.target.id : l.target;
            const thickness = getLinkThickness(
              l.amount,
              DEFAULT_NETWORK_CONFIG.linkThicknessRange[0],
              DEFAULT_NETWORK_CONFIG.linkThicknessRange[1],
              maxAmount
            );
            return sourceId === d.id || targetId === d.id ? thickness * 1.5 : thickness;
          });

        setTooltip({
          type: 'node',
          title: d.name,
          details: [
            { label: 'Type', value: getEntityTypeLabel(d.type) },
            { label: 'Total Transactions', value: formatAmount(d.totalTransactions) },
            { label: 'Transaction Count', value: d.transactionCount.toString() },
          ],
          x: event.pageX,
          y: event.pageY,
        });
      })
      .on('mouseout', function () {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('stroke-width', 2)
          .attr('stroke', '#fff');

        // Reset link opacity
        link
          .attr('stroke-opacity', 0.6)
          .attr('stroke-width', (l: any) =>
            getLinkThickness(
              l.amount,
              DEFAULT_NETWORK_CONFIG.linkThicknessRange[0],
              DEFAULT_NETWORK_CONFIG.linkThicknessRange[1],
              maxAmount
            )
          );

        setTooltip(null);
      })
      .on('click', function (event, d) {
        // Toggle pin
        if (d.fx !== null && d.fy !== null) {
          d.fx = null;
          d.fy = null;
        } else {
          d.fx = d.x;
          d.fy = d.y;
        }
      });

    // Add labels to nodes
    node
      .append('text')
      .text((d) => d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => {
        const radius = getNodeRadius(
          d.totalTransactions,
          DEFAULT_NETWORK_CONFIG.nodeSizeRange[0],
          DEFAULT_NETWORK_CONFIG.nodeSizeRange[1],
          maxTransactions
        );
        return radius + 15;
      })
      .attr('font-size', '12px')
      .attr('fill', '#374151')
      .attr('font-weight', (d) => (d.type === 'company' ? 'bold' : 'normal'))
      .style('pointer-events', 'none');

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: NetworkNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: NetworkNode) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: NetworkNode) {
      if (!event.active) simulation.alphaTarget(0);
      // Keep node pinned after drag unless unpinned by click
    }

    // Zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent(DEFAULT_NETWORK_CONFIG.zoomExtent)
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [data, dimensions]);

  if (!data.nodes.length) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-center">
          <Info className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">No Related Party Transactions</p>
          <p className="text-sm text-gray-500 mt-1">
            This company has no recorded related party transactions for {data.fiscalYear}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Related Party Transaction Network
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {data.relatedPartyCount} related parties • Total: {formatAmount(data.totalRPTAmount)}
          </p>
        </div>
        <button
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
        >
          {isFullscreen ? (
            <Minimize2 className="h-5 w-5 text-gray-600" />
          ) : (
            <Maximize2 className="h-5 w-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Legend */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-xs font-semibold text-gray-700 mb-2">Legend</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-gray-600">Company</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-600">Subsidiary</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-600">Associate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-gray-600">Joint Venture</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 Hover for details • Click to pin/unpin • Drag to move • Scroll to zoom
        </p>
      </div>

      {/* SVG Container */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          className="bg-white"
        />
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 bg-gray-900 text-white text-sm rounded-lg shadow-lg p-3 pointer-events-none"
          style={{
            left: tooltip.x + 10,
            top: tooltip.y + 10,
            maxWidth: '250px',
          }}
        >
          <div className="font-semibold mb-2">{tooltip.title}</div>
          <div className="space-y-1">
            {tooltip.details.map((detail, idx) => (
              <div key={idx} className="flex justify-between gap-3">
                <span className="text-gray-400">{detail.label}:</span>
                <span className="font-medium">{detail.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
