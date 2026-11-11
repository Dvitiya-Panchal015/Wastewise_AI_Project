import React, { useEffect, useState } from 'react';
import { fetchInventoryData } from '../../lib/api';
import { InventoryItem } from '../../features/inventory/types';
import './InventoryTable.css';

const InventoryTable: React.FC = () => {
    const [inventory, setInventory] = useState<InventoryItem[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchTerm, setSearchTerm] = useState<string>('');

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const data = await fetchInventoryData();
                setInventory(data);
            } catch (error) {
                console.error('Error fetching inventory data:', error);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const filteredInventory = inventory.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="inventory-table">
            <input
                type="text"
                placeholder="Search inventory..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
            />
            {loading ? (
                <div className="loading-indicator">Loading...</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Quantity</th>
                            <th>Location</th>
                            <th>Expiry Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredInventory.map(item => (
                            <tr key={item.id}>
                                <td>{item.name}</td>
                                <td>{item.quantity}</td>
                                <td>{item.location}</td>
                                <td>{item.expiryDate}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default InventoryTable;