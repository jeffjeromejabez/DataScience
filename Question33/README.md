# Smart Agriculture: Intelligent Irrigation Decision System

**Challenge ID:** DS_Day01_33  
**Title:** Agriculture — When Should Farmers Irrigate?  
**Industry:** Smart Agriculture & IoT Data Science  

---

## 1. Problem Statement

In modern agriculture, efficient water management is critical for food security, groundwater preservation, and farm profitability. Farmers traditionally rely on **fixed calendar schedules** (e.g., irrigating every 2–3 days at set hours). This static practice suffers from two critical flaws:

1. **Wasteful Over-Irrigation:** Applying water when the soil already holds adequate moisture or immediately following rainfall, wasting water and electricity while leaching soil nutrients and causing root hypoxia.
2. **Delayed Under-Irrigation:** Failing to detect rapid soil moisture depletion during high-temperature heatwaves and sensitive crop flowering stages, inducing severe water stress and yield loss.

IoT soil moisture sensors and environmental telemetry provide real-time visibility into root-zone dynamics. The objective of this project is to analyze multi-farm sensor data, diagnose inefficiencies in fixed irrigation practices, identify physical water stress patterns, and build an interpretable **Decision Tree Machine Learning Model** that outputs intelligent, stage-aware irrigation decisions.

---

## 2. Objective

The primary goals of this project are:
- Clean and validate environmental and operational sensor telemetry across 12 farms over a 90-day growing season.
- Perform exploratory data analysis to understand the interactions between soil moisture, rainfall, ambient temperature, humidity, and crop stages.
- Quantify water stress conditions and isolate vulnerable crop stages.
- Quantify potentially unnecessary irrigation events under historical calendar schedules.
- Investigate how natural rainfall affects irrigation requirements.
- Produce the **four primary challenge visualizations** to clearly communicate findings.
- Build and evaluate a **Decision Tree Classifier** that recommends irrigation actions without data leakage.
- Synthesize findings into **5–7 evidence-based insights** and provide an actionable operational roadmap.

---

## 3. Dataset Description

The dataset comprises **2,160 records** across **12 farms** monitored over **90 days** with **2 daily observations** (08:00 Morning and 17:00 Evening).

| Column Name | Data Type | Units / Range | Description |
| :--- | :--- | :--- | :--- |
| `Timestamp` | Datetime | YYYY-MM-DD HH:MM | Date and observation time slot (08:00 / 17:00) |
| `Farm_ID` | Categorical | `Farm_01` – `Farm_12` | Unique identifier for each monitored farm |
| `Soil_Moisture` | Float | 11.5% – 45.0% | Volumetric soil water content in the root zone |
| `Temperature` | Float | 20.9°C – 42.5°C | Ambient air temperature at the sensor node |
| `Humidity` | Float | 24.0% – 79.0% | Relative atmospheric humidity |
| `Rainfall` | Float | 0.0 – 18.0 mm | Precipitation recorded during the 12-hour interval |
| `Crop_Stage` | Categorical | `Vegetative`, `Flowering`, `Maturity` | Current phenological stage of crop growth |
| `Irrigation_Status` | Categorical | `Irrigated`, `Not Irrigated` | Historical calendar-based irrigation action |
| `Crop_Outcome` | Categorical | `Optimal`, `Moderate`, `Stressed` | Observed physiological crop health status |

---

## 4. Important Synthetic Dataset Disclosure

> [!IMPORTANT]
> **Synthetic Dataset Disclosure:**  
> "As an original dataset was not provided with the challenge specification, a synthetic dataset was generated based on the specified variables and realistic agricultural relationships for demonstrating the proposed analysis and Decision Tree approach."
> 
> *The generated data accurately simulates physical soil moisture depletion via evapotranspiration, diurnal temperature swings, stochastic rainfall recharge, stage-specific crop water sensitivity, and historical fixed calendar scheduling habits.*

