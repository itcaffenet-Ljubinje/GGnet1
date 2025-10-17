/**
 * SnapshotList Component
 * 
 * Displays a list of snapshots for a specific image.
 * Supports rollback and deletion operations.
 */

import React from 'react';
import { Snapshot } from '../services/api';

interface SnapshotListProps {
  snapshots: Snapshot[];
  onRestore?: (snapshotId: number) => void;
  onDelete?: (snapshotId: number) => void;
  onMakeCurrent?: (snapshotId: number) => void;
}

export const SnapshotList: React.FC<SnapshotListProps> = ({
  snapshots,
  onRestore,
  onDelete,
  onMakeCurrent,
}) => {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
  };

  if (snapshots.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="mt-2 text-sm text-gray-600">No snapshots available</p>
        <p className="text-xs text-gray-500">Create a snapshot to preserve the current state</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {snapshots.map((snapshot, index) => {
        const isLatest = index === 0;
        const isCurrent = snapshot.is_current;

        return (
          <div
            key={snapshot.id}
            className={`bg-white rounded-lg border-2 p-4 transition-all ${
              isCurrent
                ? 'border-blue-500 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
            }`}
          >
            <div className="flex items-center justify-between">
              {/* Snapshot Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-semibold text-gray-900">
                    Snapshot #{snapshot.id}
                  </h4>
                  
                  {isCurrent && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                      CURRENT
                    </span>
                  )}
                  
                  {isLatest && !isCurrent && (
                    <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-medium rounded">
                      LATEST
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <p className="font-medium text-gray-900">
                      {formatDate(snapshot.created_at)}
                    </p>
                  </div>

                  <div>
                    <span className="text-gray-500">Size:</span>
                    <p className="font-medium text-gray-900">
                      {formatBytes(snapshot.size_bytes)}
                    </p>
                  </div>

                  <div>
                    <span className="text-gray-500">Path:</span>
                    <p className="font-medium text-gray-900 truncate" title={snapshot.path}>
                      {snapshot.path.split('/').pop()}
                    </p>
                  </div>
                </div>

                {snapshot.description && (
                  <p className="mt-2 text-sm text-gray-600 italic">
                    "{snapshot.description}"
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 ml-4">
                {!isCurrent && onMakeCurrent && (
                  <button
                    onClick={() => onMakeCurrent(snapshot.id)}
                    className="px-3 py-2 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
                    title="Set as current snapshot"
                  >
                    Make Current
                  </button>
                )}

                {onRestore && (
                  <button
                    onClick={() => {
                      if (
                        window.confirm(
                          `Restore to snapshot #${snapshot.id}? Current changes will be lost.`
                        )
                      ) {
                        onRestore(snapshot.id);
                      }
                    }}
                    className="px-3 py-2 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 transition-colors"
                    title="Restore to this snapshot"
                  >
                    Restore
                  </button>
                )}

                {!isCurrent && onDelete && (
                  <button
                    onClick={() => {
                      if (
                        window.confirm(
                          `Delete snapshot #${snapshot.id}? This cannot be undone.`
                        )
                      ) {
                        onDelete(snapshot.id);
                      }
                    }}
                    className="px-3 py-2 bg-red-600 text-white text-xs font-medium rounded hover:bg-red-700 transition-colors"
                    title="Delete this snapshot"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SnapshotList;

