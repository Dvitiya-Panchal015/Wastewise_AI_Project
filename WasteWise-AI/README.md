\# WasteWise AI — Smart Perishable Inventory Management



\## 1. Project Overview



WasteWise AI is a machine learning-based project designed to support perishable inventory management. It combines demand forecasting, expiry-risk prediction, and waste-reduction recommendations in a web dashboard.



The application helps users review predicted product demand, identify inventory batches that may require attention, and view suggested actions for managing stock.



\*\*Important:\*\* This project uses experimental machine learning predictions and simulated labels where applicable. It is a decision-support prototype, not a certified food-safety system.



\## 2. Project Objectives



\- Forecast next-day product sales using historical sales information.

\- Predict expiry-related inventory risk.

\- Generate prioritized waste-reduction recommendations.

\- Provide a web dashboard for reviewing predictions and suggested actions.

\- Expose machine learning functionality through REST API endpoints.



\## 3. Technologies Used



\### Machine Learning and Data Processing

\- Python

\- Pandas

\- Scikit-learn

\- Joblib



\### Backend

\- FastAPI

\- Uvicorn

\- REST APIs



\### Frontend

\- React

\- TypeScript

\- Vite

\- HTML and CSS



\### Data Storage

\- CSV datasets

\- Serialized machine learning models (`.joblib`)



\## 4. Main Project Features



\### 4.1 Demand Forecasting



The demand forecasting model estimates the next day's sales for each product using historical sales features, including:



\- Product ID

\- Day of the week

\- Day of the month

\- Month

\- Weekend indicator

\- Previous-day sales

\- Sales from seven days earlier

\- Seven-day average sales



The model returns predicted units sold, previous-day sales, and the average sales over the preceding seven days.



\*\*Current data limitation:\*\* The available processed sales dataset contains records through September 27, 2026. Consequently, the current forecast is for September 28, 2026. Newer validated sales records are required for a current operational forecast.



\### 4.2 Expiry-Risk Prediction



The expiry-risk model uses inventory information such as:



\- Product category

\- Initial and remaining quantities

\- Days to expiry

\- Recent average daily sales

\- Expected demand before expiry

\- Unit price and cost

\- Discount percentage



The API returns predicted risk status and estimated high-risk probability for inventory batches.



The model was trained using simulated expiry-risk labels. Its predictions must be interpreted as experimental estimates rather than verified food-safety assessments.



\### 4.3 Waste-Reduction Recommendations



The recommendation service combines inventory information with expiry-risk predictions to provide suggested actions.



Examples include:



\- Urgent review of expired items.

\- Prioritizing eligible stock for sale.

\- Considering approved discounts for eligible items.

\- Reviewing demand and stock levels.



Recommendations are suggestions only. Always verify actual expiry dates, storage conditions, product quality, and applicable food-safety requirements. Expired items must not be sold.



\## 5. Dataset Overview



The project uses CSV files for historical sales and inventory information.



| Dataset | Purpose |

|---|---|

| `data/processed/perishable\_inventory.csv` | Historical product sales and inventory records |

| `data/processed/products.csv` | Product information |

| `data/processed/inventory\_batches.csv` | Inventory batch information |

| `data/processed/discount\_scenarios.csv` | Discount scenario records |

| `data/processed/features/inventory\_batch\_features.csv` | Features for expiry-risk prediction |



The historical sales dataset currently contains 1,800 rows across 10 columns of relevant sales and inventory information.



The inventory batch feature dataset contains 2,000 records.



\## 6. Machine Learning Evaluation



\### Demand Forecasting Model



The demand forecast model uses a Random Forest regressor.



Reported evaluation metrics:



\- MAE: 3.9142

\- RMSE: 5.0102

\- R²: 0.7096



The reported baseline MAE was 5.3, and baseline RMSE was 6.9777.



These measurements apply to the available evaluation split and do not guarantee future forecasting performance.



\### Expiry-Risk Model



The expiry-risk model uses a Random Forest classifier.



Reported evaluation metrics:



\- Accuracy: 0.845

\- Precision: 0.8644

\- Recall: 0.8718

\- F1-score: 0.8681

\- ROC-AUC: 0.936



