import React from 'react';
import ViolationHistory from '../components/ViolationHistory';

const HistoryPage = () => {
    return (
        <div className="container" style={{ paddingTop: 'var(--spacing-lg)', paddingBottom: 'var(--spacing-xl)' }}>
            <h1 style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
                Violation History
            </h1>
            <ViolationHistory />
        </div>
    );
};

export default HistoryPage;
