import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getImages, createImage, deleteImage, ImageCreate, uploadImage } from '../services/api';
import { Upload, Plus, Trash2, Camera } from 'lucide-react';

const Images = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [newImage, setNewImage] = useState<ImageCreate>({
    name: '',
    type: 'os',
    description: '',
  });
  const [imageSize, setImageSize] = useState({ value: '', unit: 'GB' });
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [filter, setFilter] = useState<'all' | 'os' | 'game'>('all');

  const queryClient = useQueryClient();

  // Fetch images
  const { data: images, isLoading, error } = useQuery({
    queryKey: ['images', filter],
    queryFn: () => getImages(filter === 'all' ? undefined : filter),
    refetchInterval: 30000,
  });

  // Create image mutation
  const createMutation = useMutation({
    mutationFn: createImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] });
      setShowAddForm(false);
      setNewImage({ name: '', type: 'os', description: '' });
      setImageSize({ value: '', unit: 'GB' });
      alert(`Image created successfully! Size: ${imageSize.value} ${imageSize.unit}. You can now upload the disk image to the storage array.`);
    },
    onError: (error: Error) => {
      alert(`Failed to create image: ${error.message}`);
    },
  });

  // Delete image mutation
  const deleteMutation = useMutation({
    mutationFn: deleteImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] });
      alert('Image deleted successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to delete image: ${error.message}`);
    },
  });

  // Upload image mutation
  const uploadMutation = useMutation({
    mutationFn: uploadImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] });
      setShowUploadForm(false);
      setUploadFile(null);
      alert('Image uploaded successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to upload image: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newImage.name) {
      alert('Image name is required!');
      return;
    }
    createMutation.mutate(newImage);
  };

  const handleDelete = (id: string, name: string) => {
    if (
      window.confirm(
        `Delete image "${name}"? This will remove the image from all machines. This cannot be undone.`
      )
    ) {
      deleteMutation.mutate(id);
    }
  };

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !newImage.name) {
      alert('Please select a file and enter image name!');
      return;
    }
    uploadMutation.mutate({
      file: uploadFile,
      name: newImage.name,
      type: newImage.type,
      description: newImage.description || undefined,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading images...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        Error loading images: {(error as Error).message}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800">Disk Images</h1>
          <p className="text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
            Manage OS and game images ({images?.length || 0} total)
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Upload size={20} />
            Upload Image
          </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            Create Image
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Images
        </button>
        <button
          onClick={() => setFilter('os')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'os'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          OS Images
        </button>
        <button
          onClick={() => setFilter('game')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'game'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Game Images
        </button>
      </div>

      {/* Upload Image Form */}
      {showUploadForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border-2 border-green-500">
          <h2 className="text-xl font-bold mb-4">Upload Image File</h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Image Name *
                </label>
                <input
                  type="text"
                  value={newImage.name}
                  onChange={(e) => setNewImage({ ...newImage, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., Windows-10-Pro"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Type *
                </label>
                <select
                  value={newImage.type}
                  onChange={(e) =>
                    setNewImage({ ...newImage, type: e.target.value as 'os' | 'game' })
                  }
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                >
                  <option value="os">Operating System</option>
                  <option value="game">Game Image</option>
                  <option value="windows">Windows OS</option>
                  <option value="linux">Linux OS</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Description
              </label>
              <textarea
                value={newImage.description}
                onChange={(e) => setNewImage({ ...newImage, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                rows={2}
                placeholder="Image description..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Image File * (VHD, VHDX, ISO, IMG)
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                accept=".vhd,.vhdx,.iso,.img,.raw"
                required
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                Supported formats: VHD, VHDX, ISO, IMG, RAW
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={uploadMutation.isPending}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {uploadMutation.isPending ? 'Uploading...' : 'Upload Image'}
              </button>
              <button
                type="button"
                onClick={() => setShowUploadForm(false)}
                className="px-6 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 dark:text-gray-600 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Add Image Form */}
      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border-2 border-blue-500">
          <h2 className="text-xl font-bold mb-4">Create New Image</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Image Name *
                </label>
                <input
                  type="text"
                  value={newImage.name}
                  onChange={(e) => setNewImage({ ...newImage, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Ubuntu-22.04-LTS"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Type *
                </label>
                <select
                  value={newImage.type}
                  onChange={(e) =>
                    setNewImage({ ...newImage, type: e.target.value as 'os' | 'game' })
                  }
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="os">Operating System</option>
                  <option value="game">Game Image</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={newImage.description || ''}
                onChange={(e) => setNewImage({ ...newImage, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Ubuntu 22.04 LTS with NVIDIA drivers"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Image Size (GB/TB) *
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={imageSize.value}
                  onChange={(e) => setImageSize({ ...imageSize, value: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 100"
                  min="1"
                  step="0.1"
                  required
                />
                <select
                  value={imageSize.unit}
                  onChange={(e) => setImageSize({ ...imageSize, unit: e.target.value })}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="GB">GB</option>
                  <option value="TB">TB</option>
                </select>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                Recommended: {newImage.type === 'os' ? '50-100 GB' : '200-500 GB'} for {newImage.type === 'os' ? 'OS images' : 'Game images'}
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> After creating the image record, you'll need to upload the
                actual disk image file to: <code className="bg-yellow-100 px-2 py-1 rounded">/srv/ggnet/images/</code>
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Image'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-6 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 dark:text-gray-600 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Images Grid */}
      {images && images.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image) => (
            <div
              key={image.image_id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 dark:text-gray-800">{image.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1 truncate" title={image.storage_path || image.image_id}>
                    {image.storage_path || image.image_id}
                  </p>
                </div>
                <span
                  className={`ml-3 px-3 py-1 rounded-full text-xs font-medium ${
                    image.type === 'os'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}
                >
                  {image.type.toUpperCase()}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Size:</span>
                  <span className="font-medium">{formatBytes(image.size_bytes)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Created:</span>
                  <span className="font-medium">
                    {new Date(image.creation_date).toLocaleDateString()}
                  </span>
                </div>
                {image.base_snapshot_id && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400 dark:text-gray-500">Base Snapshot:</span>
                    <span className="font-medium">{image.base_snapshot_id}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center justify-center gap-1"
                  title="Create snapshot"
                >
                  <Camera size={16} />
                  Snapshot
                </button>
                <button
                  onClick={() => handleDelete(image.image_id, image.name)}
                  className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 flex items-center justify-center gap-1"
                  title="Delete image"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
          <p className="text-gray-600 dark:text-gray-400 dark:text-gray-500 mb-4">No images uploaded yet</p>
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            Create Your First Image
          </button>
        </div>
      )}
    </div>
  );
};

export default Images;
