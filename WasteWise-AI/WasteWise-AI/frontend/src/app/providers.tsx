import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store'; // Assuming you have a store setup

const AppProviders: React.FC = ({ children }) => {
    return (
        <Provider store={store}>
            {children}
        </Provider>
    );
};

export default AppProviders;