import React, { useState, useEffect } from 'react';
import { getStatistics } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStatistics();
        // Refresh every 30 seconds
        const interval = setInterval(loadStatistics, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadStatistics = async () => {
        try {
            const response = await getStatistics();
            setStats(response.data);
        } catch (error) {
            console.error('Error loading statistics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="card-body text-center loading">
                    <p>Loading statistics...</p>
                </div>
            </div>
        );
    }

    if (!stats) {
        return (
            <div className="card">
                <div className="card-body text-center">
                    <p style={{ color: 'var(--text-secondary)' }}>
                        No statistics available yet.
                    </p>
                </div>
            </div>
        );
    }

    const chartData = [
        { name: 'License Plates', value: stats.license_plates || 0 },
        { name: 'Helmet Violations', value: stats.helmet_violations || 0 },
        { name: 'Triple Riding', value: stats.triple_riding_violations || 0 },
        { name: 'Red Light Violations', value: stats.red_light_violations || 0 },
    ];

    return (
        <div>
            {/* Summary Cards */}
            <div className="grid grid-4 mb-4">
                <div className="stat-card" style={{ background: 'var(--gradient-primary)' }}>
                    <div className="stat-value">{stats.total_violations || 0}</div>
                    <div className="stat-label">Total Violations</div>
                </div>
                <div className="stat-card" style={{ background: 'var(--gradient-success)' }}>
                    <div className="stat-value">{stats.license_plates || 0}</div>
                    <div className="stat-label">License Plates</div>
                </div>
                <div className="stat-card" style={{ background: 'var(--gradient-secondary)' }}>
                    <div className="stat-value">{stats.helmet_violations || 0}</div>
                    <div className="stat-label">Helmet Violations</div>
                </div>
                <div className="stat-card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                    <div className="stat-value">{stats.triple_riding_violations || 0}</div>
                    <div className="stat-label">Triple Riding</div>
                </div>
            </div>

            <div className="grid grid-4 mb-4">
                <div className="stat-card" style={{ background: 'var(--gradient-dark)' }}>
                    <div className="stat-value">{stats.red_light_violations || 0}</div>
                    <div className="stat-label">Red Light Violations</div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-2 gap-4 mb-4">
                <div className="card">
                    <div className="card-header">Violation Distribution</div>
                    <div className="card-body">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                                <YAxis stroke="var(--text-secondary)" />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--bg-tertiary)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: 'var(--radius-sm)',
                                        color: 'var(--text-primary)'
                                    }}
                                />
                                <Bar dataKey="value" fill="url(#colorGradient)" radius={[8, 8, 0, 0]} />
                                <defs>
                                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#667eea" />
                                        <stop offset="100%" stopColor="#764ba2" />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">Recent Activity</div>
                    <div className="card-body">
                        {stats.recent_violations && stats.recent_violations.length > 0 ? (
                            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                                {stats.recent_violations.map((violation, idx) => (
                                    <div
                                        key={violation._id}
                                        className="glass-hover"
                                        style={{
                                            padding: 'var(--spacing-md)',
                                            marginBottom: 'var(--spacing-sm)',
                                            borderRadius: 'var(--radius-md)'
                                        }}
                                    >
                                        <div className="flex justify-between items-center">
                                            <div>
                                                <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                                                    Violation #{idx + 1}
                                                </p>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                                    {new Date(violation.timestamp).toLocaleString()}
                                                </p>
                                            </div>
                                            <span className={`badge badge-${violation.status === 'processed' ? 'success' : 'warning'
                                                }`}>
                                                {violation.status}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center" style={{ padding: 'var(--spacing-xl)' }}>
                                <p style={{ color: 'var(--text-secondary)' }}>
                                    No recent activity
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* System Status */}
            <div className="card">
                <div className="card-header">System Status</div>
                <div className="card-body">
                    <div className="grid grid-3 gap-3">
                        <div className="flex items-center gap-3">
                            <div
                                style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '50%',
                                    background: '#10b981'
                                }}
                            ></div>
                            <div>
                                <p style={{ fontWeight: 600 }}>API Server</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    Online
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div
                                style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '50%',
                                    background: '#10b981'
                                }}
                            ></div>
                            <div>
                                <p style={{ fontWeight: 600 }}>Database</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    Connected
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div
                                style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '50%',
                                    background: '#10b981'
                                }}
                            ></div>
                            <div>
                                <p style={{ fontWeight: 600 }}>AI Models</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    Ready
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
