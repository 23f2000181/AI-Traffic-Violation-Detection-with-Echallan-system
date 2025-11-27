import React, { useState, useEffect } from 'react';
import { getAllChallans, getChallanStatistics, updateChallanStatus, resendNotification } from '../services/api';

const EchallanPage = () => {
    const [challans, setChallans] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [statusFilter, setStatusFilter] = useState('');
    const [vehicleFilter, setVehicleFilter] = useState('');
    const [selectedChallan, setSelectedChallan] = useState(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        loadData();
    }, [page, statusFilter, vehicleFilter]);

    const loadData = async () => {
        try {
            setLoading(true);

            // Load statistics
            const statsResponse = await getChallanStatistics();
            setStatistics(statsResponse.data);

            // Load challans with filters
            const filters = {};
            if (statusFilter) filters.status = statusFilter;
            if (vehicleFilter) filters.vehicle_no = vehicleFilter;

            const challansResponse = await getAllChallans(page, 20, filters);
            setChallans(challansResponse.data.challans);
            setTotalPages(challansResponse.data.total_pages);
        } catch (error) {
            console.error('Error loading e-challan data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (challanNo, newStatus) => {
        try {
            await updateChallanStatus(challanNo, newStatus);
            alert(`Challan status updated to ${newStatus}`);
            loadData();
        } catch (error) {
            console.error('Error updating status:', error);
            alert('Failed to update status');
        }
    };

    const handleResendNotification = async (challanNo) => {
        try {
            await resendNotification(challanNo, ['sms']);
            alert('Notification sent successfully');
        } catch (error) {
            console.error('Error sending notification:', error);
            alert('Failed to send notification');
        }
    };

    const viewChallanDetails = (challan) => {
        setSelectedChallan(challan);
        setShowModal(true);
    };

    if (loading && !statistics) {
        return (
            <div className="container" style={{ paddingTop: 'var(--spacing-lg)' }}>
                <div className="card">
                    <div className="card-body text-center loading">
                        <p>Loading e-challans...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container" style={{ paddingTop: 'var(--spacing-lg)', paddingBottom: 'var(--spacing-xl)' }}>
            <h1 style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
                📄 E-Challan Management
            </h1>

            {/* Statistics Cards */}
            {statistics && (
                <div className="grid grid-4 mb-4">
                    <div className="stat-card" style={{ background: 'var(--gradient-primary)' }}>
                        <div className="stat-value">{statistics.total_challans || 0}</div>
                        <div className="stat-label">Total Challans</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-success)' }}>
                        <div className="stat-value">{statistics.paid || 0}</div>
                        <div className="stat-label">Paid</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-secondary)' }}>
                        <div className="stat-value">{statistics.pending || 0}</div>
                        <div className="stat-label">Pending</div>
                    </div>
                    <div className="stat-card" style={{ background: 'var(--gradient-dark)' }}>
                        <div className="stat-value">₹{statistics.total_penalties || 0}</div>
                        <div className="stat-label">Total Penalties</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="card mb-4">
                <div className="card-body">
                    <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                        <div style={{ flex: '1 1 200px' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                                Status
                            </label>
                            <select
                                value={statusFilter}
                                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    borderRadius: 'var(--radius-md)',
                                    border: '1px solid var(--border-color)',
                                    background: 'var(--bg-tertiary)',
                                    color: 'var(--text-primary)'
                                }}
                            >
                                <option value="">All Status</option>
                                <option value="issued">Issued</option>
                                <option value="paid">Paid</option>
                                <option value="pending">Pending</option>
                            </select>
                        </div>
                        <div style={{ flex: '1 1 200px' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                                Vehicle Number
                            </label>
                            <input
                                type="text"
                                placeholder="Search by vehicle number"
                                value={vehicleFilter}
                                onChange={(e) => { setVehicleFilter(e.target.value); setPage(1); }}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    borderRadius: 'var(--radius-md)',
                                    border: '1px solid var(--border-color)',
                                    background: 'var(--bg-tertiary)',
                                    color: 'var(--text-primary)'
                                }}
                            />
                        </div>
                        <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'flex-end' }}>
                            <button
                                onClick={() => { setStatusFilter(''); setVehicleFilter(''); setPage(1); }}
                                className="btn btn-secondary"
                            >
                                Clear Filters
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Challans Table */}
            <div className="card">
                <div className="card-header">E-Challans</div>
                <div className="card-body">
                    {loading ? (
                        <div className="text-center loading">
                            <p>Loading...</p>
                        </div>
                    ) : challans.length === 0 ? (
                        <div className="text-center" style={{ padding: 'var(--spacing-xl)' }}>
                            <p style={{ color: 'var(--text-secondary)' }}>No challans found</p>
                        </div>
                    ) : (
                        <>
                            <div className="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Challan No</th>
                                            <th>Vehicle No</th>
                                            <th>Owner</th>
                                            <th>Violations</th>
                                            <th>Penalty</th>
                                            <th>Status</th>
                                            <th>Issued Date</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {challans.map((challan) => (
                                            <tr key={challan._id}>
                                                <td style={{ fontWeight: 600 }}>{challan.challan_no}</td>
                                                <td>{challan.vehicle_no}</td>
                                                <td>{challan.owner_name}</td>
                                                <td>
                                                    {challan.violations.map(v => v.type.replace('_', ' ')).join(', ')}
                                                </td>
                                                <td style={{ fontWeight: 600, color: 'var(--accent)' }}>
                                                    ₹{challan.total_penalty}
                                                </td>
                                                <td>
                                                    <span className={`badge badge-${challan.status === 'paid' ? 'success' :
                                                            challan.status === 'issued' ? 'warning' : 'danger'
                                                        }`}>
                                                        {challan.status}
                                                    </span>
                                                </td>
                                                <td style={{ fontSize: '0.875rem' }}>
                                                    {new Date(challan.issued_at).toLocaleDateString()}
                                                </td>
                                                <td>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => viewChallanDetails(challan)}
                                                            className="btn btn-secondary"
                                                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                                        >
                                                            View
                                                        </button>
                                                        {challan.status !== 'paid' && (
                                                            <button
                                                                onClick={() => handleStatusUpdate(challan.challan_no, 'paid')}
                                                                className="btn btn-primary"
                                                                style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                                            >
                                                                Mark Paid
                                                            </button>
                                                        )}
                                                        <button
                                                            onClick={() => handleResendNotification(challan.challan_no)}
                                                            className="btn btn-secondary"
                                                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                                        >
                                                            📱 Resend
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
                                        onClick={() => setPage(p => Math.max(1, p - 1))}
                                        disabled={page === 1}
                                        className="btn btn-secondary"
                                    >
                                        Previous
                                    </button>
                                    <span style={{ color: 'var(--text-secondary)' }}>
                                        Page {page} of {totalPages}
                                    </span>
                                    <button
                                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                        disabled={page === totalPages}
                                        className="btn btn-secondary"
                                    >
                                        Next
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Challan Details Modal */}
            {showModal && selectedChallan && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2 style={{ marginBottom: 'var(--spacing-lg)' }}>
                            Challan Details
                        </h2>

                        <div className="grid grid-2 gap-3 mb-4">
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Challan Number</p>
                                <p style={{ fontWeight: 600 }}>{selectedChallan.challan_no}</p>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Status</p>
                                <span className={`badge badge-${selectedChallan.status === 'paid' ? 'success' :
                                        selectedChallan.status === 'issued' ? 'warning' : 'danger'
                                    }`}>
                                    {selectedChallan.status}
                                </span>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Vehicle Number</p>
                                <p style={{ fontWeight: 600 }}>{selectedChallan.vehicle_no}</p>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Owner Name</p>
                                <p style={{ fontWeight: 600 }}>{selectedChallan.owner_name}</p>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Issued Date</p>
                                <p>{new Date(selectedChallan.issued_at).toLocaleString()}</p>
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Due Date</p>
                                <p>{new Date(selectedChallan.due_date).toLocaleDateString()}</p>
                            </div>
                        </div>

                        <div className="mb-4">
                            <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Violations</h3>
                            <div className="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Type</th>
                                            <th>Penalty</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {selectedChallan.violations.map((v, idx) => (
                                            <tr key={idx}>
                                                <td>{v.type.replace('_', ' ').toUpperCase()}</td>
                                                <td style={{ fontWeight: 600 }}>₹{v.penalty}</td>
                                                <td>
                                                    <span className="badge badge-success">
                                                        {(v.confidence * 100).toFixed(1)}%
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="mb-4">
                            <h3 style={{ color: 'var(--accent)', fontSize: '1.5rem' }}>
                                Total Penalty: ₹{selectedChallan.total_penalty}
                            </h3>
                        </div>

                        <button
                            onClick={() => setShowModal(false)}
                            className="btn btn-primary"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EchallanPage;
