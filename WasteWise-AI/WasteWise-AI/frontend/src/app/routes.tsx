import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import InventoryPage from '../features/inventory/InventoryPage';
import AnalyticsPage from '../features/analytics/AnalyticsPage';
import SettingsPage from '../features/settings/SettingsPage';

const Routes = () => {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={InventoryPage} />
                <Route path="/analytics" component={AnalyticsPage} />
                <Route path="/settings" component={SettingsPage} />
            </Switch>
        </Router>
    );
};

export default Routes;