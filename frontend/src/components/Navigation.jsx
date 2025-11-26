import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
    const location = useLocation();
    const [theme, setTheme] = useState(() => {
        // Get theme from localStorage or default to 'dark'
        return localStorage.getItem('theme') || 'dark';
    });

    useEffect(() => {
        // Apply theme to document
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
    };

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
                    <li>
                        <button
                            onClick={toggleTheme}
                            className="nav-link"
                            style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1.2rem'
                            }}
                            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                        >
                            {theme === 'dark' ? '☀️' : '🌙'}
                        </button>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navigation;
