document.addEventListener("DOMContentLoaded", () => {
  const data = window.dashboardChartData;
  if (!data || typeof Chart === "undefined") return;
  Chart.defaults.font.family = "Inter, Segoe UI, Arial, sans-serif";
  Chart.defaults.color = "#627d98";
  const grid = "rgba(148, 163, 184, 0.18)";
  const dailyCanvas = document.getElementById("dailyChart");
  let dailyChart;
  if (dailyCanvas) {
    const makeDailyChart = (days) => {
      const labels = data.dailyLabels.slice(-days);
      const values = data.dailyValues.slice(-days);
      if (dailyChart) dailyChart.destroy();
      dailyChart = new Chart(dailyCanvas, {
        type: "line",
        data: { labels, datasets: [{ label: "Transactions", data: values, borderColor: "#2563eb", backgroundColor: "rgba(37, 99, 235, .12)", fill: true, tension: .35, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: "index" }, plugins: { legend: { display: false }, tooltip: { displayColors: false } }, scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8, maxRotation: 0 } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } } } }
      });
    };
    makeDailyChart(30);
    const picker = document.getElementById("trendRange");
    if (picker) picker.addEventListener("change", () => makeDailyChart(Number(picker.value)));
  }
  const decisionCanvas = document.getElementById("decisionChart");
  if (decisionCanvas) new Chart(decisionCanvas, {
    type: "doughnut",
    data: { labels: data.decisionLabels, datasets: [{ data: data.decisionValues, backgroundColor: ["#ef4444", "#10b981", "#94a3b8"], borderColor: "#ffffff", borderWidth: 4, hoverOffset: 7 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: "68%", plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } } }
  });
  const channelCanvas = document.getElementById("channelChart");
  if (channelCanvas) new Chart(channelCanvas, {
    type: "bar",
    data: { labels: data.channelLabels, datasets: [{ label: "Suspicious transactions", data: data.channelValues, backgroundColor: "rgba(239, 68, 68, .78)", borderRadius: 7, maxBarThickness: 48 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { displayColors: false } }, scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } } } }
  });
  const merchantCanvas = document.getElementById("merchantChart");
  if (merchantCanvas) new Chart(merchantCanvas, {
    type: "bar",
    data: {
      labels: data.merchantLabels,
      datasets: [{
        label: "Suspicious transactions",
        data: data.merchantValues,
        backgroundColor: "rgba(124, 58, 237, .78)",
        borderRadius: 7,
        maxBarThickness: 38
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { displayColors: false } },
      scales: {
        x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } },
        y: { grid: { display: false } }
      }
    }
  });

});
