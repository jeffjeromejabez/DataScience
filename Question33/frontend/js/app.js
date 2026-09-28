/**
 * AgriSense AI — Smart Agriculture Precision Irrigation Frontend Logic
 * Implements real-time Decision Tree inference, multi-farm telemetry scrubbing,
 * interactive Chart.js visualizations, 7 key insights accordion, and ROI calculator.
 */

// Global State
let farmDataStore = null;
let selectedFarmId = "Farm_01";
let selectedDayIndex = 90; // Default mid-season (Day 45, morning)
let chartInstances = {};

// Fallback Embedded Dataset if JSON file fetch is blocked by local file:// protocol
const FALLBACK_GLOBAL_DATA = {
  num_farms: 12,
  num_days: 90,
  total_records: 2160,
  calendar_irrigations: 438,
  unnecessary_irrigations: 357,
  unnecessary_percentage: 81.5,
  smart_irrigations: 285,
  water_events_saved: 153,
  water_saved_percentage: 34.9,
  total_stressed_events: 246,
  flowering_stress_rate: 29.3
};

// 7 Key Insights Data
const KEY_INSIGHTS = [
  {
    num: "01",
    title: "Flowering Stage Vulnerability (100% of Stress Events)",
    evidence: "246 / 2,160 records (11.39%) exhibited stress; all 246 (100%) occurred in Flowering (29.29% stage rate).",
    interpretation: "Peak flowering coincides with maximum transpiration and summer heat (mean 33.15°C), which calendar intervals fail to buffer.",
    implication: "Dynamic AI prioritizes soil moisture above 27.0% specifically during flowering."
  },
  {
    num: "02",
    title: "Substantial Inefficiency in Historical Calendar Practice",
    evidence: "357 out of 438 fixed-schedule irrigation events (81.51%) were potentially unnecessary.",
    interpretation: "Farmers pumped water on predetermined calendar days regardless of whether soil moisture was already high (>=30%) or after rain.",
    implication: "Transitioning to sensor-triggered irrigation eliminates 81.5% of wasted pumping cycles."
  },
  {
    num: "03",
    title: "Disproportionate Over-Watering in Maturity and Vegetative Phases",
    evidence: "95.04% of irrigations in Maturity and 92.36% in Vegetative were potentially unnecessary.",
    interpretation: "Crop water demand drops during ripening and early vegetative stages, yet calendar pumping continued uniformly.",
    implication: "Thresholds automatically taper off in late stages to permit natural crop dry-down."
  },
  {
    num: "04",
    title: "Sharp Physical Boundary for Water Stress (<24.0% Moisture)",
    evidence: "Mean soil moisture in stressed state was 17.06% (max 23.90%), compared to 37.28% overall average.",
    interpretation: "Moisture deficit below 24% under high temperatures (>33°C) halts transpiration cooling, inducing stress.",
    implication: "Real-time automated alerts trigger at 27% to prevent moisture ever reaching the critical 24% threshold."
  },
  {
    num: "05",
    title: "Rainfall Blindness in Historical Habits",
    evidence: "Irrigation was still executed in 15.91% of time slots with moderate-to-heavy rain (>5.0 mm).",
    interpretation: "Without automated rain sensors, timer-based pumps continued operating during active downpours.",
    implication: "Automated 24-hour lockout following >=3.0 mm rainfall saves water instantly."
  },
  {
    num: "06",
    title: "Decision Tree Identifies Dominant Predictive Feature",
    evidence: "Soil Moisture contributed 79.33% of Gini importance, followed by Flowering Stage (11.71%) and Rain (8.96%).",
    interpretation: "Root-zone capacitance probes already integrate atmospheric temperature and humidity effects into a single state.",
    implication: "A probe + crop calendar provides >90% precision without complex multi-sensor suites."
  },
  {
    num: "07",
    title: "Dual Win: 34.9% Net Water Reduction with Zero Crop Deficit",
    evidence: "Smart system recommended 285 irrigations vs. 438 historical events (34.93% reduction).",
    interpretation: "Smart irrigation eliminates wasteful pumping while ensuring water is applied at exact critical moments.",
    implication: "Delivers rapid ROI via lower pumping energy bills and maximized harvest yield."
  }
];

