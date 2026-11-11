import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css'; // Assuming you have a CSS file for styling

const Sidebar = () => {
    return (
        <div className="sidebar">
            <div className="sidebar-logo">
                <img src="/path/to/logo.svg" alt="WasteWise AI Logo" />
            </div>
            <nav className="sidebar-nav">
                <ul>
                    <li>
                        <Link to="/dashboard">Dashboard</Link>
                    </li>
                    <li>
                        <Link to="/inventory">Inventory</Link>
                    </li>
                    <li>
                        <Link to="/analytics">Analytics</Link>
                    </li>
                    <li>
                        <Link to="/settings">Settings</Link>
                    </li>
                </ul>
            </nav>
        </div>
    );
};

export default Sidebar;