Because the target labels are simulated or rule-generated, these metrics do not establish real-world food-safety accuracy.



\## 7. Important Project Files



\- `backend/app/main.py` — FastAPI application entry point.

\- `backend/app/api/v1/sales.py` — Demand forecasting API.

\- `backend/app/api/v1/risk.py` — Expiry-risk API.

\- `backend/app/api/v1/waste.py` — Waste-recommendation API.

\- `backend/app/services/forecast\_service.py` — Demand forecasting service.

\- `backend/app/services/risk\_service.py` — Expiry-risk prediction service.

\- `backend/app/services/recommendation\_service.py` — Recommendation service.

\- `models/expiry\_risk\_model.joblib` — Saved expiry-risk model.

\- `models/demand\_forecast\_model.joblib` — Saved demand forecasting model.

\- `frontend/src/App.tsx` — Main React dashboard.

\- `frontend/src/main.tsx` — Frontend entry point.

\- `frontend/src/index.css` — Dashboard styling.

\- `frontend/vite.config.ts` — Vite configuration and API proxy.

\- `README.md` — Project documentation.



\## 8. How to Run the Project on Windows



\### Prerequisites



\- Python and the project’s required Python packages.

\- Node.js and npm.

\- The project datasets and saved model files.



\### Start the Backend



Open PowerShell and run:



```powershell

cd "C:\\Users\\hp\\OneDrive\\Desktop\\web\_scraping\_folder\\wasteAI\_project\\WasteWise-AI\\backend"

python -m uvicorn app.main:app --reload

```



The backend should become available at:



`http://127.0.0.1:8000`



API documentation:



`http://127.0.0.1:8000/docs`



\### Start the Frontend



Open a second PowerShell terminal and run:



```powershell

cd "C:\\Users\\hp\\OneDrive\\Desktop\\web\_scraping\_folder\\wasteAI\_project\\WasteWise-AI\\frontend"

npm install

npm run dev

```



Open the frontend URL shown by Vite. With the current configuration, it should be:



`http://127.0.0.1:5173/`



Keep both terminals running while using the application.



\## 9. API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | Check the backend welcome response |

| GET | `/health` | Check backend health |

| GET | `/api/v1/sales/forecast` | Retrieve next-day demand forecasts |

| GET | `/api/v1/risk/expiry` | Retrieve expiry-risk predictions |

| GET | `/api/v1/waste/recommendations` | Retrieve waste-reduction recommendations |



The frontend uses the Vite development proxy to forward `/api` requests to the backend at `http://127.0.0.1:8000`.



\## 10. Project Workflow



1\. Load the processed sales and inventory datasets.

2\. Prepare features for model training and prediction.

3\. Train and evaluate the demand forecasting model.

4\. Train and evaluate the expiry-risk classification model.

5\. Save trained models for later use.

6\. Generate predictions using the saved models.

7\. Serve predictions through FastAPI endpoints.

8\. Fetch API results in the React frontend.

9\. Display forecasts, expiry-risk records, and recommendations.

10\. Review model limitations and validate results before real-world use.



\## 11. Limitations



\- The current sales dataset is historical and ends on September 27, 2026.

\- Demand forecasts should be regenerated after updating and validating the source dataset.

\- Expiry-risk labels are simulated or rule-generated and require validation against real operational outcomes.

\- Recommendations are rule-based guidance and do not demonstrate a measured reduction in food waste.

\- The dashboard is a prototype; production deployment would require additional security, monitoring, data-quality checks, and operational validation.



\## 12. Future Enhancements



\- Integrate regularly updated inventory and sales data.

\- Automate scheduled model retraining and forecasting.

\- Add interactive filtering by product, category, expiry status, and risk level.

\- Improve model monitoring and record prediction history.

\- Evaluate recommendations using actual waste outcomes.

\- Add authentication, access controls, logging, and deployment configuration.

\- Improve forecasting through comparison with additional models and time-based evaluation.



\## 13. Conclusion



WasteWise AI demonstrates how machine learning, APIs, and a web dashboard can be combined to support perishable inventory management. It provides demand forecasts, experimental expiry-risk predictions, and suggested inventory actions in one interface.



The current implementation is a working prototype. Further validation using recent real-world sales, inventory, and waste data is required before operational use.



