import React from 'react';

interface CardProps {
    title: string;
    content: React.ReactNode;
    footer?: React.ReactNode;
    className?: string;
}

const Card: React.FC<CardProps> = ({ title, content, footer, className }) => {
    return (
        <div className={`bg-white shadow-md rounded-lg p-4 ${className}`}>
            <h2 className="text-lg font-semibold mb-2">{title}</h2>
            <div className="content mb-4">{content}</div>
            {footer && <div className="footer">{footer}</div>}
        </div>
    );
};

export default Card;