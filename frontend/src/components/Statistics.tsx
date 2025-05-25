import React, { useState, useEffect, useCallback } from 'react';
import { 
  CollectionStatistics, 
  TrendAnalysis,
  TrendRequest,
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
  const [trendAnalysis, setTrendAnalysis] = useState<TrendAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [trendLoading, setTrendLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'trends'>('overview');
  const [statusFilter, setStatusFilter] = useState<PaintingStatus | ''>('');
  
  // Trend analysis filters
  const [trendFilters, setTrendFilters] = useState<TrendRequest>({
    from_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 1 year ago
    to_date: new Date().toISOString().split('T')[0], // Today
    group_by: 'month'
  });

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

  const loadTrendAnalysis = useCallback(async () => {
    try {
      setTrendLoading(true);
      const trends = await miniatureApi.getTrendAnalysis(trendFilters);
      setTrendAnalysis(trends);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to load trend analysis');
    } finally {
      setTrendLoading(false);
    }
  }, [trendFilters, onError]);

  useEffect(() => {
    loadStatistics();
  }, [loadStatistics]);

  useEffect(() => {
    if (activeTab === 'trends') {
      loadTrendAnalysis();
    }
  }, [activeTab, loadTrendAnalysis]);

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

  const handleTrendFilterChange = (field: keyof TrendRequest, value: string) => {
    setTrendFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatTrendDate = (dateStr: string, groupBy: string) => {
    if (groupBy === 'month') {
      const [year, month] = dateStr.split('-');
      return new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short' 
      });
    }
    return dateStr;
  };

  // Create filtered statistics based on status filter
  const getFilteredStatistics = () => {
    if (!statistics || !statusFilter) return statistics;
    
    // Calculate filtered statistics
    const filteredStats = {
      ...statistics,
      total_units: statistics.status_breakdown[statusFilter] || 0,
      total_models: statistics.total_models, // This would need to be calculated properly in a real implementation
      completion_percentage: statusFilter === PaintingStatus.PARADE_READY ? 100 : 
                           statusFilter === PaintingStatus.GAME_READY ? 80 :
                           statusFilter === PaintingStatus.PRIMED ? 40 :
                           statusFilter === PaintingStatus.ASSEMBLED ? 20 :
                           statusFilter === PaintingStatus.PURCHASED ? 10 : 0,
      status_breakdown: { [statusFilter]: statistics.status_breakdown[statusFilter] || 0 }
    };
    
    return filteredStats;
  };

  const renderStatusChart = () => {
    if (!statistics) return null;
    
    const statusData = Object.entries(statistics.status_breakdown)
      .map(([status, count]) => ({
        status: status as PaintingStatus,
        count,
        info: STATUS_INFO[status as PaintingStatus]
      }))
      .filter(item => item.count > 0)
      .sort((a, b) => b.count - a.count);

    const maxCount = Math.max(...statusData.map(d => d.count));
    
    return (
      <div className="status-chart-section">
        <h3>📊 Status Distribution Chart</h3>
        <div className="status-chart">
          {statusData.map((item, index) => {
            const height = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
            const isSelected = statusFilter === item.status;
            
            return (
              <div 
                key={item.status} 
                className={`status-chart-bar ${isSelected ? 'selected' : ''}`}
                onClick={() => setStatusFilter(statusFilter === item.status ? '' : item.status)}
                style={{ cursor: 'pointer' }}
              >
                <div 
                  className="status-bar"
                  style={{ 
                    height: `${height}%`,
                    backgroundColor: item.info.color,
                    opacity: isSelected ? 1 : 0.8
                  }}
                  title={`${item.info.label}: ${item.count} units`}
                />
                <div className="status-bar-label">
                  {item.info.label}
                </div>
                <div className="status-bar-count">
                  {item.count}
                </div>
              </div>
            );
          })}
        </div>
        <p className="chart-help-text">
          💡 Click on a status bar to filter the statistics by that status
        </p>
      </div>
    );
  };

  const renderTrendChart = (data: any[], title: string, valueKey: 'count' | 'cost' = 'count') => {
    if (!data || data.length === 0) return null;

    const maxValue = Math.max(...data.map(d => valueKey === 'cost' ? (d.cost || 0) : d.count));
    
    return (
      <div className="trend-chart">
        <h4>{title}</h4>
        <div className="chart-container">
          {data.map((point, index) => {
            const value = valueKey === 'cost' ? (point.cost || 0) : point.count;
            const height = maxValue > 0 ? (value / maxValue) * 100 : 0;
            
            return (
              <div key={index} className="chart-bar-container">
                <div 
                  className="chart-bar"
                  style={{ 
                    height: `${height}%`,
                    backgroundColor: valueKey === 'cost' ? '#10b981' : '#3b82f6'
                  }}
                  title={`${formatTrendDate(point.date, trendFilters.group_by)}: ${valueKey === 'cost' ? formatCurrency(value) : value}`}
                />
                <div className="chart-label">
                  {formatTrendDate(point.date, trendFilters.group_by)}
                </div>
                <div className="chart-value">
                  {valueKey === 'cost' ? formatCurrency(value) : value}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
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
        <div className="tab-buttons">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📈 Overview
          </button>
          <button 
            className={`tab-button ${activeTab === 'trends' ? 'active' : ''}`}
            onClick={() => setActiveTab('trends')}
          >
            📊 Trends
          </button>
        </div>
        <div className="header-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as PaintingStatus | '')}
            className="status-filter-select"
          >
            <option value="">All Statuses</option>
            {Object.entries(STATUS_INFO).map(([status, info]) => (
              <option key={status} value={status}>
                {info.label}
              </option>
            ))}
          </select>
          <button onClick={loadStatistics} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {activeTab === 'overview' && statistics && (
        <>
          {/* Status Chart */}
          {renderStatusChart()}

          {/* Overview Cards */}
          <div className="stats-overview">
            <div className="stat-card">
              <div className="stat-icon">🎨</div>
              <div className="stat-content">
                <h3>{(getFilteredStatistics() || statistics).total_units}</h3>
                <p>{statusFilter ? `${STATUS_INFO[statusFilter].label} Units` : 'Total Units'}</p>
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
                <h3>{(getFilteredStatistics() || statistics).completion_percentage}%</h3>
                <p>{statusFilter ? `${STATUS_INFO[statusFilter].label} Progress` : 'Completion Rate'}</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${(getFilteredStatistics() || statistics).completion_percentage}%`,
                      backgroundColor: getProgressBarColor((getFilteredStatistics() || statistics).completion_percentage)
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
        </>
      )}

      {activeTab === 'trends' && (
        <>
          {/* Trend Filters */}
          <div className="trend-filters">
            <div className="filter-group">
              <label>From Date:</label>
              <input
                type="date"
                value={trendFilters.from_date || ''}
                onChange={(e) => handleTrendFilterChange('from_date', e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label>To Date:</label>
              <input
                type="date"
                value={trendFilters.to_date || ''}
                onChange={(e) => handleTrendFilterChange('to_date', e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label>Group By:</label>
              <select
                value={trendFilters.group_by}
                onChange={(e) => handleTrendFilterChange('group_by', e.target.value)}
              >
                <option value="day">Daily</option>
                <option value="week">Weekly</option>
                <option value="month">Monthly</option>
                <option value="year">Yearly</option>
              </select>
            </div>
            <button onClick={loadTrendAnalysis} className="apply-filters-button" disabled={trendLoading}>
              {trendLoading ? 'Loading...' : 'Apply Filters'}
            </button>
          </div>

          {trendLoading && <div className="loading">Loading trend analysis...</div>}

          {trendAnalysis && (
            <>
              {/* Summary Cards */}
              <div className="stats-overview">
                <div className="stat-card">
                  <div className="stat-icon">🛒</div>
                  <div className="stat-content">
                    <h3>{trendAnalysis.total_purchased}</h3>
                    <p>Total Purchased</p>
                    <small>in selected period</small>
                  </div>
                </div>

                {trendAnalysis.total_spent && (
                  <div className="stat-card">
                    <div className="stat-icon">💸</div>
                    <div className="stat-content">
                      <h3>{formatCurrency(trendAnalysis.total_spent)}</h3>
                      <p>Total Spent</p>
                      <small>in selected period</small>
                    </div>
                  </div>
                )}

                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <div className="stat-content">
                    <h3>{trendAnalysis.average_monthly_purchases}</h3>
                    <p>Avg. Monthly Purchases</p>
                    <small>in selected period</small>
                  </div>
                </div>

                {trendAnalysis.average_monthly_spending && (
                  <div className="stat-card">
                    <div className="stat-icon">💰</div>
                    <div className="stat-content">
                      <h3>{formatCurrency(trendAnalysis.average_monthly_spending)}</h3>
                      <p>Avg. Monthly Spending</p>
                      <small>in selected period</small>
                    </div>
                  </div>
                )}
              </div>

              {/* Trend Charts */}
              <div className="trends-section">
                <div className="trends-grid">
                  {renderTrendChart(trendAnalysis.purchases_over_time, '🛒 Purchases Over Time', 'count')}
                  {trendAnalysis.spending_over_time.some(p => p.cost && p.cost > 0) && 
                    renderTrendChart(trendAnalysis.spending_over_time, '💸 Spending Over Time', 'cost')}
                </div>

                {/* Status Trends */}
                <div className="status-trends-section">
                  <h3>📊 Status Changes Over Time</h3>
                  <div className="status-trends-grid">
                    {trendAnalysis.status_trends
                      .filter(trend => trend.data_points.some(p => p.count > 0))
                      .map(trend => (
                        <div key={trend.status} className="status-trend-chart">
                          <h4 style={{ color: STATUS_INFO[trend.status].color }}>
                            {STATUS_INFO[trend.status].label}
                          </h4>
                          <div className="mini-chart">
                            {trend.data_points.map((point, index) => {
                              const maxInTrend = Math.max(...trend.data_points.map(p => p.count));
                              const height = maxInTrend > 0 ? (point.count / maxInTrend) * 100 : 0;
                              
                              return (
                                <div key={index} className="mini-bar-container">
                                  <div 
                                    className="mini-bar"
                                    style={{ 
                                      height: `${height}%`,
                                      backgroundColor: STATUS_INFO[trend.status].color
                                    }}
                                    title={`${formatTrendDate(point.date, trendFilters.group_by)}: ${point.count}`}
                                  />
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Most Active Period */}
                {trendAnalysis.most_active_month && (
                  <div className="stats-section">
                    <h3>🏆 Most Active Period</h3>
                    <div className="insight-card">
                      <h4>{formatTrendDate(trendAnalysis.most_active_month, trendFilters.group_by)}</h4>
                      <p>Your most active period for purchases</p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Statistics; 