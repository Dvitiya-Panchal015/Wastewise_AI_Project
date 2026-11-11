import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInventory } from './inventorySlice';
import InventoryTable from '../../components/dashboard/InventoryTable';
import StatsCard from '../../components/dashboard/StatsCard';
import QuickActions from '../../components/dashboard/QuickActions';
import AlertsPanel from '../../components/dashboard/AlertsPanel';
import SalesChart from '../../components/dashboard/SalesChart';
import './InventoryPage.css';

const InventoryPage = () => {
    const dispatch = useDispatch();
    const inventory = useSelector((state) => state.inventory.items);
    const loading = useSelector((state) => state.inventory.loading);
    const error = useSelector((state) => state.inventory.error);

    useEffect(() => {
        dispatch(fetchInventory());
    }, [dispatch]);

    return (
        <div className="inventory-page">
            <h1>Inventory Management</h1>
            {loading && <p>Loading...</p>}
            {error && <p>Error loading inventory: {error}</p>}
            <StatsCard inventory={inventory} />
            <SalesChart inventory={inventory} />
            <AlertsPanel inventory={inventory} />
            <QuickActions />
            <InventoryTable inventory={inventory} />
        </div>
    );
};

export default InventoryPage;