import React from 'react';
import { Miniature } from '../types';
import MiniatureCard from './MiniatureCard';

interface MiniatureListProps {
  miniatures: Miniature[];
  onUpdate: (id: string, updates: Partial<Miniature>) => void;
  onDelete: (id: string) => void;
}

const MiniatureList: React.FC<MiniatureListProps> = ({
  miniatures,
  onUpdate,
  onDelete
}) => {
  if (miniatures.length === 0) {
    return (
      <div className="empty-state">
        <h3>No miniatures yet!</h3>
        <p>Add your first Warhammer miniature to start tracking your collection.</p>
      </div>
    );
  }

  return (
    <div className="miniature-list">
      <h2>Your Collection ({miniatures.length})</h2>
      <div className="miniature-grid">
        {miniatures.map(miniature => (
          <MiniatureCard
            key={miniature.id}
            miniature={miniature}
            onUpdate={onUpdate}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
};

export default MiniatureList; 