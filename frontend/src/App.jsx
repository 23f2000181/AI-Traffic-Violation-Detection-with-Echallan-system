import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import HistoryPage from './pages/HistoryPage';
import EchallanPage from './pages/EchallanPage';
import './index.css';

function App() {
    return (
        <Router>
            <div className="app">
                <Navigation />
                <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/upload" element={<UploadPage />} />
                    <Route path="/history" element={<HistoryPage />} />
                    <Route path="/echallans" element={<EchallanPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
