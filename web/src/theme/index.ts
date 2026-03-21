import { createTheme, type PaletteMode } from '@mui/material/styles';

const getTheme = (mode: PaletteMode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: '#7c3aed',
        light: '#a78bfa',
        dark: '#5b21b6',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#c4b5fd',
        contrastText: '#1e1b4b',
      },
      background:
        mode === 'dark'
          ? { default: '#212121', paper: '#171717' }
          : { default: '#ffffff', paper: '#f7f7f8' },
    },
    typography: {
      fontFamily: [
        'Inter',
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        'sans-serif',
      ].join(','),
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
          },
        },
      },
      MuiCssBaseline: {
        styleOverrides: {
          '*, *::before, *::after': {
            boxSizing: 'border-box',
          },
          body: {
            margin: 0,
            overflow: 'hidden',
          },
        },
      },
    },
  });

export default getTheme;
