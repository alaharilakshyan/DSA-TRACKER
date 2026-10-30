/**
 * Smart DSA Tracker — Chart.js Visualizations
 * Handles rendering and dynamic theme adaptation for dashboard charts.
 */

(function () {
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

  function getJsonData(id, fallback) {
    try {
      const el = document.getElementById(id);
      if (el && el.textContent) {
        return JSON.parse(el.textContent);
      }
    } catch (e) {
      // fallback
    }
    return fallback;
  }

  function initCharts() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js library is not loaded. Skipping chart rendering.');
      return;
    }

    const topicLabels = (window.TOPIC_LABELS && window.TOPIC_LABELS.length > 0) ? window.TOPIC_LABELS : getJsonData('topic-labels-data', []);
    const topicTotals = (window.TOPIC_TOTALS && window.TOPIC_TOTALS.length > 0) ? window.TOPIC_TOTALS : getJsonData('topic-totals-data', []);
    const topicMastered = (window.TOPIC_MASTERED && window.TOPIC_MASTERED.length > 0) ? window.TOPIC_MASTERED : getJsonData('topic-mastered-data', []);
    const diffCounts = (window.DIFF_COUNTS && window.DIFF_COUNTS.length > 0) ? window.DIFF_COUNTS : getJsonData('diff-counts-data', [0, 0, 0]);
    const patternLabels = (window.PATTERN_LABELS && window.PATTERN_LABELS.length > 0) ? window.PATTERN_LABELS : getJsonData('pattern-labels-data', []);
    const patternAvgTimes = (window.PATTERN_AVG_TIMES && window.PATTERN_AVG_TIMES.length > 0) ? window.PATTERN_AVG_TIMES : getJsonData('pattern-avg-times-data', []);

    // Expose on window for diagnostics & debugging
    window.TOPIC_LABELS = topicLabels;
    window.TOPIC_TOTALS = topicTotals;
    window.TOPIC_MASTERED = topicMastered;
    window.DIFF_COUNTS = diffCounts;
    window.PATTERN_LABELS = patternLabels;
    window.PATTERN_AVG_TIMES = patternAvgTimes;

    // 1. Topic Progress Bar Chart
    const topicCanvas = document.getElementById('topicChart');
    if (topicCanvas && topicLabels && topicLabels.length > 0) {
      const colors = getThemeColors();
      const ctx = topicCanvas.getContext('2d');

      topicChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: topicLabels,
          datasets: [
            {
              label: 'Total Solved',
              data: topicTotals,
              backgroundColor: colors.primarySubtle,
              borderColor: colors.primary,
              borderWidth: 1.5,
              borderRadius: 6,
            },
            {
              label: 'Mastered ⭐',
              data: topicMastered,
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
              ticks: {
                color: colors.textColor,
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                maxRotation: 45,
                minRotation: 20,
                autoSkip: true,
                maxTicksLimit: 12,
              },
            },
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                precision: 0,
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
    if (diffCanvas && diffCounts && diffCounts.some(c => c > 0)) {
      const colors = getThemeColors();
      const ctx = diffCanvas.getContext('2d');

      diffChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Easy', 'Medium', 'Hard'],
          datasets: [
            {
              data: diffCounts,
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
    if (patternCanvas && patternLabels && patternLabels.length > 0) {
      const colors = getThemeColors();
      const ctx = patternCanvas.getContext('2d');

      patternChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: patternLabels,
          datasets: [
            {
              label: 'Avg Minutes to Solve',
              data: patternAvgTimes,
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
              ticks: {
                color: colors.textColor,
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                autoSkip: false,
              },
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCharts);
  } else {
    initCharts();
  }
})();
