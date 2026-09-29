const data = JSON.parse(document.getElementById("dashboard-data").textContent);

const palette = ["#2e5aac", "#5b8def", "#7fb0ff", "#b7791f", "#c0392b", "#27ae60"];

Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
Chart.defaults.color = "#6b7488";

new Chart(document.getElementById("chartMonthly"), {
  type: "line",
  data: {
    labels: data.monthly_revenue.map((r) => r.month),
    datasets: [
      {
        label: "Revenue (EUR)",
        data: data.monthly_revenue.map((r) => r.revenue),
        borderColor: "#2e5aac",
        backgroundColor: "rgba(46, 90, 172, 0.12)",
        fill: true,
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  },
});

new Chart(document.getElementById("chartTopProducts"), {
  type: "bar",
  data: {
    labels: data.top_products.map((r) => r.product),
    datasets: [
      {
        label: "Revenue (EUR)",
        data: data.top_products.map((r) => r.revenue),
        backgroundColor: "#5b8def",
        borderRadius: 6,
      },
    ],
  },
  options: {
    indexAxis: "y",
    plugins: { legend: { display: false } },
    scales: { x: { beginAtZero: true } },
  },
});

new Chart(document.getElementById("chartStatus"), {
  type: "doughnut",
  data: {
    labels: data.orders_by_status.map((r) => r.status),
    datasets: [
      {
        data: data.orders_by_status.map((r) => r.n),
        backgroundColor: palette,
      },
    ],
  },
  options: {
    plugins: { legend: { position: "bottom" } },
  },
});

new Chart(document.getElementById("chartRegion"), {
  type: "bar",
  data: {
    labels: data.revenue_by_region.map((r) => r.region),
    datasets: [
      {
        label: "Revenue (EUR)",
        data: data.revenue_by_region.map((r) => r.revenue),
        backgroundColor: "#2e5aac",
        borderRadius: 6,
      },
    ],
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  },
});
