import React from 'react';
import { Theme, THEME_LABELS, THEME_DESCRIPTIONS } from '../types';
import { useTheme } from '../contexts/ThemeContext';

interface ThemeSelectorProps {
  selectedTheme: Theme;
  onThemeChange: (theme: Theme) => void;
}

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ selectedTheme, onThemeChange }) => {
  const { setTheme } = useTheme();

  const handleThemeSelect = (theme: Theme) => {
    onThemeChange(theme);
    // Apply theme immediately for preview
    setTheme(theme);
  };

  const getThemePreviewClass = (theme: Theme) => {
    switch (theme) {
      case Theme.BLUE_GRADIENT:
        return 'blue-gradient';
      case Theme.LIGHT:
        return 'light';
      case Theme.DARK:
        return 'dark';
      default:
        return 'blue-gradient';
    }
  };

  return (
    <div className="theme-selector">
      <h4>Theme</h4>
      <div className="theme-options">
        {Object.values(Theme).map((theme) => (
          <div
            key={theme}
            className={`theme-option ${selectedTheme === theme ? 'selected' : ''}`}
            onClick={() => handleThemeSelect(theme)}
          >
            <div className={`theme-preview ${getThemePreviewClass(theme)}`}></div>
            <div className="theme-info">
              <h5>{THEME_LABELS[theme]}</h5>
              <p>{THEME_DESCRIPTIONS[theme]}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ThemeSelector; 