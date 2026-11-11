import React from 'react';

interface StatsCardProps {
    title: string;
    value: number | string;
    description: string;
    icon: React.ReactNode;
    color?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, description, icon, color }) => {
    return (
        <div className={`bg-white shadow-md rounded-lg p-4 flex items-center ${color}`}>
            <div className="flex-shrink-0">
                {icon}
            </div>
            <div className="ml-4">
                <h2 className="text-xl font-semibold">{title}</h2>
                <p className="text-2xl font-bold">{value}</p>
                <p className="text-gray-600">{description}</p>
            </div>
        </div>
    );
};

export default StatsCard;