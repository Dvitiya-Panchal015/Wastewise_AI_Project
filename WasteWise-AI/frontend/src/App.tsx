
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import AuthPage from "./AuthPage";

import {
  AlertTriangle,
  Boxes,
  CheckCircle2,
  LayoutDashboard,
  Leaf,
  Package,
  RefreshCw,
  Recycle,
  Search,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

/* =========================================
   TYPES
========================================= */

type RowData = Record<string, unknown>;

type ApiResponse =
  | Record<string, unknown>
  | RowData[];

type TabId =
  | "overview"
  | "inventory"
  | "forecast"
  | "risk"
  | "recommendations"
  | "reports"
  | "metrics";

type RiskRow = RowData & {
  probability: number;
  quantityRemaining: number;
  daysToExpiry: number;
};

type CategoryItem = {
  name: string;
  value: number;
  fill: string;
};

type StockItem = {
  name: string;
  total: number;
  fill: string;
};

type ForecastItem = {
  product: string;
  previous: number;
  predicted: number;
};

/* =========================================
   CONSTANTS
========================================= */

const API_ENDPOINTS = [
  "/api/v1/sales/forecast",
  "/api/v1/risk/expiry",
  "/api/v1/waste/recommendations",
];

const COLORS = [
  "#2d7c5a",
  "#e1b86d",
  "#b8a8ee",
  "#7ca7a0",
  "#d68476",
  "#7d8de9",
];

const NAV_ITEMS: {
  id: TabId;
  label: string;
  icon: ReactNode;
}[] = [
  {
    id: "overview",
    label: "Dashboard",
    icon: <LayoutDashboard size={18} />,
  },
  {
    id: "inventory",
    label: "Inventory",
    icon: <Boxes size={18} />,
  },
  {
    id: "forecast",
    label: "Demand Forecast",
    icon: <TrendingUp size={18} />,
  },
  {
    id: "risk",
    label: "Expiry Risk",
    icon: <ShieldAlert size={18} />,
  },
  {
    id: "recommendations",
    label: "Recommendations",
    icon: <Recycle size={18} />,
  },
  {
    id: "reports",
    label: "Waste Reports",
    icon: <Package size={18} />,
  },
  {
    id: "metrics",
    label: "Model Metrics",
    icon: <CheckCircle2 size={18} />,
  },
];

const TITLES: Record<TabId, string> = {
  overview: "Dashboard",
  inventory: "Inventory",
  forecast: "Demand Forecast",
  risk: "Expiry Risk",
  recommendations: "Recommendations",
  reports: "Waste Reports",
  metrics: "Model Metrics",
};

const DESCRIPTIONS: Record<TabId, string> = {
  overview:
    "Monitor inventory performance and predicted demand.",
  inventory:
    "Manage and monitor your available stock.",
  forecast:
    "Compare previous-day sales with predicted demand.",
  risk:
    "Identify batches requiring expiry-risk review.",
  recommendations:
    "Review suggested actions for reducing potential waste.",
  reports:
    "Review inventory value and remaining-stock summaries.",
  metrics:
    "Review model evaluation information and limitations.",
};

/* =========================================
   HELPER FUNCTIONS
========================================= */

function toNumber(value: unknown): number {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return 0;
  }

  const number = Number(value);

  return Number.isFinite(number) ? number : 0;
}

