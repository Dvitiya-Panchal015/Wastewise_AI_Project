import React, { useEffect, useState } from 'react';
import { fetchRecommendations } from '../../lib/api';
import { Button } from '../common/Button';
import './QuickActions.css';

const QuickActions = () => {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getRecommendations = async () => {
            try {
                const data = await fetchRecommendations();
                setRecommendations(data);
            } catch (err) {
                setError('Failed to fetch recommendations');
            } finally {
                setLoading(false);
            }
        };

        getRecommendations();
    }, []);

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    return (
        <div className="quick-actions">
            <h2>Recommended Actions</h2>
            <ul>
                {recommendations.map((action, index) => (
                    <li key={index} className="action-item">
                        <span>{action.description}</span>
                        <Button onClick={() => action.execute()}>Execute</Button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default QuickActions;