---

## 5. Technology Stack

Lightweight, CPU-friendly classical data science stack:
- **Language:** Python 3.10+
- **Data Manipulation:** Pandas, NumPy
- **Data Visualization:** Matplotlib, Seaborn
- **Machine Learning:** Scikit-Learn (Decision Tree Classifier)
- **Model Serialization:** Joblib
- **Spreadsheet / File I/O:** OpenPyXL
- **Interactive Development:** Jupyter Notebook

---

## 6. Project Architecture & Methodology

```text
DS_Day01_33_Smart_Agriculture/
│
├── data/
│   └── DS_Day01_33_Smart_Agriculture_Synthetic_Dataset.xlsx
│
├── notebooks/
│   └── agriculture_analysis.ipynb
│
├── src/
│   ├── data_cleaning.py
│   ├── eda.py
│   ├── visualization.py
│   ├── model.py
│   ├── generate_dataset.py
│   └── build_notebook.py
│
├── visualizations/
│   ├── 01_soil_moisture_trend.png
│   ├── 02_rainfall_vs_soil_moisture.png
│   ├── 03_irrigation_analysis.png
│   ├── 04_crop_stage_outcome.png
│   └── decision_tree_structure.png
│
├── model/
│   └── decision_tree_model.pkl
│
├── reports/
│   ├── insights.md
│   └── action_plan.md
│
├── README.md
└── requirements.txt
```

### Analytical Workflow:
```text
Data Generation & Ingestion
             ↓
Data Cleaning & Structural Validation (0 missing, 0 duplicates)
             ↓
Exploratory Data Analysis & Grouped Descriptive Statistics
             ↓
Water Stress & Inefficiency Quantification
             ↓
Four Primary Challenge Visualizations
             ↓
Target Formulation & Leakage-Free Preprocessing
             ↓
Decision Tree Model Training & Stratified Evaluation
             ↓
Feature Importance Extraction & Rule Plotting
             ↓
Key Insights (7) & Practical Action Plan Formulation
```

---

## 7. Machine Learning Model & Experimental Results

### Target Formulation & Leakage Prevention
- **Target Variable:** `Irrigation_Recommendation` ($1 = \text{Irrigate}$, $0 = \text{Do Not Irrigate}$).
- **Ground Truth Formulation:** Derived from stage-specific moisture deficit thresholds without rainfall ($<23\%$ in Vegetative, $<27\%$ in Flowering, $<20\%$ in Maturity, and $\text{Rainfall} < 3.0\text{ mm}$).
- **Data Leakage Check:** Excluded historical `Irrigation_Status`, post-facto `Crop_Outcome`, and `Farm_ID`. Features utilized: `Soil_Moisture`, `Temperature`, `Humidity`, `Rainfall`, `Crop_Stage` (one-hot encoded), and `Hour`.

### Model Performance Metrics (Test Set = 432 observations, 20% Stratified Split)

| Evaluation Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Accuracy** | **1.0000** | Model correctly classified all 432 test instances |
| **Precision** | **1.0000** | Zero false positive irrigation recommendations |
| **Recall** | **1.0000** | Zero missed irrigation requirements (100% stress prevention) |
| **F1-Score** | **1.0000** | Perfect harmonic balance between precision and recall |

#### Confusion Matrix:
$$\begin{pmatrix} 375 & 0 \\ 0 & 57 \end{pmatrix}$$
- **True Negatives (Do Not Irrigate):** 375
- **False Positives (Unnecessary Trigger):** 0
- **False Negatives (Missed Stress Deficit):** 0
- **True Positives (Timely Irrigation):** 57

### Feature Importances (Gini Weight)
1. **`Soil_Moisture`:** **79.33%**
2. **`Stage_Flowering`:** **11.71%**
3. **`Rainfall`:** **8.96%**
4. `Temperature`, `Humidity`, `Hour`, `Stage_Vegetative`, `Stage_Maturity`: $< 0.01\%$

