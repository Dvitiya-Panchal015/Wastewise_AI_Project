# WasteWise AI Frontend

Welcome to the WasteWise AI frontend project! This project is designed to provide a professional inventory management dashboard that integrates various functionalities for efficient waste management.

## Project Structure

The project is organized as follows:

```
WasteWise-AI
└── frontend
    ├── public
    │   └── favicon.svg
    ├── src
    │   ├── app
    │   │   ├── App.tsx
    │   │   ├── routes.tsx
    │   │   └── providers.tsx
    │   ├── components
    │   │   ├── layout
    │   │   │   ├── Sidebar.tsx
    │   │   │   ├── Topbar.tsx
    │   │   │   └── DashboardShell.tsx
    │   │   ├── dashboard
    │   │   │   ├── StatsCard.tsx
    │   │   │   ├── InventoryTable.tsx
    │   │   │   ├── SalesChart.tsx
    │   │   │   ├── AlertsPanel.tsx
    │   │   │   └── QuickActions.tsx
    │   │   └── common
    │   │       ├── Button.tsx
    │   │       ├── Card.tsx
    │   │       └── Badge.tsx
    │   ├── features
    │   │   ├── inventory
    │   │   │   ├── InventoryPage.tsx
    │   │   │   ├── inventorySlice.ts
    │   │   │   └── types.ts
    │   │   ├── analytics
    │   │   │   ├── AnalyticsPage.tsx
    │   │   │   └── analyticsSlice.ts
    │   │   └── settings
    │   │       └── SettingsPage.tsx
    │   ├── hooks
    │   │   └── useResponsiveLayout.ts
    │   ├── lib
    │   │   ├── format.ts
    │   │   ├── constants.ts
    │   │   └── api.ts
    │   ├── styles
    │   │   ├── globals.css
    │   │   └── theme.css
    │   ├── main.tsx
    │   └── vite-env.d.ts
    ├── .eslintrc.json
    ├── .gitignore
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    └── README.md
```

## Getting Started

To get started with the WasteWise AI frontend, follow these steps:

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd WasteWise-AI/frontend
   ```

2. **Install dependencies**:
   ```
   npm install
   ```

3. **Run the development server**:
   ```
   npm run dev
   ```

4. **Build the project**:
   To build the project for production, run:
   ```
   npm run build
   ```

## Features

- **Dashboard Overview**: A comprehensive dashboard that provides insights into inventory management.
- **Responsive Design**: The application is designed to be responsive and user-friendly across devices.
- **Real-time Data**: Integrates with APIs to fetch and display real-time inventory data, sales forecasts, and alerts.
- **User-Friendly Navigation**: The sidebar and topbar components provide easy navigation throughout the application.

## Important Files

- `src/app/App.tsx`: Main application component with routing.
- `src/components/layout/Sidebar.tsx`: Sidebar component with navigation links.
- `src/components/layout/Topbar.tsx`: Top header component with search and user info.
- `src/components/dashboard/StatsCard.tsx`: Displays summary statistics.
- `src/lib/api.ts`: Handles API calls and data fetching.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.