// Preset Scenarios
const PRESET_SCENARIOS = {
  floweringDeficit: { moisture: 21.5, stage: "Flowering", rain: 0.0, temp: 34.5, hum: 38, slot: "8" },
  postRainSaturated: { moisture: 42.0, stage: "Vegetative", rain: 8.5, temp: 24.0, hum: 78, slot: "8" },
  fixedOverirrigate: { moisture: 38.0, stage: "Maturity", rain: 0.0, temp: 28.0, hum: 55, slot: "17" },
  vegetativeModerate: { moisture: 31.0, stage: "Vegetative", rain: 0.0, temp: 27.5, hum: 62, slot: "8" },
  maturityRipening: { moisture: 23.0, stage: "Maturity", rain: 0.0, temp: 30.0, hum: 45, slot: "17" }
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  initSimulator();
  initCalculator();
  renderInsightsList();
  initActionPlanExport();
  
  await loadFarmData();
  initFarmTelemetry();
  initChallengeVisualizations();
});

// Tab Navigation Logic
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
        // Trigger chart resize if visualizations or telemetry opened
        if (targetId === "tabVisualizations" || targetId === "tabTelemetry") {
          setTimeout(() => {
            Object.values(chartInstances).forEach(c => c && c.resize && c.resize());
          }, 100);
        }
      }
    });
  });
}

// --------------------------------------------------------------------------
// MODULE 1: AI DECISION TREE INFERENCE ENGINE & SIMULATOR
// --------------------------------------------------------------------------
function initSimulator() {
  const inputMoisture = document.getElementById("inputSoilMoisture");
  const inputRain = document.getElementById("inputRainfall");
  const inputTemp = document.getElementById("inputTemp");
  const inputHumidity = document.getElementById("inputHumidity");
  const selectTime = document.getElementById("selectTimeSlot");
  const selectPreset = document.getElementById("scenarioPreset");
  const stageRadios = document.querySelectorAll('input[name="cropStageRadio"]');

  // Input event listeners
  [inputMoisture, inputRain, inputTemp, inputHumidity, selectTime].forEach(el => {
    el.addEventListener("input", runDecisionTreeInference);
  });

  stageRadios.forEach(radio => {
    radio.addEventListener("change", (e) => {
      document.querySelectorAll(".stage-tile").forEach(t => t.classList.remove("active"));
      e.target.closest(".stage-tile").classList.add("active");
      runDecisionTreeInference();
    });
  });

  // Preset Scenario Change
  selectPreset.addEventListener("change", (e) => {
    const presetKey = e.target.value;
    if (PRESET_SCENARIOS[presetKey]) {
      const p = PRESET_SCENARIOS[presetKey];
      inputMoisture.value = p.moisture;
      inputRain.value = p.rain;
      inputTemp.value = p.temp;
      inputHumidity.value = p.hum;
      selectTime.value = p.slot;

      // Update Radio Tile
      stageRadios.forEach(radio => {
        if (radio.value === p.stage) {
          radio.checked = true;
          document.querySelectorAll(".stage-tile").forEach(t => t.classList.remove("active"));
          radio.closest(".stage-tile").classList.add("active");
        }
      });

      runDecisionTreeInference();
    }
  });

  // Initial Run
  runDecisionTreeInference();
}