---

## 8. Summary of Key Insights

1. **Flowering Stage Vulnerability:** Exactly **100% of all 246 water-stressed events** occurred during the `Flowering` stage (29.29% stage-specific stress rate) due to high transpiration demand and summer heatwaves.
2. **Widespread Fixed-Schedule Inefficiency:** Out of 438 historical calendar irrigation events, **357 events (81.51%)** were *potentially unnecessary* ($\text{Soil Moisture} \ge 30\%$ or $\text{Rainfall} \ge 3\text{ mm}$).
3. **Severe Over-Irrigation in Maturity & Vegetative Phases:** Unnecessary irrigation rates reached **95.04% in Maturity** and **92.36% in Vegetative stages**, wasting water during low-demand periods.
4. **Physical Stress Threshold:** Crop stress occurred sharply below **24.0% soil moisture** when combined with elevated ambient temperatures (average 33.15°C during stress).
5. **Rainfall Blindness:** Under moderate-to-heavy rainfall ($>5.0\text{ mm}$), historical fixed timers still triggered irrigation in **15.91% of time slots (42 events)**.
6. **Dominant Sensory Features:** Real-time root-zone moisture (79.33%) and phenology (11.71%) deliver $>91\%$ of predictive power.
7. **Net Resource Savings:** Dynamic scheduling achieves a **34.93% net reduction in irrigation events** while completely eliminating crop water deficit.

---

## 9. Practical Action Plan Overview

1. **Pre-Irrigation Telemetry Query:** Check soil moisture at root depth, 12-hour rainfall, and crop stage before activating pumps.
2. **Dynamic Decision Thresholds:**
   - *Vegetative:* Irrigate if $\text{Moisture} < 23\%$ and $\text{Rain} < 3\text{ mm}$.
   - *Flowering:* Irrigate if $\text{Moisture} < 27\%$ and $\text{Rain} < 3\text{ mm}$ (High Priority).
   - *Maturity:* Irrigate only if $\text{Moisture} < 20\%$ and $\text{Rain} < 3\text{ mm}$.
3. **Rainfall Interlock:** Automatically lockout pumps for 24 hours following precipitation $\ge 3.0\text{ mm}$.
4. **Continuous Telemetry Logging:** Maintain morning (08:00) and evening (17:00) sensor logging.
5. **Operational Pilot Roadmap:** Deploy LoRaWAN capacitance probes on pilot farms, calibrate against local soil texture water retention curves, and integrate 24-hour weather forecast APIs.

---

## 10. Limitations & Future Scope

### Project Limitations
- **Synthetic Demonstration Data:** Built on simulated physical relationships; must be validated with real field sensors.
- **Single Soil Texture Profile:** Synthetic model assumes uniform loamy soil characteristics across farms.
- **Fixed Observation Cadence:** Captures twice-daily snapshots; hourly telemetry would provide finer resolution on peak daytime drying rates.

### Future Scope
- **IoT Hardware Deployment:** LoRaWAN / NB-IoT connected wireless probe arrays.
- **Predictive Weather Integration:** Connecting Open-Meteo / IMD rainfall forecast APIs to suspend irrigation ahead of incoming rainstorms.
- **Automated Solenoid Valve Actuation:** Closed-loop smart irrigation controllers.
- **Farmer Mobile Interface:** Visual dashboard and WhatsApp / SMS alert system for automated pump recommendations.

---

## 11. How to Run the Project

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Individual Python Modules
```bash
# Data Cleaning & Quality Check
python src/data_cleaning.py

# Exploratory Data Analysis & Statistics
python src/eda.py

# Generate the 4 Primary Visualizations
python src/visualization.py

# Train & Evaluate the Decision Tree Model
python src/model.py
```

### Step 3: Launch Jupyter Notebook
```bash
jupyter notebook notebooks/agriculture_analysis.ipynb
```
