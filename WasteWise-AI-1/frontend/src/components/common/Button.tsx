import React from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'tertiary';
    className?: string;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false, variant = 'primary', className = '' }) => {
    const baseStyles = 'px-4 py-2 rounded focus:outline-none transition duration-200';
    const variantStyles = {
        primary: 'bg-blue-500 text-white hover:bg-blue-600',
        secondary: 'bg-gray-300 text-black hover:bg-gray-400',
        tertiary: 'bg-transparent text-blue-500 border border-blue-500 hover:bg-blue-500 hover:text-white',
    };

    return (
        <button
            className={`${baseStyles} ${variantStyles[variant]} ${className}`}
            onClick={onClick}
            disabled={disabled}
        >
            {label}
        </button>
    );
};

export default Button;