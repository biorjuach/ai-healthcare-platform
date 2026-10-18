import React, { createContext, useState, useContext } from 'react';
import { DefaultTheme, DarkTheme } from 'react-native-paper';

interface ThemeContextData {
  isDarkMode: boolean;
  toggleTheme: () => void;
  theme: typeof DefaultTheme;
}

const ThemeContext = createContext<ThemeContextData>({} as ThemeContextData);

const lightTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#2196F3',
    accent: '#03A9F4',
    background: '#FFFFFF',
    surface: '#FFFFFF',
    text: '#000000',
    error: '#B00020',
  },
};

const darkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: '#90CAF9',
    accent: '#4FC3F7',
    background: '#121212',
    surface: '#121212',
    text: '#FFFFFF',
    error: '#CF6679',
  },
};

export const ThemeProvider: React.FC = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ThemeContext.Provider
      value={{
        isDarkMode,
        toggleTheme,
        theme: isDarkMode ? darkTheme : lightTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 