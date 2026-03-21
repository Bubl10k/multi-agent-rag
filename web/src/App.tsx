import { ToastContainer } from 'react-toastify';
import { AppRouter } from '@/router';
import { ThemeProvider } from '@/theme/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <AppRouter />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        aria-label="notifications"
      />
    </ThemeProvider>
  );
}

export default App;
