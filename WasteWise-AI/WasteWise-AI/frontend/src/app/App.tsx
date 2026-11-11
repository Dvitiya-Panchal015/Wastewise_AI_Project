import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { Topbar } from '../components/layout/Topbar';
import { DashboardShell } from '../components/layout/DashboardShell';
import { Routes } from './routes';
import './App.css';

const App: React.FC = () => {
    return (
        <Router>
            <div className="app-container">
                <Sidebar />
                <div className="main-content">
                    <Topbar />
                    <DashboardShell>
                        <Routes />
                    </DashboardShell>
                </div>
            </div>
        </Router>
    );
};

export default App;