import React, { useEffect, useState } from 'react';
import { fetchAlerts } from '../../lib/api';
import { Alert } from '../../features/inventory/types';
import './AlertsPanel.css';

const AlertsPanel: React.FC = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getAlerts = async () => {
            try {
                const data = await fetchAlerts();
                setAlerts(data.sort((a, b) => b.riskLevel - a.riskLevel)); // Sort by highest risk first
            } catch (err) {
                setError('Failed to fetch alerts');
            } finally {
                setLoading(false);
            }
        };

        getAlerts();
    }, []);

    if (loading) {
        return <div className="loading">Loading alerts...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    return (
        <div className="alerts-panel">
            <h2>Expiry Risk Alerts</h2>
            <ul>
                {alerts.map(alert => (
                    <li key={alert.id} className={`alert-item risk-${alert.riskLevel}`}>
                        <span>{alert.message}</span>
                        <span className="alert-date">{new Date(alert.date).toLocaleDateString()}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default AlertsPanel;