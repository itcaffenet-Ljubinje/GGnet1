/**
 * MachineCard Component
 * 
 * Displays individual machine information in card format.
 * Alternative to table view for machine listing.
 */

import React from 'react';
import { Machine } from '../services/api';

interface MachineCardProps {
  machine: Machine;
  onPowerOn?: (machineId: number) => void;
  onPowerOff?: (machineId: number) => void;
  onDelete?: (machineId: number) => void;
}

export const MachineCard: React.FC<MachineCardProps> = ({
  machine,
  onPowerOn,
  onPowerOff,
  onDelete,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'offline':
        return 'bg-gray-100 text-gray-800';
      case 'booting':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">{machine.name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">{machine.mac_address}</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
            machine.status
          )}`}
        >
          {machine.status}
        </span>
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        {machine.ip_address && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">IP Address:</span>
            <span className="text-gray-900 dark:text-gray-100 dark:text-gray-800 font-medium">{machine.ip_address}</span>
          </div>
        )}

        {machine.image_name && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Image:</span>
            <span className="text-gray-900 dark:text-gray-100 dark:text-gray-800 font-medium">{machine.image_name}</span>
          </div>
        )}

        {machine.writeback_size > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Writeback:</span>
            <span className="text-gray-900 dark:text-gray-100 dark:text-gray-800 font-medium">
              {(machine.writeback_size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        )}

        {machine.last_boot && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Last Boot:</span>
            <span className="text-gray-900 dark:text-gray-100 dark:text-gray-800 font-medium">
              {new Date(machine.last_boot).toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
        {machine.status === 'offline' && onPowerOn && (
          <button
            onClick={() => onPowerOn(machine.id)}
            className="flex-1 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition-colors"
          >
            Power On
          </button>
        )}

        {machine.status === 'online' && onPowerOff && (
          <button
            onClick={() => onPowerOff(machine.id)}
            className="flex-1 px-4 py-2 bg-yellow-600 text-white text-sm font-medium rounded hover:bg-yellow-700 transition-colors"
          >
            Power Off
          </button>
        )}

        {onDelete && (
          <button
            onClick={() => {
              if (window.confirm(`Delete ${machine.name}?`)) {
                onDelete(machine.id);
              }
            }}
            className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default MachineCard;

