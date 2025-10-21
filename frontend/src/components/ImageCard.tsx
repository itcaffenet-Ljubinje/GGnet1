/**
 * ImageCard Component
 * 
 * Displays disk image information in card format.
 * Alternative to table view for image listing.
 */

import React from 'react';
import { Image } from '../services/api';

interface ImageCardProps {
  image: Image;
  onDelete?: (imageId: string) => void;
  onSnapshot?: (imageId: string) => void;
  onClone?: (imageId: string) => void;
}

export const ImageCard: React.FC<ImageCardProps> = ({
  image,
  onDelete,
  onSnapshot,
  onClone,
}) => {
  const getTypeColor = (type: string) => {
    return type === 'os'
      ? 'bg-blue-100 text-blue-800'
      : 'bg-purple-100 text-purple-800';
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">{image.name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1 truncate" title={image.storage_path || image.image_id}>
            {image.storage_path || image.image_id}
          </p>
        </div>
        <span
          className={`ml-3 px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(
            image.type
          )}`}
        >
          {image.type.toUpperCase()}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mb-1">Size</p>
          <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">
            {formatBytes(image.size_bytes)}
          </p>
        </div>
        
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mb-1">Created</p>
          <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">
            {new Date(image.creation_date).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Snapshot Info */}
      {image.base_snapshot_id && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-600 font-medium">
            Base Snapshot: {image.base_snapshot_id}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
        {onSnapshot && (
          <button
            onClick={() => onSnapshot(image.image_id)}
            className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
            title="Create snapshot of this image"
          >
            📸 Snapshot
          </button>
        )}

        {onClone && (
          <button
            onClick={() => onClone(image.image_id)}
            className="flex-1 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded hover:bg-purple-700 transition-colors"
            title="Clone this image"
          >
            📋 Clone
          </button>
        )}

        {onDelete && (
          <button
            onClick={() => {
              if (window.confirm(`Delete image "${image.name}"? This cannot be undone.`)) {
                onDelete(image.image_id);
              }
            }}
            className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
            title="Delete this image"
          >
            🗑️ Delete
          </button>
        )}
      </div>

      {/* Metadata */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          ID: {image.image_id} • Version: {image.version}
        </p>
      </div>
    </div>
  );
};

export default ImageCard;

