const LANGUAGE_HINTS: [RegExp, string][] = [
  [/\bdef \w+\(|class \w+:|from \w+ import/, 'python'],
  [/\bfunction\s*[\w(]|const\s|let\s|=>\s*{|import\s*{/, 'typescript'],
  [/\bpublic\s+class\s|System\.out\.|@Override/, 'java'],
  [/\bfn\s+\w+\s*\(|let\s+mut\s|impl\s+\w+|use\s+\w+::/, 'rust'],
  [/\bfunc\s+\w+\s*\(|:=|^package\s+\w+/m, 'go'],
];

function detectLanguage(code: string): string {
  for (const [pattern, lang] of LANGUAGE_HINTS) {
    if (pattern.test(code)) return lang;
  }
  return '';
}

function isCodeLine(line: string): boolean {
  return (
    /^(class|def|function|const|let|var|import|from|export|public|private|protected|fn |use |struct |impl |package |func )\s/.test(line) ||
    /^    \S/.test(line) ||
    /^\t/.test(line) ||
    /^#\s\S/.test(line) // code comment (not markdown header, which has no space after #)
  );
}

function isProseStart(line: string): boolean {
  // Prose: starts with a capital letter, 3+ lowercase letters, then whitespace or punctuation
  return /^[A-Z][a-z]{2,}[\s!,.]/.test(line) && !isCodeLine(line);
}

// Splits content into fenced code blocks and surrounding text so we only
// apply text transformations to non-code regions.
function splitOnCodeFences(content: string): { text: string; isCode: boolean }[] {
  const parts: { text: string; isCode: boolean }[] = [];
  const fenceRe = /```[\s\S]*?```/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = fenceRe.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ text: content.slice(lastIndex, match.index), isCode: false });
    }
    parts.push({ text: match[0], isCode: true });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < content.length) {
    parts.push({ text: content.slice(lastIndex), isCode: false });
  }
  return parts;
}

function convertLatexDelimiters(text: string): string {
  // \[...\] → $$...$$ (display math)
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, '\n$$$$\n$1\n$$$$\n');
  // \(...\) → $...$ (inline math)
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, '$$$1$$');
  return text;
}

export function preprocessMarkdown(content: string): string {
  // Fix 1: closing bracket/paren directly followed by prose — only in non-fenced regions.
  // e.g. "startsWith(prefix)Certainly!" → "startsWith(prefix)\n\nCertainly!"
  const parts = splitOnCodeFences(content);
  let result = parts
    .map(({ text, isCode }) => {
      if (isCode) return text;
      return convertLatexDelimiters(text.replace(/([)}\];])([A-Z][a-z]{3,})/g, '$1\n\n$2'));
    })
    .join('');

  // Fix 2: wrap a leading unfenced code block.
  // Only applies when content doesn't start with a markdown block element.
  const hasMarkdownStart = /^(```|#{1,6} |>|\*\s|-\s|\d+\.\s)/.test(result.trimStart());
  if (!hasMarkdownStart) {
    const lines = result.split('\n');
    if (isCodeLine(lines[0])) {
      let proseStartIndex = -1;
      for (let i = 1; i < lines.length; i++) {
        if (isProseStart(lines[i])) {
          proseStartIndex = i;
          break;
        }
      }
      if (proseStartIndex > 0) {
        const codeBlock = lines.slice(0, proseStartIndex).join('\n').trimEnd();
        const rest = lines.slice(proseStartIndex).join('\n');
        const lang = detectLanguage(codeBlock);
        result = `\`\`\`${lang}\n${codeBlock}\n\`\`\`\n\n${rest}`;
      }
    }
  }

  return result;
}