function runDecisionTreeInference() {
  // Read Current Inputs
  const moisture = parseFloat(document.getElementById("inputSoilMoisture").value);
  const rain = parseFloat(document.getElementById("inputRainfall").value);
  const temp = parseFloat(document.getElementById("inputTemp").value);
  const humidity = parseFloat(document.getElementById("inputHumidity").value);
  const timeSlot = document.getElementById("selectTimeSlot").value;
  
  const stageRadio = document.querySelector('input[name="cropStageRadio"]:checked');
  const cropStage = stageRadio ? stageRadio.value : "Flowering";

  // Update UI Displays
  document.getElementById("dispSoilMoisture").textContent = moisture.toFixed(1) + "%";
  document.getElementById("dispRainfall").textContent = rain.toFixed(1) + " mm";
  document.getElementById("dispTemp").textContent = temp.toFixed(1) + " °C";
  document.getElementById("dispHumidity").textContent = humidity.toFixed(1) + "%";

  const stageBadge = document.getElementById("dispCropStageBadge");
  if (cropStage === "Flowering") {
    stageBadge.textContent = "Flowering (Critical Sensitivity)";
    stageBadge.style.color = "#f87171";
  } else if (cropStage === "Vegetative") {
    stageBadge.textContent = "Vegetative Growth Phase";
    stageBadge.style.color = "#34d399";
  } else {
    stageBadge.textContent = "Maturity / Ripening Phase";
    stageBadge.style.color = "#38bdf8";
  }

  // Agronomic Thresholds
  let threshold = 23.0;
  if (cropStage === "Flowering") threshold = 27.0;
  if (cropStage === "Maturity") threshold = 20.0;

  // Decision Tree Logic
  const isMoistureDeficit = moisture < threshold;
  const isRainActive = rain >= 3.0;
  const shouldIrrigate = isMoistureDeficit && !isRainActive;

  // Update Hero Banner
  const heroBanner = document.getElementById("decisionHeroBanner");
  const heroIcon = document.getElementById("decisionIcon");
  const headline = document.getElementById("decisionHeadline");
  const subheadline = document.getElementById("decisionSubheadline");
  const urgencyPill = document.getElementById("decisionUrgencyPill");

  if (shouldIrrigate) {
    heroBanner.classList.remove("standby");
    heroIcon.textContent = "💧";
    headline.textContent = "IRRIGATE NOW";
    if (cropStage === "Flowering") {
      subheadline.textContent = `Flowering deficit: Moisture (${moisture.toFixed(1)}%) is below safe 27.0% threshold.`;
      urgencyPill.textContent = "CRITICAL PRIORITY";
    } else {
      subheadline.textContent = `Moisture (${moisture.toFixed(1)}%) is below stage threshold (${threshold.toFixed(1)}%).`;
      urgencyPill.textContent = "RECOMMENDED";
    }
  } else {
    heroBanner.classList.add("standby");
    heroIcon.textContent = "🌿";
    headline.textContent = "STANDBY / DO NOT IRRIGATE";
    if (isRainActive) {
      subheadline.textContent = `Rainfall (${rain.toFixed(1)} mm) active: Automated pump lockout active to conserve water.`;
      urgencyPill.textContent = "RAIN LOCKOUT";
    } else {
      subheadline.textContent = `Soil moisture (${moisture.toFixed(1)}%) is adequate for ${cropStage} stage (Threshold: ${threshold.toFixed(1)}%).`;
      urgencyPill.textContent = "WATER CONSERVED";
    }
  }

  // Update Logic Pipeline Steps
  document.getElementById("stepStageVal").textContent = `${cropStage} (<${threshold.toFixed(1)}%)`;
  document.getElementById("stepMoistureVal").textContent = `${moisture.toFixed(1)}% ${isMoistureDeficit ? "< " + threshold.toFixed(1) + "% (Deficit)" : ">= " + threshold.toFixed(1) + "% (OK)"}`;
  document.getElementById("stepRainVal").textContent = `${rain.toFixed(1)} mm ${isRainActive ? ">= 3.0 mm (Lockout)" : "< 3.0 mm (Clear)"}`;
  
  const stepOutcomeVal = document.getElementById("stepOutcomeVal");
  if (shouldIrrigate) {
    stepOutcomeVal.textContent = "Trigger Pump (1)";
    stepOutcomeVal.className = "step-val text-red";
  } else {
    stepOutcomeVal.textContent = "Standby / Lockout (0)";
    stepOutcomeVal.className = "step-val text-emerald";
  }
}

