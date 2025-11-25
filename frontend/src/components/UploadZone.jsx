import React, { useState } from 'react';
import { uploadImage, getImageUrl } from '../services/api';

const UploadZone = ({ onUploadComplete }) => {
    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [preview, setPreview] = useState(null);
    const [error, setError] = useState(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleFile = async (file) => {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            setError('Invalid file type. Please upload JPG, JPEG, or PNG images.');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            setError('File size exceeds 16MB limit.');
            return;
        }

        setError(null);

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(file);

        // Upload file
        setUploading(true);
        setProgress(0);

        try {
            const response = await uploadImage(file, (percent) => {
                setProgress(percent);
            });

            console.log('Upload response:', response.data);

            if (response.data.success) {
                if (onUploadComplete) {
                    onUploadComplete(response.data);
                }
            } else {
                setError('Upload failed. Please try again.');
            }
        } catch (err) {
            console.error('Upload error:', err);
            setError(err.response?.data?.error || 'Upload failed. Please try again.');
        } finally {
            setUploading(false);
            setProgress(0);
        }
    };

    return (
        <div className="card">
            <div className="card-header">Upload Image for Detection</div>
            <div className="card-body">
                <div
                    className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('file-input').click()}
                >
                    <input
                        id="file-input"
                        type="file"
                        accept="image/jpeg,image/jpg,image/png"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />

                    {preview ? (
                        <div>
                            <img
                                src={preview}
                                alt="Preview"
                                style={{
                                    maxWidth: '100%',
                                    maxHeight: '300px',
                                    borderRadius: 'var(--radius-md)',
                                    marginBottom: 'var(--spacing-md)'
                                }}
                            />
                            {!uploading && (
                                <p style={{ color: 'var(--text-secondary)' }}>
                                    Click or drag another image to replace
                                </p>
                            )}
                        </div>
                    ) : (
                        <>
                            <div className="upload-icon">📸</div>
                            <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>
                                Drag & Drop Image Here
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-md)' }}>
                                or click to browse
                            </p>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                Supported formats: JPG, JPEG, PNG (Max 16MB)
                            </p>
                        </>
                    )}
                </div>

                {uploading && (
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                        <div className="flex justify-between mb-1">
                            <span style={{ color: 'var(--text-secondary)' }}>
                                {progress < 100 ? 'Uploading...' : 'Processing...'}
                            </span>
                            <span style={{ color: 'var(--primary)' }}>{progress}%</span>
                        </div>
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                        </div>
                    </div>
                )}

                {error && (
                    <div
                        className="card mt-2"
                        style={{
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderColor: '#ef4444',
                            padding: 'var(--spacing-md)'
                        }}
                    >
                        <p style={{ color: '#ef4444', margin: 0 }}>❌ {error}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UploadZone;
