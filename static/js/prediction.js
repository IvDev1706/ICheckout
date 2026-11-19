//datos pre-calculados enviados desde la vista
const predictionData = JSON.parse(
    document.getElementById("prediction-data").textContent
);

//estilos globales de las graficas
Chart.defaults.font.family = "Arial, Helvetica, sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = "#333333";

//dibujar el historial, la prediccion y su banda de confianza
function renderForecast(data) {
    const canvas = document.getElementById("forecastChart");

    //validar que exista la grafica y la serie
    if (!canvas || !data.labels.length) {
        return;
    }

    new Chart(canvas, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: "Límite superior",
                    data: data.upper,
                    borderColor: "transparent",
                    backgroundColor: "#910BBD22",
                    pointRadius: 0,
                    fill: "+1"
                },
                {
                    label: "Límite inferior",
                    data: data.lower,
                    borderColor: "transparent",
                    backgroundColor: "#910BBD22",
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: "Historial",
                    data: data.history,
                    borderColor: "#910BBD",
                    backgroundColor: "#910BBD",
                    pointRadius: 2,
                    tension: 0.25,
                    fill: false
                },
                {
                    label: "Predicción",
                    data: data.future,
                    borderColor: "#3FA355",
                    backgroundColor: "#3FA355",
                    borderDash: [6, 4],
                    pointRadius: 3,
                    tension: 0.25,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            spanGaps: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        padding: 12,
                        boxWidth: 14
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Reservas"
                    }
                }
            }
        }
    });
}

//dibujar una grafica de barras de los patrones
function renderBars(canvasId, labels, values, label, yTitle) {
    const canvas = document.getElementById(canvasId);

    //validar que exista la grafica y los grupos
    if (!canvas || !labels.length) {
        return;
    }

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: "#910BBD",
                hoverBackgroundColor: "#800AAC",
                borderColor: "#800AAC",
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yTitle
                    }
                }
            }
        }
    });
}

//grafica del historial y la prediccion de reservas
renderForecast(predictionData.forecast);

//graficas de los patrones detectados
renderBars(
    "clusterSizeChart",
    predictionData.clusters.labels,
    predictionData.clusters.sizes,
    "Habitaciones",
    "Habitaciones"
);

renderBars(
    "clusterUtilizationChart",
    predictionData.clusters.labels,
    predictionData.clusters.utilization,
    "Ocupación promedio",
    "Ocupación (%)"
);
