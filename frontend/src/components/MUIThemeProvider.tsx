// @ts-nocheck
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb', // Blue-600 to match your existing color scheme
      dark: '#1d4ed8', // Blue-700
    },
    secondary: {
      main: '#64748b', // Slate-500
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 12, // Rounded corners to match your design
  },
  components: {
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            fontSize: '1.125rem', // text-lg equivalent
            padding: '0',
            '& fieldset': {
              borderWidth: '2px',
              borderColor: '#e5e7eb', // gray-200
            },
            '&:hover fieldset': {
              borderColor: '#93c5fd', // blue-300
            },
            '&.Mui-focused fieldset': {
              borderColor: '#2563eb', // blue-600
            },
            '&.Mui-error fieldset': {
              borderColor: '#f87171', // red-400
            },
            // Better spacing for text fields with icons
            '&.MuiInputBase-adornedStart': {
              paddingLeft: '8px',
            },
            '&.MuiInputBase-adornedEnd': {
              paddingRight: '8px',
            },
          },
          '& .MuiInputBase-input': {
            padding: '20px 14px', // py-5 px-4 equivalent
          },
          // Improved spacing for input adornments
          '& .MuiInputAdornment-root': {
            marginLeft: '4px',
            marginRight: '4px',
          },
          '& .MuiInputAdornment-positionStart': {
            marginRight: '8px',
          },
          '& .MuiInputAdornment-positionEnd': {
            marginLeft: '8px',
          },
        },
      },
    },
  },
});

export default function MUIThemeProvider({ children }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
