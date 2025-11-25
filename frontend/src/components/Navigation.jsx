import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="navbar">
            <div className="container navbar-content">
                <div className="navbar-brand">
                    🚦 Traffic Violation Detection
                </div>
                <ul className="navbar-nav">
                    <li>
                        <Link
                            to="/"
                            className={`nav-link ${isActive('/') ? 'active' : ''}`}
                        >
                            📊 Dashboard
                        </Link>
                    </li>
                    <li>
                        <Link
                            to="/upload"
                            className={`nav-link ${isActive('/upload') ? 'active' : ''}`}
                        >
                            📤 Upload
                        </Link>
                    </li>
                    <li>
                        <Link
                            to="/history"
                            className={`nav-link ${isActive('/history') ? 'active' : ''}`}
                        >
                            📋 History
                        </Link>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navigation;
