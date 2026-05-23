import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip as ChartTooltip,
} from 'chart.js';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  useTheme,
} from '@mui/material';
import { Brain, Bot, FolderOpen, MessageSquare } from 'lucide-react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { useNavigate } from 'react-router';

import { useGetAgentsQuery } from '@/api/endpoints/agent';
import { useGetLLMsQuery } from '@/api/endpoints/llm';
import { useGetCollectionsQuery } from '@/api/endpoints/collection';
import { useGetConversationsQuery } from '@/api/endpoints/conversation';
import { AgentType } from '@/api/types/agent';
import { conversationChatPath } from '@/router/router';
import { getConversationPreview } from '@/utils/conversation';

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  ChartTooltip,
  Legend,
);

const AGENT_TYPE_LABELS: Record<AgentType, string> = {
  [AgentType.GENERAL]: 'General',
  [AgentType.PROGRAMMING]: 'Programming',
  [AgentType.MATH]: 'Math',
  [AgentType.RESEARCHER]: 'Researcher',
  [AgentType.INVOICE]: 'Invoice',
  [AgentType.ROUTER]: 'Router',
};

const CHART_COLORS = [
  '#7c3aed',
  '#0ea5e9',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#06b6d4',
  '#84cc16',
];

type StatCardProps = {
  label: string;
  value: number | string;
  sub?: string;
  icon: React.ReactNode;
  color: string;
};

const StatCard = ({ label, value, sub, icon, color }: StatCardProps) => (
  <Card variant="outlined" sx={{ flex: 1, minWidth: 180 }}>
    <CardContent sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
      <Box
        sx={{
          width: 44,
          height: 44,
          borderRadius: 2,
          bgcolor: `${color}22`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color,
          flexShrink: 0,
        }}
      >
        {icon}
      </Box>
      <Box>
        <Typography variant="h5" fontWeight={700} lineHeight={1.2}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={0.25}>
          {label}
        </Typography>
        {sub && (
          <Typography variant="caption" color="text.disabled">
            {sub}
          </Typography>
        )}
      </Box>
    </CardContent>
  </Card>
);

const DashboardPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const { data: agents = [], isLoading: agentsLoading } = useGetAgentsQuery();
  const { data: llms = [], isLoading: llmsLoading } = useGetLLMsQuery();
  const { data: collections = [], isLoading: collectionsLoading } =
    useGetCollectionsQuery();
  const { data: conversations = [], isLoading: conversationsLoading } =
    useGetConversationsQuery();

  const isLoading =
    agentsLoading || llmsLoading || collectionsLoading || conversationsLoading;

  const activeAgents = agents.filter(a => a.is_active).length;
  const activeLLMs = llms.filter(l => l.is_active).length;

  const recentConversations = [...conversations]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
    .slice(0, 10);

  const agentById = Object.fromEntries(agents.map(a => [a.id, a]));

  // conversations per agent
  const convCountByAgent = conversations.reduce<Record<string, number>>(
    (acc, c) => ({ ...acc, [c.agent_id]: (acc[c.agent_id] ?? 0) + 1 }),
    {},
  );
  const agentUsage = agents
    .map(a => ({ agent: a, count: convCountByAgent[a.id] ?? 0 }))
    .sort((a, b) => b.count - a.count);

  // agents per LLM
  const agentCountByLLM = agents.reduce<Record<string, number>>(
    (acc, a) => a.llm ? { ...acc, [a.llm.id]: (acc[a.llm.id] ?? 0) + 1 } : acc,
    {},
  );
  const llmUsage = llms
    .map(l => ({ llm: l, count: agentCountByLLM[l.id] ?? 0 }))
    .sort((a, b) => b.count - a.count);

  // agent types
  const agentTypeBreakdown = Object.values(AgentType)
    .map(type => ({
      type,
      count: agents.filter(a => a.agent_type === type).length,
    }))
    .filter(e => e.count > 0);

  const textColor = theme.palette.text.secondary;
  const gridColor =
    theme.palette.mode === 'dark'
      ? 'rgba(255,255,255,0.08)'
      : 'rgba(0,0,0,0.08)';

  const agentBarData = {
    labels: agentUsage.map(e => e.agent.name),
    datasets: [
      {
        label: 'Conversations',
        data: agentUsage.map(e => e.count),
        backgroundColor: agentUsage.map(
          (_, i) => CHART_COLORS[i % CHART_COLORS.length] + 'cc',
        ),
        borderColor: agentUsage.map(
          (_, i) => CHART_COLORS[i % CHART_COLORS.length],
        ),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const agentBarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: { parsed: { y: number | null } }) => {
            const v = ctx.parsed.y ?? 0;
            return ` ${v} conversation${v !== 1 ? 's' : ''}`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: { color: textColor, font: { size: 12 } },
        grid: { display: false },
      },
      y: {
        ticks: {
          color: textColor,
          font: { size: 12 },
          stepSize: 1,
          precision: 0,
        },
        grid: { color: gridColor },
        beginAtZero: true,
      },
    },
  } as const;

  const llmDoughnutData = {
    labels: llmUsage.map(e => e.llm.model_name),
    datasets: [
      {
        data: llmUsage.map(e => Math.max(e.count, 0.001)),
        backgroundColor: llmUsage.map(
          (_, i) => CHART_COLORS[i % CHART_COLORS.length] + 'cc',
        ),
        borderColor: llmUsage.map(
          (_, i) => CHART_COLORS[i % CHART_COLORS.length],
        ),
        borderWidth: 1,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: textColor,
          font: { size: 12 },
          padding: 12,
          boxWidth: 12,
        },
      },
      tooltip: {
        callbacks: {
          label: (ctx: { label: string; parsed: number }) =>
            ` ${ctx.label}: ${Math.round(ctx.parsed)}`,
        },
      },
    },
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1250, mx: 'auto' }}>
      <Typography variant="h5" fontWeight={600} mb={3}>
        Dashboard
      </Typography>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Stat cards */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 4 }}>
            <StatCard
              label="Agents"
              value={agents.length}
              sub={`${activeAgents} active`}
              icon={<Bot size={20} />}
              color="#7c3aed"
            />
            <StatCard
              label="LLM Models"
              value={llms.length}
              sub={`${activeLLMs} active`}
              icon={<Brain size={20} />}
              color="#0ea5e9"
            />
            <StatCard
              label="Collections"
              value={collections.length}
              icon={<FolderOpen size={20} />}
              color="#10b981"
            />
            <StatCard
              label="Conversations"
              value={conversations.length}
              icon={<MessageSquare size={20} />}
              color="#f59e0b"
            />
          </Box>

          {/* Charts row */}
          <Box
            sx={{
              display: 'flex',
              gap: 3,
              flexWrap: 'wrap',
              alignItems: 'flex-start',
              mb: 4,
            }}
          >
            {/* Agents usage bar chart */}
            <Card variant="outlined" sx={{ flex: 2, minWidth: 320 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} mb={2}>
                  Agents Usage
                </Typography>
                {agentUsage.length === 0 ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      No agents yet.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ height: 220 }}>
                    <Bar data={agentBarData} options={agentBarOptions} />
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* API keys / LLM doughnut */}
            <Card variant="outlined" sx={{ flex: 1, minWidth: 220 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} mb={2}>
                  API Keys Usage
                </Typography>
                {llmUsage.length === 0 ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      No LLM models yet.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ height: 220 }}>
                    <Doughnut data={llmDoughnutData} options={doughnutOptions} />
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Agent types list */}
            <Card variant="outlined" sx={{ flex: 1, minWidth: 220 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} mb={2}>
                  Agent Types
                </Typography>
                {agentTypeBreakdown.length === 0 ? (
                  <Box sx={{ py: 4, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      No agents yet.
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {agentTypeBreakdown.map(({ type, count }) => (
                      <Box
                        key={type}
                        sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                      >
                        <Chip
                          label={AGENT_TYPE_LABELS[type]}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                        <Typography variant="body2" color="text.secondary">
                          {count}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>

          {/* Recent conversations */}
          <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
            Recent Conversations
          </Typography>
          {recentConversations.length === 0 ? (
            <Box component={Paper} variant="outlined" sx={{ py: 5, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No conversations yet.
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Preview</TableCell>
                    <TableCell>Agent</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentConversations.map(conv => {
                    const agent = agentById[conv.agent_id];
                    return (
                      <TableRow
                        key={conv.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() =>
                          navigate(conversationChatPath(conv.agent_id, conv.id))
                        }
                      >
                        <TableCell sx={{ maxWidth: 340 }}>
                          <Typography variant="body2" noWrap>
                            {getConversationPreview(conv)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {agent?.name ?? '—'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {agent ? (
                            <Chip
                              label={AGENT_TYPE_LABELS[agent.agent_type]}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          ) : (
                            <Typography variant="body2" color="text.disabled">
                              —
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell sx={{ whiteSpace: 'nowrap' }}>
                          <Typography variant="caption" color="text.disabled">
                            {new Date(conv.created_at).toLocaleDateString(
                              undefined,
                              { month: 'short', day: 'numeric', year: 'numeric' },
                            )}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}
    </Box>
  );
};

export default DashboardPage;