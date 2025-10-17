import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getSnapshots,
  createSnapshot,
  deleteSnapshot,
  SnapshotCreate,
  getImages,
} from '../services/api';
import { Camera, Plus, Trash2, RotateCcw } from 'lucide-react';

const Snapshots = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newSnapshot, setNewSnapshot] = useState<SnapshotCreate>({
    image_id: 0,
    comment: '',
    created_by: 'admin',
  });

  const queryClient = useQueryClient();

  // Fetch snapshots and images
  const { data: snapshots, isLoading, error } = useQuery({
    queryKey: ['snapshots'],
    queryFn: getSnapshots,
    refetchInterval: 30000,
  });

  const { data: images } = useQuery({
    queryKey: ['images'],
    queryFn: () => getImages(),
  });

  // Create snapshot mutation
  const createMutation = useMutation({
    mutationFn: createSnapshot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['snapshots'] });
      setShowCreateForm(false);
      setNewSnapshot({ image_id: 0, comment: '', created_by: 'admin' });
      alert('Snapshot created successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to create snapshot: ${error.message}`);
    },
  });

  // Delete snapshot mutation
  const deleteMutation = useMutation({
    mutationFn: deleteSnapshot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['snapshots'] });
      alert('Snapshot deleted successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to delete snapshot: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSnapshot.image_id) {
      alert('Please select an image!');
      return;
    }
    createMutation.mutate(newSnapshot);
  };

  const handleDelete = (id: number) => {
    if (window.confirm(`Delete this snapshot? This cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
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

  if (isLoading) {
    return <div className="text-center py-12">Loading snapshots...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        Error loading snapshots: {(error as Error).message}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Snapshots</h1>
          <p className="text-gray-500 mt-1">
            Point-in-time captures of disk images ({snapshots?.length || 0} total)
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Camera size={20} />
          Create Snapshot
        </button>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">About Snapshots</h3>
        <p className="text-sm text-blue-800">
          Snapshots are immutable point-in-time captures of disk images. They allow you to preserve
          the current state before making changes, and can be restored if needed. Snapshots use ZFS
          or filesystem-level COW (copy-on-write) for efficient storage.
        </p>
      </div>

      {/* Create Snapshot Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6 border-2 border-blue-500">
          <h2 className="text-xl font-bold mb-4">Create New Snapshot</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Image *
                </label>
                <select
                  value={newSnapshot.image_id}
                  onChange={(e) =>
                    setNewSnapshot({ ...newSnapshot, image_id: parseInt(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">-- Select Image --</option>
                  {images?.map((image) => (
                    <option key={image.id} value={image.id}>
                      {image.name} ({image.type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Created By
                </label>
                <input
                  type="text"
                  value={newSnapshot.created_by}
                  onChange={(e) =>
                    setNewSnapshot({ ...newSnapshot, created_by: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="admin"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comment / Description
              </label>
              <textarea
                value={newSnapshot.comment || ''}
                onChange={(e) => setNewSnapshot({ ...newSnapshot, comment: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Before system update"
                rows={3}
              />
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Snapshot'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Snapshots List */}
      {snapshots && snapshots.length > 0 ? (
        <div className="space-y-4">
          {snapshots.map((snapshot) => {
            const image = images?.find((img) => img.id === snapshot.image_id);
            return (
              <div
                key={snapshot.id}
                className="bg-white rounded-lg border-2 border-gray-200 p-6 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Snapshot #{snapshot.id}
                      </h3>
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {image?.name || `Image #${snapshot.image_id}`}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                      <div>
                        <span className="text-gray-500">Created:</span>
                        <p className="font-medium text-gray-900">
                          {formatDate(snapshot.created_at)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Created By:</span>
                        <p className="font-medium text-gray-900">
                          {snapshot.created_by || 'Unknown'}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Path:</span>
                        <p
                          className="font-medium text-gray-900 truncate"
                          title={snapshot.path}
                        >
                          {snapshot.path.split('/').pop()}
                        </p>
                      </div>
                    </div>

                    {snapshot.comment && (
                      <p className="text-sm text-gray-600 italic mb-3">"{snapshot.comment}"</p>
                    )}
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      className="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 flex items-center gap-1"
                      title="Restore to this snapshot"
                    >
                      <RotateCcw size={16} />
                      Restore
                    </button>
                    <button
                      onClick={() => handleDelete(snapshot.id)}
                      className="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 flex items-center gap-1"
                      title="Delete snapshot"
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-4">No snapshots created yet</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            Create Your First Snapshot
          </button>
        </div>
      )}
    </div>
  );
};

export default Snapshots;
