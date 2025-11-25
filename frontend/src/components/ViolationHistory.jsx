import React, { useState, useEffect } from 'react';
import { getViolations, deleteViolation } from '../services/api';
import { format } from 'date-fns';

const ViolationHistory = () => {
    const [violations, setViolations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedViolation, setSelectedViolation] = useState(null);

    useEffect(() => {
        loadViolations();
    }, [page]);

    const loadViolations = async () => {
        try {
            setLoading(true);
            const response = await getViolations(page, 50);
            setViolations(response.data.violations);
            setTotalPages(response.data.total_pages);
        } catch (error) {
            console.error('Error loading violations:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Are you sure you want to delete this violation?')) {
            return;
        }

        try {
            await deleteViolation(id);
            loadViolations();
        } catch (error) {
            console.error('Error deleting violation:', error);
            alert('Failed to delete violation');
        }
    };

    const formatDate = (dateString) => {
        try {
            return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
        } catch {
            return dateString;
        }
    };

    const getViolationCount = (violation) => {
        const results = violation.detection_results || {};
        return (
            (results.license_plates?.length || 0) +
            (results.helmet_violations?.length || 0) +
            (results.red_light_violations?.length || 0)
        );
    };

    if (loading && violations.length === 0) {
        return (
            <div className="card">
                <div className="card-body text-center loading">
                    <p>Loading violations...</p>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="card">
                <div className="card-header flex justify-between items-center">
                    <span>Violation History</span>
                    <span className="badge badge-success">
                        {violations.length} records
                    </span>
                </div>
                <div className="card-body">
                    {violations.length === 0 ? (
                        <div className="text-center" style={{ padding: 'var(--spacing-xl)' }}>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                No violations found. Upload an image to get started.
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Detections</th>
                                            <th>Status</th>
                                            <th>Processing Time</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {violations.map((violation) => (
                                            <tr key={violation._id}>
                                                <td>{formatDate(violation.timestamp)}</td>
                                                <td>
                                                    <span className="badge badge-success">
                                                        {getViolationCount(violation)} detections
                                                    </span>
                                                </td>
                                                <td>
                                                    <span className={`badge badge-${violation.status === 'processed' ? 'success' : 'warning'
                                                        }`}>
                                                        {violation.status}
                                                    </span>
                                                </td>
                                                <td>{violation.processing_time?.toFixed(2)}s</td>
                                                <td>
                                                    <div className="flex gap-2">
                                                        <button
                                                            className="btn btn-secondary"
                                                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                                            onClick={() => setSelectedViolation(violation)}
                                                        >
                                                            👁️ View
                                                        </button>
                                                        <button
                                                            className="btn btn-danger"
                                                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                                            onClick={() => handleDelete(violation._id)}
                                                        >
                                                            🗑️ Delete
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="flex justify-between items-center mt-4">
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => setPage(page - 1)}
                                        disabled={page === 1}
                                    >
                                        ← Previous
                                    </button>
                                    <span style={{ color: 'var(--text-secondary)' }}>
                                        Page {page} of {totalPages}
                                    </span>
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => setPage(page + 1)}
                                        disabled={page === totalPages}
                                    >
                                        Next →
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Violation Detail Modal */}
            {selectedViolation && (
                <div className="modal-overlay" onClick={() => setSelectedViolation(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="flex justify-between items-center mb-4">
                            <h2 style={{ margin: 0 }}>Violation Details</h2>
                            <button
                                className="btn btn-secondary"
                                onClick={() => setSelectedViolation(null)}
                            >
                                ✕ Close
                            </button>
                        </div>

                        <div className="grid grid-2 gap-4 mb-4">
                            <div>
                                <p style={{ color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                    Date & Time
                                </p>
                                <p style={{ fontWeight: 600 }}>
                                    {formatDate(selectedViolation.timestamp)}
                                </p>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                    Processing Time
                                </p>
                                <p style={{ fontWeight: 600 }}>
                                    {selectedViolation.processing_time?.toFixed(2)}s
                                </p>
                            </div>
                        </div>

                        <div className="mb-4">
                            <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Detection Summary</h4>
                            <div className="grid grid-3 gap-3">
                                <div className="card">
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                        License Plates
                                    </p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                        {selectedViolation.detection_results?.license_plates?.length || 0}
                                    </p>
                                </div>
                                <div className="card">
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                        Helmet Violations
                                    </p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                        {selectedViolation.detection_results?.helmet_violations?.length || 0}
                                    </p>
                                </div>
                                <div className="card">
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                        Red Light Violations
                                    </p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                        {selectedViolation.detection_results?.red_light_violations?.length || 0}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Full Details</h4>
                            <pre
                                style={{
                                    background: 'var(--bg-tertiary)',
                                    padding: 'var(--spacing-md)',
                                    borderRadius: 'var(--radius-md)',
                                    overflow: 'auto',
                                    maxHeight: '300px',
                                    fontSize: '0.875rem'
                                }}
                            >
                                {JSON.stringify(selectedViolation, null, 2)}
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ViolationHistory;
