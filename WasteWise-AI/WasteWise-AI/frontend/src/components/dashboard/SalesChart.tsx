import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { fetchSalesData } from '../../lib/api';

const SalesChart = () => {
    const [salesData, setSalesData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getSalesData = async () => {
            try {
                const data = await fetchSalesData();
                setSalesData(data);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        getSalesData();
    }, []);

    const chartData = {
        labels: salesData.map(item => item.date),
        datasets: [
            {
                label: 'Sales',
                data: salesData.map(item => item.amount),
                fill: false,
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: 'rgba(75,192,192,1)',
            },
        ],
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error loading sales data</div>;

    return (
        <div>
            <h2>Sales Chart</h2>
            <Line data={chartData} />
        </div>
    );
};

export default SalesChart;