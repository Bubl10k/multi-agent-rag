import { useState, type AnchorHTMLAttributes } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { Highlight, themes } from 'prism-react-renderer';
import { Box, IconButton, Link, Tooltip, Typography } from '@mui/material';
import { Copy, Check } from 'lucide-react';
import 'katex/dist/katex.min.css';

import { useThemeMode } from '@/theme/ThemeContext';
import { useAppSelector } from '@/store';
import { preprocessMarkdown } from './preprocessMarkdown';

const useInvoiceDownload = () => {
  const token = useAppSelector(state => state.auth.token);
  return async (href: string) => {
    const res = await fetch(href, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const disposition = res.headers.get('Content-Disposition') ?? '';
    const match = disposition.match(/filename="?([^"]+)"?/);
    a.download = match?.[1] ?? 'invoice.pdf';
    a.click();
    URL.revokeObjectURL(url);
  };
};

const InvoiceAwareLink = ({ href, children }: AnchorHTMLAttributes<HTMLAnchorElement>) => {
  const downloadInvoice = useInvoiceDownload();
  if (href?.includes('/api/invoices/download')) {
    return (
      <Link
        href={href}
        onClick={e => {
          e.preventDefault();
          void downloadInvoice(href!);
        }}
        sx={{ cursor: 'pointer' }}
      >
        {children}
      </Link>
    );
  }
  return (
    <Link href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </Link>
  );
};

const CopyButton = ({ code }: { code: string }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <Tooltip title={copied ? 'Copied!' : 'Copy'}>
      <IconButton
        onClick={handleCopy}
        size="small"
        sx={{ position: 'absolute', top: 6, right: 6, opacity: 0.7, '&:hover': { opacity: 1 } }}
      >
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </IconButton>
    </Tooltip>
  );
};

type Props = { children: string };

const MarkdownRenderer = ({ children }: Props) => {
  const { mode } = useThemeMode();
  const prismTheme = mode === 'dark' ? themes.vsDark : themes.github;

  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath, remarkGfm]}
      rehypePlugins={[rehypeKatex]}
      components={{
        code({ className, children: codeChildren }) {
          const match = /language-(\w+)/.exec(className || '');
          const codeStr = String(codeChildren).replace(/\n$/, '');
          const isBlock = !!match || codeStr.includes('\n');

          if (isBlock) {
            return (
              <Box sx={{ position: 'relative', my: 1 }}>
                <Highlight
                  code={codeStr}
                  language={match?.[1] ?? 'text'}
                  theme={prismTheme}
                >
                  {({ className: hlClass, style, tokens, getLineProps, getTokenProps }) => (
                    <pre
                      className={hlClass}
                      style={{ ...style, borderRadius: 6, padding: '12px 16px', overflow: 'auto', margin: 0 }}
                    >
                      <code>
                        {tokens.map((line, i) => (
                          <div key={i} {...getLineProps({ line })}>
                            {line.map((token, key) => (
                              <span key={key} {...getTokenProps({ token })} />
                            ))}
                          </div>
                        ))}
                      </code>
                    </pre>
                  )}
                </Highlight>
                <CopyButton code={codeStr} />
              </Box>
            );
          }

          return (
            <Box
              component="code"
              sx={{
                fontSize: '0.875em',
                bgcolor: 'action.hover',
                px: 0.5,
                borderRadius: 0.5,
                fontFamily: 'monospace',
              }}
            >
              {codeChildren}
            </Box>
          );
        },
        // Unwrap <pre> so the Highlight block inside code doesn't get double-wrapped
        pre({ children }) {
          return <>{children}</>;
        },
        a({ href, children }) {
          return <InvoiceAwareLink href={href}>{children}</InvoiceAwareLink>;
        },
        h1({ children }) {
          return <Typography variant="h5" fontWeight={700} mb={1}>{children}</Typography>;
        },
        h2({ children }) {
          return <Typography variant="h6" fontWeight={700} mb={1}>{children}</Typography>;
        },
        h3({ children }) {
          return <Typography variant="subtitle1" fontWeight={700} mb={0.5}>{children}</Typography>;
        },
        h4({ children }) {
          return <Typography variant="subtitle2" fontWeight={700} mb={0.5}>{children}</Typography>;
        },
      }}
    >
      {preprocessMarkdown(children)}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;