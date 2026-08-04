import React, { useState } from 'react';
import { User } from 'lucide-react';

interface AvatarProps {
  src: string;
  name: string;
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({ src, name, className = 'w-16 h-16' }) => {
  const [error, setError] = useState(false);

  const getImageSrc = () => {
    if (!src || error) return null;
    const trimmed = src.trim();
    if (trimmed.startsWith('data:') || trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('/')) {
      return trimmed;
    }
    if (trimmed.length > 50) {
      return `data:image/jpeg;base64,${trimmed}`;
    }
    return null;
  };

  const finalSrc = getImageSrc();

  // Get initials from name
  const getInitials = (n: string) => {
    const parts = n.replace(/^(Hon|Sen|Dr|Prof|Mr|Mrs|Chief|Alhaji|Engr|Arc|Barr)\.?\s+/i, '').trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return parts[0] ? parts[0][0].toUpperCase() : 'NA';
  };

  if (!finalSrc) {
    return (
      <div className={`${className} rounded-full bg-slate-800 dark:bg-slate-700 border-2 border-slate-700 dark:border-slate-600 flex items-center justify-center font-bold text-slate-300 shadow-md`}>
        {getInitials(name) || <User className="w-1/2 h-1/2 text-slate-400" />}
      </div>
    );
  }

  return (
    <img
      src={finalSrc}
      alt={name}
      onError={() => setError(true)}
      loading="lazy"
      className={`${className} rounded-full object-cover [object-position:center_20%] border-2 border-slate-700 dark:border-slate-600 shadow-md`}
    />
  );
};

