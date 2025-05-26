import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Theme } from '../types';

interface ThemeContextType {
  currentTheme: Theme;
  setTheme: (theme: Theme) => void;
  applyTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  initialTheme = Theme.BLUE_GRADIENT 
}) => {
  const [currentTheme, setCurrentTheme] = useState<Theme>(initialTheme);

  const applyTheme = (theme: Theme) => {
    // Remove existing theme classes
    document.body.classList.remove('theme-blue-gradient', 'theme-light', 'theme-dark');
    
    // Add new theme class
    switch (theme) {
      case Theme.BLUE_GRADIENT:
        document.body.classList.add('theme-blue-gradient');
        break;
      case Theme.LIGHT:
        document.body.classList.add('theme-light');
        break;
      case Theme.DARK:
        document.body.classList.add('theme-dark');
        break;
    }
  };

  const setTheme = (theme: Theme) => {
    setCurrentTheme(theme);
    applyTheme(theme);
    // Store theme preference in localStorage
    localStorage.setItem('miniature-tracker-theme', theme);
  };

  // Apply theme on mount and when theme changes
  useEffect(() => {
    applyTheme(currentTheme);
  }, [currentTheme]);

  // Update theme when initialTheme prop changes (from user preferences)
  useEffect(() => {
    if (initialTheme !== currentTheme) {
      setCurrentTheme(initialTheme);
    }
  }, [initialTheme]);

  // Load theme from localStorage on mount (only if no initialTheme provided)
  useEffect(() => {
    if (initialTheme === Theme.BLUE_GRADIENT) {
      const savedTheme = localStorage.getItem('miniature-tracker-theme') as Theme;
      if (savedTheme && Object.values(Theme).includes(savedTheme)) {
        setCurrentTheme(savedTheme);
      }
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ currentTheme, setTheme, applyTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}; 