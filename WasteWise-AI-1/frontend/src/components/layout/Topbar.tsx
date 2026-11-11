import React from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '../../common/Button';

const Topbar = () => {
    const location = useLocation();
    const currentPath = location.pathname.split('/').filter(Boolean).pop();
    const lastUpdated = new Date().toLocaleString();

    return (
        <div className="topbar">
            <div className="topbar-content">
                <div className="breadcrumb">
                    <span>Home</span> / <span>{currentPath}</span>
                </div>
                <div className="welcome-message">
                    <h2>Welcome to WasteWise AI</h2>
                </div>
                <div className="topbar-actions">
                    <input type="text" placeholder="Search..." className="search-field" />
                    <Button label="Refresh" onClick={() => window.location.reload()} />
                    <span className="last-updated">Last updated: {lastUpdated}</span>
                </div>
            </div>
        </div>
    );
};

export default Topbar;