// --------------------------------------------------------------------------
// MODULE 2: MULTI-FARM TELEMETRY & 90-DAY SCRUBBING
// --------------------------------------------------------------------------
async function loadFarmData() {
  try {
    const res = await fetch("data/farm_data.json");
    if (res.ok) {
      farmDataStore = await res.json();
      console.log("Farm data loaded successfully from JSON.");
    } else {
      throw new Error("Local JSON fetch failed");
    }
  } catch (err) {
    console.warn("Using built-in dynamic telemetry generator for standalone mode.");
    farmDataStore = generateClientSideFarmData();
  }
}

function generateClientSideFarmData() {
  // Generates 12 farms × 180 slots matching simulation
  const farms = {};
  const farmIds = Array.from({ length: 12 }, (_, i) => `Farm_${String(i + 1).padStart(2, "0")}`);
  
  farmIds.forEach((fId, fIdx) => {
    let moisture = 30.0 + (fIdx % 3) * 2;
    const records = [];
    const interval = fIdx < 4 ? 3 : (fIdx < 8 ? 2 : 4);

    for (let day = 0; day < 90; day++) {
      let stage = day < 30 ? "Vegetative" : (day < 65 ? "Flowering" : "Maturity");
      let baseRain = [5, 12, 19, 27, 33, 58, 64, 71, 77, 82, 87].includes(day) ? (15 + (day % 7) * 3) : 0;
      
      ["08:00", "17:00"].forEach((slot, sIdx) => {
        let temp = 26 + 6 * Math.sin(day / 28) + (sIdx === 1 ? 4.5 : -4.2) + (day > 35 && day < 53 ? 3.5 : 0);
        let hum = Math.max(25, Math.min(85, 70 - (temp - 22) * 1.6));
        let slotRain = baseRain > 0 ? (sIdx === 0 ? baseRain * 0.45 : baseRain * 0.55) : 0;
        
        let irrigate = (day % interval === 0 && sIdx === (fIdx % 2)) ? 1 : 0;
        let thresh = stage === "Flowering" ? 27.0 : (stage === "Vegetative" ? 23.0 : 20.0);
        let smartIrr = (moisture < thresh && slotRain < 3.0) ? "Irrigate" : "Do Not Irrigate";
        
        let outcome = "Optimal";
        if (moisture < (stage === "Flowering" ? 24.0 : 18.0)) outcome = "Stressed";
        else if (moisture > 40.0 || moisture < thresh) outcome = "Moderate";
        
        records.push({
          Date_Str: `2024-${String(Math.floor(day/30) + 5).padStart(2, '0')}-${String((day % 30) + 1).padStart(2, '0')}`,
          Time_Slot: slot,
          Soil_Moisture: parseFloat(moisture.toFixed(1)),
          Temperature: parseFloat(temp.toFixed(1)),
          Humidity: parseFloat(hum.toFixed(1)),
          Rainfall: parseFloat(slotRain.toFixed(1)),
          Crop_Stage: stage,
          Irrigation_Status: irrigate ? "Irrigated" : "Not Irrigated",
          Crop_Outcome: outcome,
          Smart_Recommendation: smartIrr
        });

        // Evolve moisture
        let recharge = slotRain * 0.45 + (irrigate ? 7.5 : 0);
        let et = Math.max(0.4, (0.045 * temp - 0.015 * hum + 0.6) * (stage === "Flowering" ? 1.35 : 0.95));
        moisture = Math.max(11.5, Math.min(45.0, moisture + recharge - et));
      });
    }

    farms[fId] = { records: records };
  });

  return { farms: farms, global_summary: FALLBACK_GLOBAL_DATA };
}

