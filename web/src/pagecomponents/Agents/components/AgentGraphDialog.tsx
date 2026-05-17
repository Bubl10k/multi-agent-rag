import { useMemo } from 'react';
import {
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from '@mui/material';
import { X } from 'lucide-react';
import {
  Background,
  Controls,
  type Edge,
  MarkerType,
  MiniMap,
  type Node,
  Position,
  ReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useGetAgentGraphJSONQuery } from '@/api/endpoints/agent';
import { buildGraphLayout, NODE_HEIGHT, NODE_WIDTH } from '@/utils/agentGraph';

type Props = {
  agentId: string;
  agentName: string;
  open: boolean;
  onClose: () => void;
};

const AgentGraphDialog = ({ agentId, agentName, open, onClose }: Props) => {
  const { data, isLoading, isError } = useGetAgentGraphJSONQuery(agentId, {
    skip: !open,
  });

  const { nodes, edges } = useMemo<{ nodes: Node[]; edges: Edge[] }>(() => {
    if (!data) return { nodes: [], edges: [] };

    const positions = buildGraphLayout(data.nodes, data.edges);

    const nodes: Node[] = data.nodes.map(n => ({
      id: n.id,
      position: positions.get(n.id) ?? { x: 0, y: 0 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: { label: n.name },
      style: {
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 8,
        fontFamily: 'inherit',
        fontSize: 13,
        fontWeight: 500,
        background: '#fff',
        border: '1.5px solid #1976d2',
        color: '#1976d2',
      },
    }));

    const edges: Edge[] = data.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.data ?? undefined,
      animated: false,
      style: e.conditional
        ? { strokeDasharray: '5 3', stroke: '#ed6c02' }
        : { stroke: '#1976d2' },
      labelStyle: { fontSize: 11, fill: e.conditional ? '#ed6c02' : '#555' },
      labelBgStyle: { fill: '#fff', fillOpacity: 0.85 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: e.conditional ? '#ed6c02' : '#1976d2',
      },
    }));

    return { nodes, edges };
  }, [data]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="lg"
      slotProps={{ paper: { sx: { height: '75vh' } } }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pb: 1,
        }}
      >
        <Typography variant="h6" fontWeight={600}>
          {agentName} — graph
        </Typography>
        <IconButton size="small" onClick={onClose}>
          <X size={18} />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
        {isLoading && (
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography color="error">Failed to load graph.</Typography>
          </Box>
        )}

        {!isLoading && !isError && (
          <Box sx={{ flex: 1 }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable={false}
              proOptions={{ hideAttribution: true }}
            >
              <Background gap={16} size={1} />
              <Controls showInteractive={false} />
            </ReactFlow>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default AgentGraphDialog;
