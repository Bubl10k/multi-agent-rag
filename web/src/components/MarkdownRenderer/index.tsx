import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import {
  vscDarkPlus,
  vs,
} from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Box, Divider, Link, Typography } from '@mui/material';
import type { Components } from 'react-markdown';

import { useThemeMode } from '@/theme/ThemeContext';

// TODO: refactor this via some Markdown library
const useComponents = (isDark: boolean): Components => ({
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className ?? '');
    const isBlock = !!match;
    if (!isBlock) {
      return (
        <Box
          component="code"
          sx={{
            px: 0.6,
            py: 0.2,
            borderRadius: 1,
            bgcolor: 'action.hover',
            fontFamily: 'monospace',
            fontSize: '0.85em',
          }}
          {...(props as object)}
        >
          {children}
        </Box>
      );
    }
    return (
      <SyntaxHighlighter
        style={isDark ? vscDarkPlus : vs}
        language={match[1]}
        PreTag="div"
        customStyle={{ borderRadius: 8, margin: '8px 0', fontSize: '0.85rem' }}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    );
  },
  p: ({ children }) => (
    <Typography
      variant="body1"
      sx={{ lineHeight: 1.7, mb: 1, '&:last-child': { mb: 0 } }}
    >
      {children}
    </Typography>
  ),
  h1: ({ children }) => (
    <Typography variant="h5" fontWeight={700} mb={1}>
      {children}
    </Typography>
  ),
  h2: ({ children }) => (
    <Typography variant="h6" fontWeight={700} mb={1}>
      {children}
    </Typography>
  ),
  h3: ({ children }) => (
    <Typography variant="subtitle1" fontWeight={700} mb={0.5}>
      {children}
    </Typography>
  ),
  h4: ({ children }) => (
    <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
      {children}
    </Typography>
  ),
  ul: ({ children }) => (
    <Box component="ul" sx={{ pl: 2.5, my: 0.5 }}>
      {children}
    </Box>
  ),
  ol: ({ children }) => (
    <Box component="ol" sx={{ pl: 2.5, my: 0.5 }}>
      {children}
    </Box>
  ),
  li: ({ children }) => (
    <Typography component="li" variant="body1" sx={{ lineHeight: 1.7 }}>
      {children}
    </Typography>
  ),
  a: ({ href, children }) => (
    <Link href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </Link>
  ),
  hr: () => <Divider sx={{ my: 1.5 }} />,
  blockquote: ({ children }) => (
    <Box
      component="blockquote"
      sx={{
        borderLeft: 3,
        borderColor: 'divider',
        pl: 1.5,
        ml: 0,
        my: 1,
        color: 'text.secondary',
      }}
    >
      {children}
    </Box>
  ),
});

type Props = { children: string };

const MarkdownRenderer = ({ children }: Props) => {
  const { mode } = useThemeMode();
  const components = useComponents(mode === 'dark');

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {children}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;
