import { ChangelogEntry } from '../types';

export const changelogData: ChangelogEntry[] = [
  {
    id: 'v1.5.0',
    date: '2025-01-26',
    version: '1.5.0',
    title: 'Complete Application Overhaul - Units, Statistics & Enhanced UX',
    description: 'Major transformation from miniature tracking to comprehensive unit management with statistics, import/export, and dramatically improved user experience',
    type: 'feature',
    items: [
      '🎯 **Complete Model Transformation**: Migrated from Miniatures to comprehensive Unit tracking system',
      '🎮 **Game System Integration**: Full support for Warhammer 40K, Age of Sigmar, D&D, and other game systems',
      '📊 **Advanced Statistics Dashboard**: Collection analytics with status, faction, and game system breakdowns',
      '📈 **Trend Analysis**: Comprehensive trend tracking with purchase patterns and spending analysis',
      '📁 **Import/Export System**: Full CSV/JSON import/export with modal interface and validation',
      '🔍 **Enhanced Unit Management**: Quantity tracking, base dimensions, cost tracking, and faction autocomplete',
      '🎨 **Complete UI Redesign**: Modern glassmorphism design with improved mobile responsiveness',
      '🔧 **Player Search Fixes**: Resolved display issues and synchronized game systems across components',
      '📧 **Email System Improvements**: Enhanced verification UX and comprehensive feedback forms',
      '🛠️ **Admin Tools**: User deletion functionality and database migration endpoints',
      '🎯 **Navigation Overhaul**: Streamlined interface with better contrast and user feedback integration',
      '📱 **Mobile Optimization**: Improved responsive design for import/export controls and navigation',
      '🔐 **Authentication Enhancements**: OAuth improvements and simplified login experience',
      '🌍 **International Support**: Worldwide geocoding replacing UK-only postcodes',
      '🧪 **Comprehensive Testing**: Updated test coverage for all new features and authentication',
      '⚡ **Performance Improvements**: Optimized database queries and frontend rendering',
      '🎨 **Status Management**: Enhanced status history with editable dates and timeline exports',
      '🔧 **Developer Experience**: Improved error handling, debugging tools, and code organization'
    ]
  },
  {
    id: 'v1.4.0',
    date: '2025-01-15',
    version: '1.4.0',
    title: 'Player Discovery System',
    description: 'Find and connect with other wargamers in your area',
    type: 'feature',
    items: [
      'Player preferences with postcode-based location',
      'Comprehensive game library (20+ wargames including Warhammer 40K, Age of Sigmar, Kill Team)',
      'Distance-based player search with range slider (5-500km)',
      'Game type preferences (Competitive/Narrative)',
      'Optional bio field for player profiles',
      'Email contact option in player discovery',
      'Game and preference filtering in search',
      'Privacy-aware postcode display',
      'Local development environment improvements',
      'File-based database for development testing'
    ]
  },
  {
    id: 'v1.3.0',
    date: '2025-05-24',
    version: '1.3.0',
    title: 'Password Recovery System',
    description: 'Complete password reset functionality with email integration',
    type: 'feature',
    items: [
      'Email-based password reset with secure tokens',
      'Gmail SMTP integration for sending reset emails',
      'Forgot password form with validation',
      'Reset password form with confirmation',
      'Token-based security with 1-hour expiration',
      'Production-ready email service architecture'
    ]
  },
  {
    id: 'v1.2.0',
    date: '2025-05-23',
    version: '1.2.0', 
    title: 'Enhanced UI & Status Management',
    description: 'Major UI improvements and advanced status tracking features',
    type: 'feature',
    items: [
      'Table view for miniatures with sorting and filtering',
      'Expandable status history for each miniature',
      'Manual status log entry creation and editing',
      'Enhanced card view with better status visualization',
      'Improved mobile responsiveness',
      'Better color coding for painting statuses'
    ]
  },
  {
    id: 'v1.1.0',
    date: '2025-05-22',
    version: '1.1.0',
    title: 'Authentication & User Management',
    description: 'Secure user authentication and session management',
    type: 'feature',
    items: [
      'User registration and login system',
      'JWT-based authentication with secure tokens',
      'Protected routes and user sessions',
      'User profile management',
      'Secure token storage and refresh'
    ]
  },
  {
    id: 'v1.0.0',
    date: '2025-05-21',
    version: '1.0.0',
    title: 'Core Miniature Tracking',
    description: 'Initial release with basic miniature tracking functionality',
    type: 'feature',
    items: [
      'Create, edit, and delete miniatures',
      'Track painting status (Want to Buy, Purchased, Assembled, Primed, Game Ready, Showcase)',
      'Add army faction and miniature names',
      'Basic status history tracking',
      'Responsive web interface',
      'Local data persistence'
    ]
  }
];

export const getLatestVersion = (): string => {
  return changelogData[0]?.version || '1.0.0';
};

export const getChangelogByVersion = (version: string): ChangelogEntry | undefined => {
  return changelogData.find(entry => entry.version === version);
}; 