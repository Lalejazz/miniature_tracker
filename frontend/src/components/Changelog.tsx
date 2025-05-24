import React from 'react';
import { ChangelogEntry } from '../types';
import { changelogData } from '../data/changelog';

const Changelog: React.FC = () => {
  const getTypeIcon = (type: ChangelogEntry['type']) => {
    switch (type) {
      case 'feature':
        return '✨';
      case 'improvement':
        return '🚀';
      case 'bugfix':
        return '🐛';
      case 'security':
        return '🔒';
      default:
        return '📝';
    }
  };

  const getTypeColor = (type: ChangelogEntry['type']) => {
    switch (type) {
      case 'feature':
        return '#4CAF50';
      case 'improvement':
        return '#2196F3';
      case 'bugfix':
        return '#FF9800';
      case 'security':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="changelog-container">
      <div className="changelog-header">
        <h2>📋 Changelog</h2>
        <p className="changelog-subtitle">
          Track all new features, improvements, and updates to your Miniature Tracker
        </p>
      </div>

      <div className="changelog-list">
        {changelogData.map((entry) => (
          <div key={entry.id} className="changelog-entry">
            <div className="changelog-entry-header">
              <div className="changelog-entry-title">
                <span 
                  className="changelog-type-icon"
                  style={{ color: getTypeColor(entry.type) }}
                >
                  {getTypeIcon(entry.type)}
                </span>
                <h3>{entry.title}</h3>
                <span 
                  className="changelog-type-badge"
                  style={{ backgroundColor: getTypeColor(entry.type) }}
                >
                  {entry.type}
                </span>
              </div>
              <div className="changelog-entry-meta">
                <span className="changelog-version">v{entry.version}</span>
                <span className="changelog-date">{formatDate(entry.date)}</span>
              </div>
            </div>

            <p className="changelog-description">{entry.description}</p>

            <ul className="changelog-items">
              {entry.items.map((item, index) => (
                <li key={index} className="changelog-item">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="changelog-footer">
        <p>
          🎯 Have suggestions for new features? Let us know how we can improve your miniature tracking experience!
        </p>
      </div>
    </div>
  );
};

export default Changelog; 