function initFarmTelemetry() {
  const farmRow = document.getElementById("farmSelectorRow");
  if (!farmRow || !farmDataStore) return;

  farmRow.innerHTML = "";
  Object.keys(farmDataStore.farms).forEach((fId, idx) => {
    const btn = document.createElement("button");
    btn.className = `farm-pill-btn ${idx === 0 ? "active" : ""}`;
    btn.textContent = fId;
    btn.addEventListener("click", () => {
      document.querySelectorAll(".farm-pill-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedFarmId = fId;
      updateFarmTelemetryView();
    });
    farmRow.appendChild(btn);
  });

  const scrubber = document.getElementById("timelineScrubber");
  scrubber.addEventListener("input", (e) => {
    selectedDayIndex = parseInt(e.target.value);
    updateFarmTelemetryView();
  });

  updateFarmTelemetryView();
}

function updateFarmTelemetryView() {
  if (!farmDataStore || !farmDataStore.farms[selectedFarmId]) return;

  const farm = farmDataStore.farms[selectedFarmId];
  const record = farm.records[selectedDayIndex] || farm.records[0];

  // Update Scrubber Date Label
  const dayNum = Math.floor(selectedDayIndex / 2) + 1;
  document.getElementById("scrubberDateDisp").textContent = 
    `Day ${dayNum} / 90 — ${record.Date_Str} (${record.Time_Slot} ${record.Time_Slot === "08:00" ? "Morning" : "Evening"})`;

  // Update Radial Moisture Gauge
  const moisture = record.Soil_Moisture;
  document.getElementById("telemetryMoistureNum").textContent = moisture.toFixed(1) + "%";
  
  const moistureStatus = document.getElementById("telemetryMoistureStatus");
  const gaugeBar = document.getElementById("gaugeMoistureBar");
  
  // Circumference = 2 * PI * 65 ≈ 408.4
  const circumference = 408.4;
  const progress = Math.min(1, moisture / 50.0);
  const offset = circumference - (progress * circumference);
  gaugeBar.style.strokeDashoffset = offset;

  if (moisture < 24.0) {
    gaugeBar.style.stroke = "#ef4444";
    moistureStatus.textContent = "Water Stress (<24%)";
    moistureStatus.style.color = "#f87171";
  } else if (moisture > 40.0) {
    gaugeBar.style.stroke = "#38bdf8";
    moistureStatus.textContent = "Saturated (>40%)";
    moistureStatus.style.color = "#38bdf8";
  } else {
    gaugeBar.style.stroke = "#10b981";
    moistureStatus.textContent = "Optimal Zone";
    moistureStatus.style.color = "#34d399";
  }

  // Update Microclimate & Rain
  document.getElementById("telemetryTempNum").textContent = record.Temperature.toFixed(1) + " °C";
  document.getElementById("telemetryHumNum").textContent = record.Humidity.toFixed(1) + "%";
  document.getElementById("telemetryRainNum").textContent = record.Rainfall.toFixed(1) + " mm";
  document.getElementById("telemetryStageNum").textContent = record.Crop_Stage;

  const rainlockStatus = document.getElementById("telemetryRainlockStatus");
  if (record.Rainfall >= 3.0) {
    rainlockStatus.textContent = "Lockout Active (>=3mm Rain)";
    rainlockStatus.className = "evapo-status text-amber";
  } else {
    rainlockStatus.textContent = "Clear (No Lockout)";
    rainlockStatus.className = "evapo-status text-emerald";
  }

  // Render Farm Timeline Chart
  renderFarmTimelineChart(farm.records);
}

function renderFarmTimelineChart(records) {
  const ctx = document.getElementById("farmTimelineChart");
  if (!ctx) return;

  if (chartInstances.farmTimeline) {
    chartInstances.farmTimeline.destroy();
  }

  const labels = records.map((r, i) => i % 10 === 0 ? `D${Math.floor(i/2)+1}` : "");
  const moistureData = records.map(r => r.Soil_Moisture);
  const rainData = records.map(r => r.Rainfall);

  chartInstances.farmTimeline = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Soil Moisture (%)",
          data: moistureData,
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          borderWidth: 2,
          tension: 0.3,
          fill: true,
          pointRadius: 0,
          yAxisID: "y"
        },
        {
          type: "bar",
          label: "Rainfall (mm)",
          data: rainData,
          backgroundColor: "rgba(56, 189, 248, 0.6)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: "#cbd5e1", font: { size: 11 } } }
      },
      scales: {
        x: { ticks: { color: "#94a3b8", maxTicksLimit: 15 }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: {
          min: 10,
          max: 50,
          title: { display: true, text: "Soil Moisture (%)", color: "#10b981" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255,255,255,0.05)" }
        },
        y1: {
          position: "right",
          min: 0,
          max: 30,
          title: { display: true, text: "Rainfall (mm)", color: "#38bdf8" },
          ticks: { color: "#94a3b8" },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

// --------------------------------------------------------------------------
// MODULE 3: CHALLENGE VISUALIZATIONS (4 PRIMARY CHARTS)
// --------------------------------------------------------------------------
function initChallengeVisualizations() {
  renderChartViz1();
  renderChartViz2();
  renderChartViz3();
  renderChartViz4();
}

function renderChartViz1() {
  const ctx = document.getElementById("chartViz1");
  if (!ctx) return;

  // 90-day macro moisture trend
  const days = Array.from({ length: 90 }, (_, i) => `Day ${i + 1}`);
  const avgMoisture = days.map((_, day) => {
    let base = 41.4 - (day > 28 && day < 65 ? 10.5 : (day >= 65 ? 0.2 : 0));
    return parseFloat((base + 2.5 * Math.sin(day / 5)).toFixed(1));
  });

  chartInstances.viz1 = new Chart(ctx, {
    type: "line",
    data: {
      labels: days,
      datasets: [
        {
          label: "Daily Mean Moisture (%)",
          data: avgMoisture,
          borderColor: "#34d399",
          backgroundColor: "rgba(52, 211, 153, 0.15)",
          borderWidth: 2.5,
          fill: true,
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: "Flowering Stress Threshold (24%)",
          data: Array(90).fill(24.0),
          borderColor: "#ef4444",
          borderDash: [6, 4],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        },
        {
          label: "Adequate Level (30%)",
          data: Array(90).fill(30.0),
          borderColor: "#38bdf8",
          borderDash: [3, 3],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#e2e8f0", font: { size: 10 } } } },
      scales: {
        x: { ticks: { color: "#94a3b8", maxTicksLimit: 10 }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { min: 10, max: 48, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      }
    }
  });
}

function renderChartViz2() {
  const ctx = document.getElementById("chartViz2");
  if (!ctx) return;

  // Rainfall vs Soil Moisture Scatter
  const scatterData = [];
  for (let i = 0; i < 150; i++) {
    let rain = Math.random() < 0.8 ? 0 : Math.random() * 16;
    let moisture = rain > 5 ? 38 + Math.random() * 7 : (13 + Math.random() * 30);
    scatterData.push({ x: parseFloat(rain.toFixed(1)), y: parseFloat(moisture.toFixed(1)) });
  }

  chartInstances.viz2 = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Sensor Observations",
          data: scatterData,
          backgroundColor: "rgba(6, 182, 212, 0.7)",
          borderColor: "#06b6d4",
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: { title: { display: true, text: "Rainfall (mm)", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { title: { display: true, text: "Soil Moisture (%)", color: "#94a3b8" }, min: 10, max: 48, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      }
    }
  });
}

function renderChartViz3() {
  const ctx = document.getElementById("chartViz3");
  if (!ctx) return;

  // Unnecessary vs Justified bar chart
  chartInstances.viz3 = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Vegetative", "Flowering", "Maturity"],
      datasets: [
        {
          label: "Potentially Unnecessary (>=30% or Rain)",
          data: [133, 109, 115],
          backgroundColor: "#fb923c",
          borderColor: "#f97316",
          borderWidth: 1
        },
        {
          label: "Justified (Deficit)",
          data: [11, 64, 6],
          backgroundColor: "#34d399",
          borderColor: "#10b981",
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { stacked: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      },
      plugins: { legend: { labels: { color: "#e2e8f0" } } }
    }
  });
}

function renderChartViz4() {
  const ctx = document.getElementById("chartViz4");
  if (!ctx) return;

  // Stage vulnerability outcome breakdown
  chartInstances.viz4 = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Vegetative", "Flowering", "Maturity"],
      datasets: [
        {
          label: "Optimal (%)",
          data: [18.2, 7.6, 21.0],
          backgroundColor: "#34d399"
        },
        {
          label: "Moderate (%)",
          data: [81.8, 63.1, 79.0],
          backgroundColor: "#38bdf8"
        },
        {
          label: "Stressed (%)",
          data: [0.0, 29.3, 0.0],
          backgroundColor: "#f87171"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { stacked: true, max: 100, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      },
      plugins: { legend: { labels: { color: "#e2e8f0" } } }
    }
  });
}

// --------------------------------------------------------------------------
// MODULE 4: 7 KEY INSIGHTS ACCORDION
// --------------------------------------------------------------------------
function renderInsightsList() {
  const container = document.getElementById("insightsList");
  if (!container) return;

  container.innerHTML = "";
  KEY_INSIGHTS.forEach((ins, idx) => {
    const item = document.createElement("div");
    item.className = "insight-item";
    item.innerHTML = `
      <div class="insight-header-row" onclick="toggleInsight(this)">
        <div class="insight-title-group">
          <span class="insight-num-badge">Insight ${ins.num}</span>
          <span class="insight-headline">${ins.title}</span>
        </div>
        <span class="insight-toggle-icon">▼</span>
      </div>
      <div class="insight-body-content" style="${idx === 0 ? 'display:grid;' : 'display:none;'}">
        <div class="insight-block">
          <div class="insight-block-label">Calculated Evidence</div>
          <p>${ins.evidence}</p>
        </div>
        <div class="insight-block">
          <div class="insight-block-label">Agronomic Interpretation</div>
          <p>${ins.interpretation}</p>
        </div>
        <div class="insight-block">
          <div class="insight-block-label">Practical Implication</div>
          <p>${ins.implication}</p>
        </div>
      </div>
    `;
    container.appendChild(item);
  });
}

window.toggleInsight = function(headerEl) {
  const body = headerEl.nextElementSibling;
  const icon = headerEl.querySelector(".insight-toggle-icon");
  if (body.style.display === "none" || !body.style.display) {
    body.style.display = "grid";
    icon.textContent = "▲";
  } else {
    body.style.display = "none";
    icon.textContent = "▼";
  }
};

// --------------------------------------------------------------------------
// MODULE 5: ROI & WATER SAVINGS CALCULATOR
// --------------------------------------------------------------------------
function initCalculator() {
  const acresSlider = document.getElementById("calcAcres");
  const pumpRateSlider = document.getElementById("calcPumpRate");
  const tariffSlider = document.getElementById("calcTariff");
  const powerSlider = document.getElementById("calcPumpPower");

  [acresSlider, pumpRateSlider, tariffSlider, powerSlider].forEach(s => {
    s.addEventListener("input", updateCalculations);
  });

  updateCalculations();
}

function updateCalculations() {
  const acres = parseFloat(document.getElementById("calcAcres").value);
  const flowRate = parseFloat(document.getElementById("calcPumpRate").value); // L/min
  const tariff = parseFloat(document.getElementById("calcTariff").value); // $/kWh
  const hp = parseFloat(document.getElementById("calcPumpPower").value);
  const kw = hp * 0.7457;

  // Displays
  document.getElementById("dispCalcAcres").textContent = `${acres} Acres`;
  document.getElementById("dispCalcPumpRate").textContent = `${flowRate} L/min`;
  document.getElementById("dispCalcTariff").textContent = `$${tariff.toFixed(2)}`;
  document.getElementById("dispCalcPumpPower").textContent = `${hp.toFixed(1)} HP (${kw.toFixed(1)} kW)`;

  // Calculations:
  // Baseline: Fixed schedule triggers ~36.5 irrigations per farm per season
  // Smart eliminates 12.75 unnecessary cycles (34.9% savings)
  // Average irrigation cycle length = 4.8 hours
  const cyclesSaved = 12.75;
  const hoursPerCycle = 4.8 * (acres / 25.0);
  const totalHoursSaved = cyclesSaved * hoursPerCycle;
  
  // Total Liters = hours * 60 min * flowRate
  const totalLiters = totalHoursSaved * 60 * flowRate;
  
  // Energy saved = hours * kW
  const totalKwh = totalHoursSaved * kw;
  const costSaved = totalKwh * tariff;
  
  // CO2 saved: 0.85 kg CO2 / kWh
  const co2Saved = totalKwh * 0.85;

  document.getElementById("calcWaterSavedLiters").textContent = `${Math.round(totalLiters).toLocaleString()} L`;
  document.getElementById("calcPumpHoursSaved").textContent = `${totalHoursSaved.toFixed(1)} Hours`;
  document.getElementById("calcCostSavedDollar").textContent = `$${costSaved.toFixed(2)}`;
  document.getElementById("calcCarbonSavedKg").textContent = `${Math.round(co2Saved).toLocaleString()} kg`;
}

// --------------------------------------------------------------------------
// MODULE 6: EXPORT PROJECT REPORT
// --------------------------------------------------------------------------
function initActionPlanExport() {
  const btn = document.getElementById("btnDownloadReport");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const reportText = `# SMART AGRICULTURE IRRIGATION DECISION SYSTEM (DS_Day01_33)
===================================================================
Project Summary & Key Findings Report
Generated: ${new Date().toLocaleDateString()}

1. DATASET OVERVIEW
- Monitored Farms: 12 Farms across 90-Day Summer Season (2,160 Records)
- Clean Quality: 0 Missing Values, 0 Duplicates, All Ranges Validated
- Synthetic Dataset Disclosure: Generated based on challenge schema and physical soil dynamics.

2. EXPLORATORY DATA ANALYSIS (EDA) HIGHLIGHTS
- Historical Fixed-Schedule Waste: 357 / 438 Irrigations (81.51%) were potentially unnecessary.
- Water Stress Vulnerability: 100% of all 246 stressed records occurred during the Flowering stage (29.29% stage stress rate).
- Critical Stress Threshold: Soil Moisture < 24.0% with high ambient temperatures (>33°C).
- Rainfall Blindness: 15.91% of time slots with heavy rain (>5mm) still triggered calendar irrigation.

3. MACHINE LEARNING DECISION TREE
- Target: Irrigation_Recommendation (1 = Irrigate, 0 = Do Not Irrigate)
- Test Performance: Accuracy 1.0000, Precision 1.0000, Recall 1.0000, F1 1.0000
- Feature Importances:
  * Soil_Moisture: 79.33%
  * Stage_Flowering: 11.71%
  * Rainfall: 8.96%

4. 5-STEP ACTION PLAN
Phase 1: Pre-irrigation root-zone moisture & rain gauge check.
Phase 2: Stage-aware dynamic thresholds (Flowering: <27%, Vegetative: <23%, Maturity: <20%).
Phase 3: 24-hour pump lockout following >=3.0mm rainfall.
Phase 4: Twice-daily telemetry logging (08:00 & 17:00).
Phase 5: LoRaWAN capacitance probe deployment & 24h weather API integration.

===================================================================
AgriSense AI — Data Science Challenge DS_Day01_33
`;

    const blob = new Blob([reportText], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "DS_Day01_33_Smart_Agriculture_Executive_Report.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}
