import React from 'react';
import Dashboard from '../components/Dashboard';

const DashboardPage = () => {
    return (
        <div className="container" style={{ paddingTop: 'var(--spacing-lg)', paddingBottom: 'var(--spacing-xl)' }}>
            <h1 style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
                Dashboard
            </h1>
            <Dashboard />
        </div>
    );
};

export default DashboardPage;
