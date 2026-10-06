/**
 * Smart DSA Tracker — Chart.js Visualizations
 * Handles rendering and dynamic theme adaptation for dashboard charts.
 */

document.addEventListener('DOMContentLoaded', () => {
  const isDarkMode = () => document.documentElement.getAttribute('data-bs-theme') === 'dark';

  const getThemeColors = () => {
    const dark = isDarkMode();
    return {
      textColor: dark ? '#94a3b8' : '#64748b',
      gridColor: dark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)',
      primary: dark ? '#818cf8' : '#4f46e5',
      primarySubtle: dark ? 'rgba(129, 140, 248, 0.25)' : 'rgba(79, 70, 229, 0.15)',
      success: dark ? '#34d399' : '#059669',
      successSubtle: dark ? 'rgba(52, 211, 153, 0.3)' : 'rgba(5, 150, 105, 0.2)',
      warning: dark ? '#fbbf24' : '#d97706',
      danger: dark ? '#fb7185' : '#e11d48',
    };
  };

  let topicChartInstance = null;
  let diffChartInstance = null;
  let patternChartInstance = null;

  // 1. Topic Progress Bar Chart
  const topicCanvas = document.getElementById('topicChart');
  if (topicCanvas && window.TOPIC_LABELS) {
    const colors = getThemeColors();
    const ctx = topicCanvas.getContext('2d');

    topicChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.TOPIC_LABELS,
        datasets: [
          {
            label: 'Total Solved',
            data: window.TOPIC_TOTALS,
            backgroundColor: colors.primarySubtle,
            borderColor: colors.primary,
            borderWidth: 1.5,
            borderRadius: 6,
          },
          {
            label: 'Mastered ⭐',
            data: window.TOPIC_MASTERED,
            backgroundColor: colors.successSubtle,
            borderColor: colors.success,
            borderWidth: 1.5,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: colors.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            },
          },
          tooltip: {
            padding: 10,
            cornerRadius: 8,
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { family: "'Plus Jakarta Sans', sans-serif" } },
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              color: colors.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif" },
            },
            grid: { color: colors.gridColor },
          },
        },
      },
    });
  }

  // 2. Difficulty Breakdown Doughnut Chart
  const diffCanvas = document.getElementById('difficultyChart');
  if (diffCanvas && window.DIFF_COUNTS) {
    const colors = getThemeColors();
    const ctx = diffCanvas.getContext('2d');

    diffChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Easy', 'Medium', 'Hard'],
        datasets: [
          {
            data: window.DIFF_COUNTS,
            backgroundColor: [colors.success, colors.warning, colors.danger],
            borderWidth: 2,
            borderColor: isDarkMode() ? '#111827' : '#ffffff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: colors.textColor,
              boxWidth: 12,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            },
          },
          tooltip: {
            padding: 10,
            cornerRadius: 8,
          },
        },
        cutout: '70%',
      },
    });
  }

  // 3. Weak Patterns Average Solve Time Chart
  const patternCanvas = document.getElementById('weakPatternChart');
  if (patternCanvas && window.PATTERN_LABELS && window.PATTERN_LABELS.length > 0) {
    const colors = getThemeColors();
    const ctx = patternCanvas.getContext('2d');

    patternChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.PATTERN_LABELS,
        datasets: [
          {
            label: 'Avg Minutes to Solve',
            data: window.PATTERN_AVG_TIMES,
            backgroundColor: 'rgba(244, 63, 94, 0.2)',
            borderColor: colors.danger,
            borderWidth: 1.5,
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Avg Time: ${context.parsed.x} minutes`,
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              color: colors.textColor,
              callback: (v) => `${v}m`,
            },
            grid: { color: colors.gridColor },
          },
          y: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { family: "'Plus Jakarta Sans', sans-serif" } },
          },
        },
      },
    });
  }

  // Dynamic Theme Refresh for Charts
  window.addEventListener('themeChanged', () => {
    const updatedColors = getThemeColors();

    if (topicChartInstance) {
      topicChartInstance.options.scales.x.ticks.color = updatedColors.textColor;
      topicChartInstance.options.scales.y.ticks.color = updatedColors.textColor;
      topicChartInstance.options.scales.y.grid.color = updatedColors.gridColor;
      topicChartInstance.options.plugins.legend.labels.color = updatedColors.textColor;
      topicChartInstance.update();
    }

    if (diffChartInstance) {
      diffChartInstance.data.datasets[0].borderColor = isDarkMode() ? '#111827' : '#ffffff';
      diffChartInstance.options.plugins.legend.labels.color = updatedColors.textColor;
      diffChartInstance.update();
    }

    if (patternChartInstance) {
      patternChartInstance.options.scales.x.ticks.color = updatedColors.textColor;
      patternChartInstance.options.scales.y.ticks.color = updatedColors.textColor;
      patternChartInstance.options.scales.x.grid.color = updatedColors.gridColor;
      patternChartInstance.update();
    }
  });
});
