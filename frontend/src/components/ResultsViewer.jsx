import React from 'react';
import { getImageUrl } from '../services/api';

const ResultsViewer = ({ results }) => {
    if (!results) {
        return null;
    }

    const {
        license_plates = [],
        helmet_violations = [],
        triple_riding_violations = [],
        red_light_violations = [],
        processing_time,
        image_path,
        processed_image_path
    } = results;

    const totalViolations =
        license_plates.length + helmet_violations.length + triple_riding_violations.length + red_light_violations.length;

    const downloadResults = () => {
        const dataStr = JSON.stringify(results, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `detection_results_${Date.now()}.json`;
        link.click();
    };

    return (
        <div className="card mt-4">
            <div className="card-header flex justify-between items-center">
                <span>Detection Results</span>
                <button className="btn btn-secondary" onClick={downloadResults}>
                    💾 Download JSON
                </button>
            </div>
            <div className="card-body">
                {/* Summary */}
                <div className="grid grid-4 mb-4">
                    <div className="stat-card" style={{ background: 'var(--gradient-primary)' }}>
                        <div className="stat-value">{totalViolations}</div>
                        <div className="stat-label">Total Detections</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-success)' }}>
                        <div className="stat-value">{license_plates.length}</div>
                        <div className="stat-label">License Plates</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-secondary)' }}>
                        <div className="stat-value">{helmet_violations.length}</div>
                        <div className="stat-label">Helmet Violations</div>
                    </div>
                    <div className="stat-card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                        <div className="stat-value">{triple_riding_violations.length}</div>
                        <div className="stat-label">Triple Riding</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-dark)' }}>
                        <div className="stat-value">{red_light_violations.length}</div>
                        <div className="stat-label">Red Light Violations</div>
                    </div>
                </div>

                {/* Processing Time */}
                <div className="mb-4">
                    <span className="badge badge-success">
                        ⚡ Processed in {processing_time?.toFixed(2)}s
                    </span>
                </div>

                {/* Image Comparison */}
                <div className="grid grid-2 mb-4">
                    <div>
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            Original Image
                        </h4>
                        <img
                            src={getImageUrl(image_path)}
                            alt="Original"
                            style={{
                                width: '100%',
                                borderRadius: 'var(--radius-md)',
                                border: '1px solid var(--border-color)'
                            }}
                        />
                    </div>
                    <div>
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            Processed Image
                        </h4>
                        {processed_image_path ? (
                            <img
                                src={getImageUrl(processed_image_path)}
                                alt="Processed"
                                style={{
                                    width: '100%',
                                    borderRadius: 'var(--radius-md)',
                                    border: '1px solid var(--border-color)'
                                }}
                            />
                        ) : (
                            <div
                                style={{
                                    width: '100%',
                                    aspectRatio: '16/9',
                                    background: 'var(--bg-tertiary)',
                                    borderRadius: 'var(--radius-md)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'var(--text-muted)'
                                }}
                            >
                                No processed image available
                            </div>
                        )}
                    </div>
                </div>

                {/* Detection Details */}
                {license_plates.length > 0 && (
                    <div className="mb-4">
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            🚗 License Plates Detected
                        </h4>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Plate Text</th>
                                        <th>Confidence</th>
                                        <th>Bounding Box</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {license_plates.map((plate, idx) => (
                                        <tr key={idx}>
                                            <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                                {plate.plate_text}
                                            </td>
                                            <td>
                                                <span className="badge badge-success">
                                                    {(plate.confidence * 100).toFixed(1)}%
                                                </span>
                                            </td>
                                            <td style={{ fontSize: '0.875rem' }}>
                                                {plate.bbox?.join(', ')}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {helmet_violations.length > 0 && (
                    <div className="mb-4">
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            🛵 Helmet Violations
                        </h4>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Confidence</th>
                                        <th>Bounding Box</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {helmet_violations.map((violation, idx) => (
                                        <tr key={idx}>
                                            <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                                {violation.type}
                                            </td>
                                            <td>
                                                <span className="badge badge-warning">
                                                    {(violation.confidence * 100).toFixed(1)}%
                                                </span>
                                            </td>
                                            <td style={{ fontSize: '0.875rem' }}>
                                                {violation.bbox?.join(', ')}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {triple_riding_violations.length > 0 && (
                    <div className="mb-4">
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            🏍️ Triple Riding Violations
                        </h4>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Person Count</th>
                                        <th>Confidence</th>
                                        <th>Motorbike BBox</th>
                                        <th>Timestamp</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {triple_riding_violations.map((violation, idx) => (
                                        <tr key={idx}>
                                            <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                                {violation.person_count} persons
                                            </td>
                                            <td>
                                                <span className="badge badge-danger">
                                                    {(violation.confidence * 100).toFixed(1)}%
                                                </span>
                                            </td>
                                            <td style={{ fontSize: '0.875rem' }}>
                                                {violation.motorbike_bbox?.join(', ')}
                                            </td>
                                            <td style={{ fontSize: '0.875rem' }}>
                                                {new Date(violation.timestamp).toLocaleTimeString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {red_light_violations.length > 0 && (
                    <div className="mb-4">
                        <h4 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--text-primary)' }}>
                            🚦 Red Light Violations
                        </h4>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Vehicle Type</th>
                                        <th>Light State</th>
                                        <th>Confidence</th>
                                        <th>Bounding Box</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {red_light_violations.map((violation, idx) => (
                                        <tr key={idx}>
                                            <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                                {violation.vehicle_type}
                                            </td>
                                            <td>
                                                <span className="badge badge-danger">
                                                    {violation.light_state}
                                                </span>
                                            </td>
                                            <td>
                                                <span className="badge badge-danger">
                                                    {(violation.confidence * 100).toFixed(1)}%
                                                </span>
                                            </td>
                                            <td style={{ fontSize: '0.875rem' }}>
                                                {violation.bbox?.join(', ')}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultsViewer;