function getText(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }

  if (typeof value === "number") {
    return value.toLocaleString("en-IN");
  }

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function formatINR(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function getRows(
  response: ApiResponse,
  key: string,
): RowData[] {
  if (Array.isArray(response)) {
    return response;
  }

  const value = response[key];

  return Array.isArray(value)
    ? (value as RowData[])
    : [];
}

function matchesSearch(
  row: RowData,
  search: string,
): boolean {
  const term = search.trim().toLowerCase();

  if (!term) {
    return true;
  }

  return Object.values(row)
    .map(getText)
    .join(" ")
    .toLowerCase()
    .includes(term);
}

function riskBadge(status: string): string {
  const value = status.toLowerCase();

  if (value.includes("expired")) {
    return "badge badge-expired";
  }

  if (value.includes("high")) {
    return "badge badge-high";
  }

  if (value.includes("low")) {
    return "badge badge-low";
  }

  return "badge";
}

/* =========================================
   REUSABLE DATA TABLE
========================================= */

function DataTable({
  title,
  rows,
  icon,
}: {
  title: string;
  rows: RowData[];
  icon: ReactNode;
}) {
  const columns =
    rows.length > 0
      ? Object.keys(rows[0]).slice(0, 6)
      : [];

  return (
    <section className="panel data-panel">
      <div className="panel-heading">
        <div className="panel-title">
          <span className="panel-icon">{icon}</span>

          <div>
            <h2>{title}</h2>
            <p className="muted">
              Records returned by the API
            </p>
          </div>
        </div>

        <span className="record-count">
          {rows.length.toLocaleString("en-IN")} records
        </span>
      </div>

      {rows.length === 0 ? (
        <p className="empty-state">
          No records match your search.
        </p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>
                    {column.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {rows.slice(0, 12).map((row, index) => (
                <tr
                  key={String(
                    row.batch_id ??
                      row.product_id ??
                      index
                  )}
                >
                  {columns.map((column) => (
                    <td key={column}>
                      {getText(row[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="muted table-footnote">
        Showing up to 12 matching records.
      </p>
    </section>
  );
}

/* =========================================
   FORECAST CHART
========================================= */

function ForecastChart({
  data,
  loading,
  date,
}: {
  data: ForecastItem[];
  loading: boolean;
  date: string;
}) {
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div className="panel-title">
          <span className="panel-icon">
            <TrendingUp size={18} />
          </span>

          <div>
            <h2>Sales vs. Predicted Demand</h2>

            <p className="muted">
              Previous-day sales and predicted units
            </p>
          </div>
        </div>

        <span className="chart-tag">Units sold</span>
      </div>

      {data.length > 0 ? (
        <div className="chart-area">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <LineChart
              data={data}
              margin={{
                top: 10,
                right: 10,
                left: -18,
                bottom: 0,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e6eee9"
              />

              <XAxis
                dataKey="product"
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11 }}
              />

              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11 }}
              />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="previous"
                name="Previous-day sales"
                stroke="#a8c5b7"
                strokeWidth={3}
                dot={{ r: 3 }}
              />

              <Line
                type="monotone"
                dataKey="predicted"
                name="Predicted demand"
                stroke="#237e5a"
                strokeWidth={3}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="empty-state">
          {loading
            ? "Loading forecast..."
            : "No forecast data available."}
        </p>
      )}

      {date && (
        <p className="chart-caption">
          Forecast date: {date}
        </p>
      )}
    </section>
  );
}

/* =========================================
   CATEGORY CHART
========================================= */

function CategoryChart({
  data,
  loading,
}: {
  data: CategoryItem[];
  loading: boolean;
}) {
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div className="panel-title">
          <span className="panel-icon">
            <Boxes size={18} />
          </span>

          <div>
            <h2>Inventory by Category</h2>
            <p className="muted">
              Count of returned expiry-risk records
            </p>
          </div>
        </div>
      </div>

      {data.length > 0 ? (
        <>
          <div className="risk-chart-area">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={54}
                  outerRadius={80}
                  paddingAngle={2}
                >
                  {data.map((item) => (
                    <Cell
                      key={item.name}
                      fill={item.fill}
                    />
                  ))}
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="legend-list">
            {data.map((item) => (
              <div
                className="legend-item"
                key={item.name}
              >
                <span
                  className="legend-dot"
                  style={{ background: item.fill }}
                />

                <span>{item.name}</span>

                <strong>
                  {item.value.toLocaleString("en-IN")}
                </strong>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="empty-state">
          {loading
            ? "Loading category data..."
            : "No category data available."}
        </p>
      )}
    </section>
  );
}

/* =========================================
   EXPIRY RISK ALERTS
========================================= */

function RiskAlerts({
  rows,
  loading,
}: {
  rows: RiskRow[];
  loading: boolean;
}) {
  return (
    <section className="panel risk-panel">
      <div className="panel-heading">
        <div className="panel-title">
          <span className="panel-icon">
            <ShieldAlert size={18} />
          </span>

          <div>
            <h2>Expiry-Risk Alerts</h2>
            <p className="muted">
              Expired records first, then highest risk
            </p>
          </div>
        </div>

        <span className="record-count">
          {rows.length.toLocaleString("en-IN")} records
        </span>
      </div>

      {rows.length > 0 ? (
        <div className="risk-list">
          {rows.slice(0, 8).map((row, index) => (
            <div
              className="risk-card"
              key={String(
                row.batch_id ??
                  `${row.product_id}-${index}`
              )}
            >
              <div className="risk-card-top">
                <div>
                  <div className="tiny-label">
                    Batch {getText(row.batch_id)}
                  </div>

                  <strong>
                    Product {getText(row.product_id)}
                  </strong>
                </div>

                <span
                  className={riskBadge(
                    String(
                      row.predicted_risk_status ??
                        "Unknown"
                    )
                  )}
                >
                  {getText(
                    row.predicted_risk_status ??
                      "Unknown"
                  )}
                </span>
              </div>

              <div className="risk-meta">
                <span>{getText(row.category)}</span>

                <span>
                  {getText(row.daysToExpiry)} days to expiry
                </span>
              </div>

              <div className="risk-metrics">
                <div>
                  <small>Remaining quantity</small>
                  <strong>
                    {getText(row.quantityRemaining)}
                  </strong>
                </div>

                <div>
                  <small>High-risk probability</small>
                  <strong>
                    {(row.probability * 100).toFixed(1)}%
                  </strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">
          {loading
            ? "Loading expiry alerts..."
            : "No expiry alerts match your search."}
        </p>
      )}
    </section>
  );
}

/* =========================================
   REMAINING STOCK CHART
========================================= */

function RemainingStockChart({
  data,
  loading,
}: {
  data: StockItem[];
  loading: boolean;
}) {
  return (
    <section className="panel chart-panel bar-panel">
      <div className="panel-heading">
        <div className="panel-title">
          <span className="panel-icon">
            <Recycle size={18} />
          </span>

          <div>
            <h2>Remaining Stock by Category</h2>
            <p className="muted">
              Quantity in recommendation records
            </p>
          </div>
        </div>
      </div>

      {data.length > 0 ? (
        <div className="chart-area">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <BarChart
              data={data}
              layout="vertical"
            >
              <CartesianGrid
                strokeDasharray="3 3"
                horizontal={false}
                stroke="#e6eee9"
              />

              <XAxis
                type="number"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                dataKey="name"
                type="category"
                width={90}
                tickLine={false}
                axisLine={false}
              />

              <Tooltip />

              <Bar
                dataKey="total"
                name="Remaining quantity"
                radius={[0, 8, 8, 0]}
              >
                {data.map((item) => (
                  <Cell
                    key={item.name}
                    fill={item.fill}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="empty-state">
          {loading
            ? "Loading stock summary..."
            : "Remaining-stock data unavailable."}
        </p>
      )}
    </section>
  );
}

/* =========================================
   MAIN APPLICATION
========================================= */

function App() {
  // AUTHENTICATION STATE
  const [authToken, setAuthToken] = useState<string | null>(
    () => sessionStorage.getItem("wastewise_token")
  );

  // LOGIN SUCCESS
  function handleLoginSuccess(token: string) {
    sessionStorage.setItem("wastewise_token", token);
    setAuthToken(token);
  }

  // LOGOUT
  function handleLogout() {
    sessionStorage.removeItem("wastewise_token");
    setAuthToken(null);
  }

  // EXISTING DASHBOARD STATES
  const [salesRows, setSalesRows] = useState<RowData[]>([]);
  const [riskRows, setRiskRows] = useState<RowData[]>([]);
  const [
    recommendationRows,
    setRecommendationRows,
  ] = useState<RowData[]>([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  const [activeTab, setActiveTab] =
    useState<TabId>("overview");
  /* -----------------------------------------
     TAB NAVIGATION
  ----------------------------------------- */

  function openTab(tab: TabId) {
    setActiveTab(tab);
    setSearch("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  /* -----------------------------------------
     LOAD API DATA
  ----------------------------------------- */

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const responses = await Promise.all(
        API_ENDPOINTS.map(
          async (url): Promise<ApiResponse> => {
            const response = await fetch(url);
            const body = await response.text();

            let payload: ApiResponse;

            try {
              if (!body.trim()) {
                throw new Error("Empty response.");
              }

              payload = JSON.parse(body) as ApiResponse;
            } catch {
              if (!response.ok) {
                throw new Error(
                  `${url}: HTTP ${response.status}. ` +
                    "Check the backend terminal."
                );
              }

              throw new Error(
                `${url}: Invalid JSON response.`
              );
            }

            if (!response.ok) {
              const detail =
                !Array.isArray(payload) &&
                typeof payload === "object" &&
                payload !== null &&
                "detail" in payload
                  ? String(payload.detail)
                  : response.statusText;

              throw new Error(
                `${url}: ${
                  detail || "Request failed."
                }`
              );
            }

            return payload;
          }
        )
      );

      setSalesRows(
        getRows(responses[0], "forecasts")
      );

      setRiskRows(
        getRows(responses[1], "predictions")
      );

      setRecommendationRows(
        getRows(responses[2], "recommendations")
      );

      setLastUpdated(
        new Date().toLocaleTimeString([], {
          hour: "numeric",
          minute: "2-digit",
        })
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load dashboard data."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  
useEffect(() => {
  if (authToken) {
    void loadDashboard();
  }
}, [authToken, loadDashboard]);


  /* -----------------------------------------
     FORECAST INFORMATION
  ----------------------------------------- */

  const forecastDateValue =
    salesRows[0]?.forecast_date;

  const forecastDate =
    typeof forecastDateValue === "string"
      ? forecastDateValue
      : "";

  const forecastChartData = useMemo<ForecastItem[]>(
    () =>
      salesRows.map((row) => ({
        product: `P${getText(row.product_id)}`,
        previous: toNumber(
          row.last_day_units_sold
        ),
        predicted: toNumber(
          row.predicted_units_sold
        ),
      })),
    [salesRows]
  );

  /* -----------------------------------------
     CATEGORY ANALYSIS
  ----------------------------------------- */

  const categoryTotals = useMemo<CategoryItem[]>(() => {
    const totals: Record<string, number> = {};

    riskRows.forEach((row) => {
      const category = String(
        row.category ?? "Uncategorized"
      );

      totals[category] =
        (totals[category] ?? 0) + 1;
    });

    return Object.entries(totals).map(
      ([name, value], index) => ({
        name,
        value,
        fill: COLORS[index % COLORS.length],
      })
    );
  }, [riskRows]);

  /* -----------------------------------------
     EXPIRY RISK DATA
  ----------------------------------------- */

  const riskAlerts = useMemo<RiskRow[]>(
    () =>
      [...riskRows]
        .map((row): RiskRow => ({
          ...row,
          probability: toNumber(
            row.high_risk_probability
          ),
          quantityRemaining: toNumber(
            row.quantity_remaining
          ),
          daysToExpiry: toNumber(
            row.days_to_expiry
          ),
        }))
        .sort((a, b) => {
          const aStatus = String(
            a.predicted_risk_status ?? ""
          ).toLowerCase();

          const bStatus = String(
            b.predicted_risk_status ?? ""
          ).toLowerCase();

          if (
            aStatus.includes("expired") &&
            !bStatus.includes("expired")
          ) {
            return -1;
          }

          if (
            bStatus.includes("expired") &&
            !aStatus.includes("expired")
          ) {
            return 1;
          }

          return b.probability - a.probability;
        }),
    [riskRows]
  );

  /* -----------------------------------------
     REMAINING STOCK BY CATEGORY
  ----------------------------------------- */

  const stockTotals = useMemo<StockItem[]>(() => {
    const totals: Record<string, number> = {};

    recommendationRows.forEach((row) => {
      const value = row.quantity_remaining;

      if (
        value === null ||
        value === undefined ||
        value === "" ||
        !Number.isFinite(Number(value))
      ) {
        return;
      }

      const category = String(
        row.category ?? "Uncategorized"
      );

      totals[category] =
        (totals[category] ?? 0) + Number(value);
    });

    return Object.entries(totals).map(
      ([name, total], index) => ({
        name,
        total,
        fill: COLORS[index % COLORS.length],
      })
    );
  }, [recommendationRows]);

  /* -----------------------------------------
     DASHBOARD KPI CALCULATIONS
  ----------------------------------------- */

  const unitsAtRisk = useMemo(
    () =>
      riskRows.reduce((sum, row) => {
        const status = String(
          row.predicted_risk_status ?? ""
        ).toLowerCase();

        if (
          !status.includes("high") &&
          !status.includes("expired")
        ) {
          return sum;
        }

        return (
          sum + toNumber(row.quantity_remaining)
        );
      }, 0),
    [riskRows]
  );

  const predictedDemand = useMemo(
    () =>
      salesRows.reduce(
        (sum, row) =>
          sum + toNumber(row.predicted_units_sold),
        0
      ),
    [salesRows]
  );

  const lowStockAlerts = useMemo(
    () =>
      riskRows.filter((row) => {
        const quantity = Number(
          row.quantity_remaining
        );

        return (
          Number.isFinite(quantity) &&
          quantity >= 0 &&
          quantity < 100
        );
      }).length,
    [riskRows]
  );

  /*
   * Snapshot estimates.
   * These values do not automatically update when
   * the source dataset changes.
   */

  const inventoryValue = 3791508;
  const wasteCost = 99101;

  /* -----------------------------------------
     SEARCH FILTERS
  ----------------------------------------- */

  const filteredInventory = useMemo(
    () =>
      riskRows.filter((row) =>
        matchesSearch(row, search)
      ),
    [riskRows, search]
  );

  const filteredForecast = useMemo(
    () =>
      salesRows.filter((row) =>
        matchesSearch(row, search)
      ),
    [salesRows, search]
  );

  const filteredRisk = useMemo(
    () =>
      riskAlerts.filter((row) =>
        matchesSearch(row, search)
      ),
    [riskAlerts, search]
  );

  const filteredRecommendations = useMemo(
    () =>
      recommendationRows.filter((row) =>
        matchesSearch(row, search)
      ),
    [recommendationRows, search]
  );

  /* -----------------------------------------
     DASHBOARD SUMMARY CARDS
  ----------------------------------------- */

  const stats = [
    {
      label: "Total Inventory Value",
      value: formatINR(inventoryValue),
      note: "Snapshot estimate",
      tone: "green",
      icon: <Boxes size={18} />,
    },
    {
      label: "Units at Expiry Risk",
      value: `${unitsAtRisk.toLocaleString(
        "en-IN"
      )} units`,
      note: "High-risk and expired records",
      tone: "amber",
      icon: <ShieldAlert size={18} />,
    },
    {
      label: "Estimated Waste Cost",
      value: formatINR(wasteCost),
      note: "Snapshot waste estimate",
      tone: "purple",
      icon: <Recycle size={18} />,
    },
    {
      label: "Predicted Demand",
      value: `${predictedDemand.toFixed(1)} units`,
      note: "Total across returned forecasts",
      tone: "green",
      icon: <TrendingUp size={18} />,
    },
    {
      label: "Low Stock Alerts",
      value: lowStockAlerts.toLocaleString("en-IN"),
      note: "Below 100 units (demo rule)",
      tone: "amber",
      icon: <AlertTriangle size={18} />,
    },
  ];

  /* =========================================
   AUTHENTICATION PAGE
========================================= */

if (!authToken) {
  return (
    <AuthPage
      onLoginSuccess={handleLoginSuccess}
    />
  );
}



  /* =========================================
     RENDER APPLICATION
  ========================================= */

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <aside className="sidebar">
        <a
          className="brand"
          href="#overview"
          onClick={(event) => {
            event.preventDefault();
            openTab("overview");
          }}
        >
          <span className="brand-mark">
            <Leaf size={23} />
          </span>

          <span className="brand-text">
            <strong>WasteWise AI</strong>
            <small>
              SMART INVENTORY MANAGEMENT
            </small>
          </span>
        </a>

        <div className="nav-label">
          WORKSPACE
        </div>

        <nav
          className="side-nav"
          aria-label="Main navigation"
        >
          {NAV_ITEMS.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`nav-item ${
                activeTab === item.id ? "active" : ""
              }`}
              aria-current={
                activeTab === item.id
                  ? "page"
                  : undefined
              }
              onClick={(event) => {
                event.preventDefault();
                openTab(item.id);
              }}
            >
              {item.icon}
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-tip">
            <Leaf size={21} />
            <strong>Waste less.</strong>
            <p>
              Make better inventory decisions with data.
            </p>
          </div>

          <div className="sidebar-version">
            WasteWise AI · Prototype
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace / {TITLES[activeTab]}
            </p>

            <h1>{TITLES[activeTab]}</h1>

            <p className="page-subtitle">
              {DESCRIPTIONS[activeTab]}
            </p>
          </div>

          <div className="header-actions">
            <label
              className="search-box"
              aria-label="Search records"
            >
              <Search size={15} />

              <input
                type="text"
                placeholder="Search products or batches..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
              />
            </label>

            <button
              type="button"
              className="refresh-button"
              onClick={() => void loadDashboard()}
              disabled={loading}
            >
              <RefreshCw
                size={16}
                className={loading ? "spin" : ""}
              />

              {loading ? "Refreshing..." : "Refresh"}
            </button>
            <button
           type="button"
           className="refresh-button"
             onClick={handleLogout}
           >
            Logout
           </button>
          </div>
        </header>

        {/* API ERROR */}

        {error && (
          <div
            className="error"
            role="alert"
          >
            <AlertTriangle size={19} />

            <div>
              <strong>
                Unable to load dashboard data
              </strong>

              <p>{error}</p>

              <p>
                Check that the FastAPI backend is running.
              </p>
            </div>
          </div>
        )}

        {/* PAGE HEADING */}

        <div className="section-heading">
          <div>
            <h2>{TITLES[activeTab]}</h2>
            <p>{DESCRIPTIONS[activeTab]}</p>
          </div>

          <span className="updated-label">
            {lastUpdated
              ? `Updated at ${lastUpdated}`
              : loading
                ? "Loading API data..."
                : "Waiting for data"}
          </span>
        </div>

        {/* =================================
            1. DASHBOARD
        ================================= */}

        {activeTab === "overview" && (
          <div className="tab-content-stack">

            {/* HEALTHIER FOOD - LESS WASTE BANNER */}

            <section className="dashboard-hero">

              <div className="dashboard-hero-copy">

                <span className="hero-eyebrow">
                  SMART INVENTORY • LESS WASTE • GREENER TOMORROW
                </span>

                <h2>
                  Healthier Food,
                  <br />
                  Less Waste
                </h2>

                <p>
                  Better inventory. Fresher food.
                  A sustainable tomorrow.
                </p>

                <span className="hero-tagline">
                  Smart Inventory • Less Waste
                </span>

              </div>

              <img
                src="/vegetables.png"
                alt="Fresh vegetables including broccoli, carrots, tomatoes and capsicum"
                className="hero-produce-image"
              />

            </section>

            {/* DASHBOARD SUMMARY CARDS */}

            <section className="stats-grid">
              {stats.map((item) => (
                <article
                  key={item.label}
                  className={`metric-card metric-${item.tone}`}
                >
                  <div className="metric-top">
                    <span>{item.label}</span>

                    <span className="metric-icon">
                      {item.icon}
                    </span>
                  </div>

                  <strong>{item.value}</strong>

                  <p>
                    <CheckCircle2 size={14} />
                    {item.note}
                  </p>
                </article>
              ))}
            </section>

            {/* FORECAST CHART */}

            <ForecastChart
              data={forecastChartData}
              loading={loading}
              date={forecastDate}
            />

          </div>
        )}

        {/* =================================
            2. INVENTORY
        ================================= */}

        {activeTab === "inventory" && (
          <div className="inventory-page">

            <div className="inventory-page-header">
              <div>
                <h2>Your Inventory</h2>
                <p>
                  Manage and monitor your available stock.
                </p>
              </div>

              <span className="inventory-date">
                {lastUpdated
                  ? `Updated ${lastUpdated}`
                  : "Inventory overview"}
              </span>
            </div>

            {/* INVENTORY SUMMARY CARDS */}

            <section className="inventory-kpis">

              <article className="inventory-kpi-card">
                <span className="inventory-kpi-icon inventory-blue">
                  <Boxes size={21} />
                </span>

                <div>
                  <p>Total Batches</p>
                  <h2>
                    {riskRows.length.toLocaleString("en-IN")}
                  </h2>
                </div>
              </article>

              <article className="inventory-kpi-card">
                <span className="inventory-kpi-icon inventory-purple">
                  <Package size={21} />
                </span>

                <div>
                  <p>Remaining Units</p>
                  <h2>
                    {riskRows
                      .reduce(
                        (sum, row) =>
                          sum +
                          Math.max(
                            0,
                            toNumber(row.quantity_remaining)
                          ),
                        0
                      )
                      .toLocaleString("en-IN")}
                  </h2>
                </div>
              </article>

              <article className="inventory-kpi-card">
                <span className="inventory-kpi-icon inventory-green">
                  <CheckCircle2 size={21} />
                </span>

                <div>
                  <p>In Stock</p>
                  <h2>
                    {riskRows
                      .filter((row) => {
                        const quantity = toNumber(
                          row.quantity_remaining
                        );

                        const status = String(
                          row.predicted_risk_status ?? ""
                        ).toLowerCase();

                        const days = Number(
                          row.days_to_expiry
                        );

                        return (
                          quantity >= 100 &&
                          !status.includes("high") &&
                          !status.includes("expired") &&
                          (!Number.isFinite(days) ||
                            days >= 0)
                        );
                      })
                      .length.toLocaleString("en-IN")}
                  </h2>
                </div>
              </article>

              <article className="inventory-kpi-card">
                <span className="inventory-kpi-icon inventory-orange">
                  <AlertTriangle size={21} />
                </span>

                <div>
                  <p>Low Stock Batches</p>
                  <h2>
                    {lowStockAlerts.toLocaleString("en-IN")}
                  </h2>
                </div>
              </article>

            </section>

            {/* CATEGORY CHART */}

            <CategoryChart
              data={categoryTotals}
              loading={loading}
            />

            {/* SEARCH AND EXPORT */}

            <section className="inventory-toolbar">

              <label className="inventory-search">
                <Search size={17} />

                <input
                  type="text"
                  placeholder="Search product, batch or category..."
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                />
              </label>

              <button
                type="button"
                className="inventory-export-button"
                onClick={() => {
                  const headers = [
                    "Batch ID",
                    "Product ID",
                    "Category",
                    "Remaining Quantity",
                    "Days to Expiry",
                    "Risk Status",
                  ];

                  const csvRows = filteredInventory.map(
                    (row) =>
                      [
                        row.batch_id,
                        row.product_id,
                        row.category,
                        row.quantity_remaining,
                        row.days_to_expiry,
                        row.predicted_risk_status,
                      ]
                        .map(
                          (value) =>
                            `"${String(
                              value ?? ""
                            ).replace(/"/g, '""')}"`
                        )
                        .join(",")
                  );

                  const csvContent = [
                    headers.join(","),
                    ...csvRows,
                  ].join("\r\n");

                  const blob = new Blob(
                    [csvContent],
                    {
                      type: "text/csv;charset=utf-8;",
                    }
                  );

                  const url = URL.createObjectURL(blob);
                  const link = document.createElement("a");

                  link.href = url;
                  link.download = "wastewise_inventory.csv";

                  document.body.appendChild(link);
                  link.click();
                  link.remove();

                  URL.revokeObjectURL(url);
                }}
              >
                Export CSV
              </button>

            </section>

            {/* INVENTORY TABLE */}

            <section className="panel inventory-table-panel">

              <div className="panel-heading inventory-table-heading">
                <div>
                  <h2>Inventory List</h2>
                  <p className="muted">
                    Review stock quantity and expiry status
                  </p>
                </div>

                <span className="record-count">
                  {filteredInventory.length.toLocaleString(
                    "en-IN"
                  )}{" "}
                  records
                </span>
              </div>

              {filteredInventory.length === 0 ? (
                <p className="empty-state">
                  {loading
                    ? "Loading inventory..."
                    : "No inventory records found."}
                </p>
              ) : (

                <div className="table-wrap inventory-table-wrap">

                  <table className="professional-inventory-table">

                    <thead>
                      <tr>
                        <th>Batch ID</th>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Remaining Qty</th>
                        <th>Expiry</th>
                        <th>Availability</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredInventory
                        .slice(0, 30)
                        .map((row, index) => {

                          const quantity = toNumber(
                            row.quantity_remaining
                          );

                          const daysValue =
                            row.days_to_expiry;

                          const days = Number(daysValue);

                          const rawStatus = String(
                            row.predicted_risk_status ?? ""
                          );

                          const statusLower =
                            rawStatus.toLowerCase();

                          const expired =
                            statusLower.includes("expired") ||
                            (
                              daysValue !== null &&
                              daysValue !== undefined &&
                              daysValue !== "" &&
                              Number.isFinite(days) &&
                              days < 0
                            );

                          const highRisk =
                            statusLower.includes("high");

                          const lowStock =
                            quantity < 100 && !expired;

                          const status = expired
                            ? "Expired"
                            : highRisk
                              ? "High Risk"
                              : lowStock
                                ? "Low Stock"
                                : "In Stock";

                          const statusClass = expired
                            ? "inventory-expired"
                            : highRisk
                              ? "inventory-high-risk"
                              : lowStock
                                ? "inventory-low-stock"
                                : "inventory-in-stock";

                          return (
                            <tr
                              key={String(
                                row.batch_id ??
                                  `${row.product_id}-${index}`
                              )}
                            >

                              <td>
                                {getText(row.batch_id)}
                              </td>

                              <td>
                                <div className="inventory-product-cell">

                                  <span className="inventory-product-icon">
                                    <Package size={16} />
                                  </span>

                                  <strong>
                                    Product{" "}
                                    {getText(row.product_id)}
                                  </strong>

                                </div>
                              </td>

                              <td>
                                {getText(row.category)}
                              </td>

                              <td>
                                <strong>
                                  {quantity.toLocaleString(
                                    "en-IN"
                                  )}
                                </strong>
                              </td>

                              <td>
                                {daysValue === null ||
                                daysValue === undefined ||
                                daysValue === ""
                                  ? "—"
                                  : Number.isFinite(days)
                                    ? days < 0
                                      ? `${Math.abs(
                                          days
                                        )} days overdue`
                                      : `${days} days left`
                                    : getText(daysValue)}
                              </td>

                              <td>
                                <span
                                  className={`inventory-status-pill ${statusClass}`}
                                >
                                  {status}
                                </span>
                              </td>

                            </tr>
                          );
                        })}
                    </tbody>

                  </table>
                </div>
              )}

              <p className="muted table-footnote">
                Showing up to 30 records. Export CSV to save
                all records matching the current search.
              </p>

            </section>

          </div>
        )}

        {/* =================================
            3. DEMAND FORECAST
        ================================= */}

        {activeTab === "forecast" && (
          <div className="tab-content-stack">

            <ForecastChart
              data={forecastChartData}
              loading={loading}
              date={forecastDate}
            />

            <DataTable
              title="Next-Day Demand Forecast"
              rows={filteredForecast}
              icon={<TrendingUp size={18} />}
            />

          </div>
        )}

        {/* =================================
            4. EXPIRY RISK
        ================================= */}

        {activeTab === "risk" && (
          <div className="tab-content-stack">

            <RiskAlerts
              rows={filteredRisk}
              loading={loading}
            />

            <DataTable
              title="Expiry Risk Monitoring"
              rows={filteredRisk}
              icon={<ShieldAlert size={18} />}
            />

          </div>
        )}

        {/* =================================
            5. RECOMMENDATIONS
        ================================= */}

        {activeTab === "recommendations" && (
          <div className="tab-content-stack">

            <section className="stats-grid">

              <article className="metric-card metric-purple">
                <div className="metric-top">
                  <span>Total Recommendations</span>

                  <span className="metric-icon">
                    <Recycle size={18} />
                  </span>
                </div>

                <strong>
                  {recommendationRows.length.toLocaleString(
                    "en-IN"
                  )}
                </strong>

                <p>
                  <CheckCircle2 size={14} />
                  Suggestions returned by the API
                </p>
              </article>

              <article className="metric-card metric-amber">
                <div className="metric-top">
                  <span>Matching Results</span>

                  <span className="metric-icon">
                    <Search size={18} />
                  </span>
                </div>

                <strong>
                  {filteredRecommendations.length.toLocaleString(
                    "en-IN"
                  )}
                </strong>

                <p>
                  <CheckCircle2 size={14} />
                  Results matching your search
                </p>
              </article>

            </section>

            <DataTable
              title="Waste Reduction Recommendations"
              rows={filteredRecommendations}
              icon={<Recycle size={18} />}
            />

          </div>
        )}

        {/* =================================
            6. WASTE REPORTS
        ================================= */}

        {activeTab === "reports" && (
          <div className="tab-content-stack">

            <section className="stats-grid">

              <article className="metric-card metric-purple">
                <div className="metric-top">
                  <span>Estimated Waste Cost</span>

                  <span className="metric-icon">
                    <Recycle size={18} />
                  </span>
                </div>

                <strong>{formatINR(wasteCost)}</strong>

                <p>
                  <CheckCircle2 size={14} />
                  Snapshot estimate
                </p>
              </article>

              <article className="metric-card metric-green">
                <div className="metric-top">
                  <span>Inventory Value</span>

                  <span className="metric-icon">
                    <Boxes size={18} />
                  </span>
                </div>

                <strong>
                  {formatINR(inventoryValue)}
                </strong>

                <p>
                  <CheckCircle2 size={14} />
                  Snapshot estimate
                </p>
              </article>

              <article className="metric-card metric-amber">
                <div className="metric-top">
                  <span>Recommendation Records</span>

                  <span className="metric-icon">
                    <Package size={18} />
                  </span>
                </div>

                <strong>
                  {recommendationRows.length.toLocaleString(
                    "en-IN"
                  )}
                </strong>

                <p>
                  <CheckCircle2 size={14} />
                  Records used for stock summary
                </p>
              </article>

            </section>

            <RemainingStockChart
              data={stockTotals}
              loading={loading}
            />

            <p className="muted report-note">
              Cost values are snapshot estimates and do not
              automatically change when the dataset changes.
            </p>

          </div>
        )}

        {/* =================================
            7. MODEL METRICS
        ================================= */}

        {activeTab === "metrics" && (
          <div className="model-metrics-page">

            {/* SUMMARY CARDS */}

            <section className="model-metrics-kpis">

              <article className="model-metric-card">
                <span className="model-metric-label">
                  Demand Forecast MAE
                </span>

                <strong className="model-metric-value">
                  2.61
                </strong>

                <span className="model-metric-sub">
                  Baseline: 3.92 units
                </span>
              </article>

              <article className="model-metric-card">
                <span className="model-metric-label">
                  Demand Forecast RMSE
                </span>

                <strong className="model-metric-value">
                  3.53
                </strong>

                <span className="model-metric-sub">
                  Baseline: 5.08 units
                </span>
              </article>

              <article className="model-metric-card">
                <span className="model-metric-label">
                  Forecast R² Score
                </span>

                <strong className="model-metric-value">
                  84.29%
                </strong>

                <span className="model-metric-sub">
                  410 testing records
                </span>
              </article>

              <article className="model-metric-card">
                <span className="model-metric-label">
                  Expiry Risk F1 Score
                </span>

                <strong className="model-metric-value">
                  87.07%
                </strong>

                <span className="model-metric-sub">
                  400 testing records
                </span>
              </article>

            </section>

            {/* MODEL DETAILS */}

            <section className="model-metrics-models">

              <article className="panel model-info-card">
                <div className="panel-heading">
                  <div className="panel-title">
                    <span className="panel-icon">
                      <TrendingUp size={18} />
                    </span>

                    <div>
                      <h2>Demand Forecast Model</h2>

                      <p className="muted">
                        Random Forest Regressor
                      </p>
                    </div>
                  </div>
                </div>

                <div className="model-details">

                  <div>
                    <span>Target</span>
                    <strong>units_sold</strong>
                  </div>

                  <div>
                    <span>Training records</span>
                    <strong>1,620</strong>
                  </div>

                  <div>
                    <span>Testing records</span>
                    <strong>410</strong>
                  </div>

                  <div>
                    <span>Test period</span>
                    <strong>
                      Sep 17 – Oct 27, 2026
                    </strong>
                  </div>

                </div>
              </article>

              <article className="panel model-info-card">
                <div className="panel-heading">
                  <div className="panel-title">
                    <span className="panel-icon">
                      <ShieldAlert size={18} />
                    </span>

                    <div>
                      <h2>Expiry Risk Model</h2>

                      <p className="muted">
                        Classification evaluation
                      </p>
                    </div>
                  </div>
                </div>

                <div className="model-details">

                  <div>
                    <span>Target</span>
                    <strong>expiry_risk_label</strong>
                  </div>

                  <div>
                    <span>Training records</span>
                    <strong>1,600</strong>
                  </div>

                  <div>
                    <span>Testing records</span>
                    <strong>400</strong>
                  </div>

                  <div>
                    <span>ROC-AUC</span>
                    <strong>93.71%</strong>
                  </div>

                </div>
              </article>

            </section>

            {/* PERFORMANCE CHARTS */}

            <section className="model-metrics-chart-grid">

              {/* FORECAST BASELINE CHART */}

              <article className="panel model-chart-card">
                <div className="panel-heading">
                  <div className="panel-title">
                    <span className="panel-icon">
                      <TrendingUp size={18} />
                    </span>

                    <div>
                      <h2>Forecast Error vs Baseline</h2>

                      <p className="muted">
                        Compare MAE and RMSE
                      </p>
                    </div>
                  </div>
                </div>

                <div className="model-chart-area">
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <BarChart
                      data={[
                        {
                          metric: "MAE",
                          model: 2.6053,
                          baseline: 3.9244,
                        },
                        {
                          metric: "RMSE",
                          model: 3.5346,
                          baseline: 5.0806,
                        },
                      ]}
                      margin={{
                        top: 10,
                        right: 8,
                        left: -15,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#e5ece8"
                      />

                      <XAxis
                        dataKey="metric"
                        tickLine={false}
                        axisLine={false}
                      />

                      <YAxis
                        tickLine={false}
                        axisLine={false}
                      />

                      <Tooltip />

                      <Bar
                        dataKey="model"
                        name="Random Forest"
                        fill="#27845c"
                        radius={[5, 5, 0, 0]}
                      />

                      <Bar
                        dataKey="baseline"
                        name="Baseline"
                        fill="#d9ad62"
                        radius={[5, 5, 0, 0]}
                      />

                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <p className="muted model-chart-note">
                  Lower MAE and RMSE indicate smaller prediction errors.
                </p>
              </article>

              {/* EXPIRY RISK CHART */}

              <article className="panel model-chart-card">
                <div className="panel-heading">
                  <div className="panel-title">
                    <span className="panel-icon">
                      <ShieldAlert size={18} />
                    </span>

                    <div>
                      <h2>Expiry Risk Performance</h2>

                      <p className="muted">
                        Classification evaluation scores
                      </p>
                    </div>
                  </div>
                </div>

                <div className="model-chart-area">
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <BarChart
                      data={[
                        {
                          metric: "Accuracy",
                          score: 85.00,
                        },
                        {
                          metric: "Precision",
                          score: 87.83,
                        },
                        {
                          metric: "Recall",
                          score: 86.32,
                        },
                        {
                          metric: "F1 Score",
                          score: 87.07,
                        },
                        {
                          metric: "ROC-AUC",
                          score: 93.71,
                        },
                      ]}
                      margin={{
                        top: 10,
                        right: 8,
                        left: -12,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#e5ece8"
                      />

                      <XAxis
                        dataKey="metric"
                        tickLine={false}
                        axisLine={false}
                        tick={{ fontSize: 10 }}
                        interval={0}
                      />

                      <YAxis
                        domain={[0, 100]}
                        tickFormatter={(value) => `${value}%`}
                        tickLine={false}
                        axisLine={false}
                      />

                      <Tooltip
                        formatter={(value) =>
                          `${Number(value).toFixed(2)}%`
                        }
                      />

                      <Bar
                        dataKey="score"
                        name="Score"
                        radius={[5, 5, 0, 0]}
                      >
                        {[
                          "#7d8de9",
                          "#7ca7a0",
                          "#d9ad62",
                          "#27845c",
                          "#b8a8ee",
                        ].map((color, index) => (
                          <Cell
                            key={index}
                            fill={color}
                          />
                        ))}
                      </Bar>

                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <p className="muted model-chart-note">
                  Scores are percentages from the saved evaluation results.
                </p>
              </article>

            </section>

            {/* COMPLETE METRICS TABLE */}

            <section className="panel model-info-card">
              <div className="panel-heading">
                <div className="panel-title">
                  <span className="panel-icon">
                    <CheckCircle2 size={18} />
                  </span>

                  <div>
                    <h2>All Evaluation Metrics</h2>

                    <p className="muted">
                      Detailed results from the evaluation files
                    </p>
                  </div>
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Metric</th>
                      <th>Model Value</th>
                      <th>Baseline</th>
                    </tr>
                  </thead>

                  <tbody>

                    <tr>
                      <td>Demand Forecast</td>
                      <td>MAE</td>
                      <td>2.6053</td>
                      <td>3.9244</td>
                    </tr>

                    <tr>
                      <td>Demand Forecast</td>
                      <td>RMSE</td>
                      <td>3.5346</td>
                      <td>5.0806</td>
                    </tr>

                    <tr>
                      <td>Demand Forecast</td>
                      <td>R² Score</td>
                      <td>0.8429</td>
                      <td>Not provided</td>
                    </tr>

                    <tr>
                      <td>Expiry Risk</td>
                      <td>Accuracy</td>
                      <td>85.00%</td>
                      <td>Not provided</td>
                    </tr>

                    <tr>
                      <td>Expiry Risk</td>
                      <td>Precision</td>
                      <td>87.83%</td>
                      <td>Not provided</td>
                    </tr>

                    <tr>
                      <td>Expiry Risk</td>
                      <td>Recall</td>
                      <td>86.32%</td>
                      <td>Not provided</td>
                    </tr>

                    <tr>
                      <td>Expiry Risk</td>
                      <td>F1 Score</td>
                      <td>87.07%</td>
                      <td>Not provided</td>
                    </tr>

                    <tr>
                      <td>Expiry Risk</td>
                      <td>ROC-AUC</td>
                      <td>93.71%</td>
                      <td>Not provided</td>
                    </tr>

                  </tbody>
                </table>
              </div>
            </section>

            {/* EVALUATION LIMITATIONS */}

            <section className="panel model-limitations">
              <div className="panel-title">
                <AlertTriangle size={20} />
                <h2>Evaluation Notes</h2>
              </div>

              <p>
                The demand forecast metrics are based on
                historical sales simulation and represent
                an initial evaluation.
              </p>

              <p>
                The expiry-risk target labels are simulated
                and match the simulated-waste definition
                exactly. These results should not be treated
                as proof of real-world expiry prediction
                performance.
              </p>

              <p>
                Validate both models on representative
                real-world data before relying on their
                predictions for operational decisions.
              </p>
            </section>

          </div>
        )}

        {/* FOOTER */}

        <footer className="footer">
          <span>WasteWise AI</span>

          <span>
            Experimental prototype · API-driven dashboard ·
            Verify real expiry and food-safety requirements.
          </span>
        </footer>

      </main>
    </div>
  );
}

export default App;
