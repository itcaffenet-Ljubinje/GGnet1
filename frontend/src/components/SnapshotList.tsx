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
  onRestore?: (snapshotId: string) => void;
  onDelete?: (snapshotId: string) => void;
  onMakeCurrent?: (snapshotId: string) => void;
}

export const SnapshotList: React.FC<SnapshotListProps> = ({
  snapshots,
  onRestore,
  onDelete,
  onMakeCurrent,
}) => {
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
      <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
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
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">No snapshots available</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500">Create a snapshot to preserve the current state</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {snapshots.map((snapshot, index) => {
        const isLatest = index === 0;
        const isCurrent = false; // TODO: Track current snapshot in backend

        return (
          <div
            key={snapshot.snapshot_id}
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
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">
                    Snapshot {snapshot.name || snapshot.snapshot_id}
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
                    <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Created:</span>
                    <p className="font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800">
                      {formatDate(snapshot.created_at)}
                    </p>
                  </div>

                  <div>
                    <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">ID:</span>
                    <p className="font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800">
                      {snapshot.snapshot_id}
                    </p>
                  </div>

                  <div>
                    <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Path:</span>
                    <p className="font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800 truncate" title={snapshot.path}>
                      {snapshot.path.split('/').pop()}
                    </p>
                  </div>
                </div>

                {snapshot.comment && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500 italic">
                    "{snapshot.comment}"
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 ml-4">
                {!isCurrent && onMakeCurrent && (
                  <button
                    onClick={() => onMakeCurrent(snapshot.snapshot_id)}
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
                          `Restore to snapshot ${snapshot.snapshot_id}? Current changes will be lost.`
                        )
                      ) {
                        onRestore(snapshot.snapshot_id);
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
                          `Delete snapshot ${snapshot.snapshot_id}? This cannot be undone.`
                        )
                      ) {
                        onDelete(snapshot.snapshot_id);
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

