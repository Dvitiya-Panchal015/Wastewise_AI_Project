import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../app/store';
import { AnalyticsOverview } from './AnalyticsOverview';
import { AnalyticsTrends } from './AnalyticsTrends';
import { AnalyticsInsights } from './AnalyticsInsights';
import './AnalyticsPage.css';

const AnalyticsPage: React.FC = () => {
    const analyticsData = useSelector((state: RootState) => state.analytics.data);
    const loading = useSelector((state: RootState) => state.analytics.loading);

    return (
        <div className="analytics-page">
            <h1>Analytics Dashboard</h1>
            {loading ? (
                <div>Loading...</div>
            ) : (
                <>
                    <AnalyticsOverview data={analyticsData.overview} />
                    <AnalyticsTrends data={analyticsData.trends} />
                    <AnalyticsInsights data={analyticsData.insights} />
                </>
            )}
        </div>
    );
};

export default AnalyticsPage;