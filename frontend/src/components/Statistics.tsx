import React, { useState, useEffect, useCallback } from 'react';
import { 
  CollectionStatistics, 
  PaintingStatus, 
  GameSystem, 
  UnitType,
  STATUS_INFO,
  GAME_SYSTEM_LABELS,
  UNIT_TYPE_LABELS
} from '../types';
import { miniatureApi } from '../services/api';

interface StatisticsProps {
  onError: (error: string) => void;
}

const Statistics: React.FC<StatisticsProps> = ({ onError }) => {
  const [statistics, setStatistics] = useState<CollectionStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  const loadStatistics = useCallback(async () => {
    try {
      setLoading(true);
      const stats = await miniatureApi.getStatistics();
      setStatistics(stats);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    loadStatistics();
  }, [loadStatistics]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage >= 80) return '#10b981'; // Green
    if (percentage >= 60) return '#f59e0b'; // Yellow
    if (percentage >= 40) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  if (loading) {
    return (
      <div className="statistics-container">
        <div className="loading">Loading statistics...</div>
      </div>
    );
  }

  if (!statistics) {
    return (
      <div className="statistics-container">
        <div className="empty-state">
          <h3>No statistics available</h3>
          <p>Add some units to your collection to see statistics.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="statistics-container">
      <div className="statistics-header">
        <h2>📊 Collection Statistics</h2>
        <button onClick={loadStatistics} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {/* Overview Cards */}
      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-icon">🎨</div>
          <div className="stat-content">
            <h3>{statistics.total_units}</h3>
            <p>Total Units</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔢</div>
          <div className="stat-content">
            <h3>{statistics.total_models}</h3>
            <p>Total Models</p>
          </div>
        </div>

        {statistics.total_cost && (
          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <h3>{formatCurrency(statistics.total_cost)}</h3>
              <p>Total Investment</p>
            </div>
          </div>
        )}

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{statistics.completion_percentage}%</h3>
            <p>Completion Rate</p>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${statistics.completion_percentage}%`,
                  backgroundColor: getProgressBarColor(statistics.completion_percentage)
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="stats-section">
        <h3>📈 Status Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(statistics.status_breakdown).map(([status, count]) => {
            const statusInfo = STATUS_INFO[status as PaintingStatus];
            const percentage = statistics.total_units > 0 ? (count / statistics.total_units * 100) : 0;
            
            return (
              <div key={status} className="breakdown-item">
                <div className="breakdown-header">
                  <div 
                    className="status-indicator"
                    style={{ backgroundColor: statusInfo.color }}
                  />
                  <span className="breakdown-label">{statusInfo.label}</span>
                  <span className="breakdown-count">{count}</span>
                </div>
                <div className="breakdown-bar">
                  <div 
                    className="breakdown-fill"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: statusInfo.color
                    }}
                  />
                </div>
                <div className="breakdown-percentage">{percentage.toFixed(1)}%</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Game System Breakdown */}
      <div className="stats-section">
        <h3>🎮 Game System Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(statistics.game_system_breakdown)
            .filter(([_, count]) => count > 0)
            .map(([system, count]) => {
              const systemLabel = GAME_SYSTEM_LABELS[system as GameSystem];
              const percentage = statistics.total_units > 0 ? (count / statistics.total_units * 100) : 0;
              
              return (
                <div key={system} className="breakdown-item">
                  <div className="breakdown-header">
                    <span className="breakdown-label">{systemLabel}</span>
                    <span className="breakdown-count">{count}</span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-fill"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: '#3b82f6'
                      }}
                    />
                  </div>
                  <div className="breakdown-percentage">{percentage.toFixed(1)}%</div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Unit Type Breakdown */}
      <div className="stats-section">
        <h3>⚔️ Unit Type Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(statistics.unit_type_breakdown)
            .filter(([_, count]) => count > 0)
            .map(([type, count]) => {
              const typeLabel = UNIT_TYPE_LABELS[type as UnitType];
              const percentage = statistics.total_units > 0 ? (count / statistics.total_units * 100) : 0;
              
              return (
                <div key={type} className="breakdown-item">
                  <div className="breakdown-header">
                    <span className="breakdown-label">{typeLabel}</span>
                    <span className="breakdown-count">{count}</span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-fill"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: '#10b981'
                      }}
                    />
                  </div>
                  <div className="breakdown-percentage">{percentage.toFixed(1)}%</div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Faction Breakdown */}
      <div className="stats-section">
        <h3>🏛️ Faction Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(statistics.faction_breakdown)
            .sort(([,a], [,b]) => b - a) // Sort by count descending
            .slice(0, 10) // Show top 10 factions
            .map(([faction, count]) => {
              const percentage = statistics.total_units > 0 ? (count / statistics.total_units * 100) : 0;
              
              return (
                <div key={faction} className="breakdown-item">
                  <div className="breakdown-header">
                    <span className="breakdown-label">{faction}</span>
                    <span className="breakdown-count">{count}</span>
                  </div>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-fill"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: '#8b5cf6'
                      }}
                    />
                  </div>
                  <div className="breakdown-percentage">{percentage.toFixed(1)}%</div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Collection Insights */}
      <div className="stats-section">
        <h3>💡 Collection Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>Most Popular Game System</h4>
            <p>
              {Object.entries(statistics.game_system_breakdown)
                .filter(([_, count]) => count > 0)
                .sort(([,a], [,b]) => b - a)[0]?.[0] 
                ? GAME_SYSTEM_LABELS[Object.entries(statistics.game_system_breakdown)
                    .filter(([_, count]) => count > 0)
                    .sort(([,a], [,b]) => b - a)[0][0] as GameSystem]
                : 'None'}
            </p>
          </div>

          <div className="insight-card">
            <h4>Most Popular Faction</h4>
            <p>
              {Object.entries(statistics.faction_breakdown)
                .sort(([,a], [,b]) => b - a)[0]?.[0] || 'None'}
            </p>
          </div>

          <div className="insight-card">
            <h4>Average Models per Unit</h4>
            <p>
              {statistics.total_units > 0 
                ? (statistics.total_models / statistics.total_units).toFixed(1)
                : '0'}
            </p>
          </div>

          {statistics.total_cost && (
            <div className="insight-card">
              <h4>Average Cost per Unit</h4>
              <p>
                {formatCurrency(statistics.total_cost / statistics.total_units)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Statistics; 