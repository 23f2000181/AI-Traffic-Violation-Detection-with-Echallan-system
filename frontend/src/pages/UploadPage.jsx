import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import ResultsViewer from '../components/ResultsViewer';

const UploadPage = () => {
    const [results, setResults] = useState(null);

    const handleUploadComplete = (data) => {
        console.log('Upload complete:', data);
        setResults(data.results);
    };

    return (
        <div className="container" style={{ paddingTop: 'var(--spacing-lg)', paddingBottom: 'var(--spacing-xl)' }}>
            <h1 style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
                Upload Image for Detection
            </h1>

            <UploadZone onUploadComplete={handleUploadComplete} />

            {results && <ResultsViewer results={results} />}
        </div>
    );
};

export default UploadPage;
