//datos del periodo enviados desde la vista
const stadisticsData = JSON.parse(
    document.getElementById("stadistics-data").textContent
);

//colores del tema de la aplicacion
const CHART_COLORS = [
    "#910BBD",
    "#F2EA4E",
    "#3FA355",
    "#E65353",
    "#800AAC",
    "#E1D93D",
    "#D54242",
    "#2E9244"
];

//estilos globales de las graficas
Chart.defaults.font.family = "Arial, Helvetica, sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = "#333333";

//opciones compartidas por las graficas de pastel
const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: "bottom",
            labels: {
                padding: 12,
                boxWidth: 14
            }
        }
    }
};

//dibujar una grafica de pastel
function renderPie(canvasId, data, colors) {
    const canvas = document.getElementById(canvasId);

    //validar que existan datos en el periodo
    const total = data.values.reduce((sum, value) => sum + value, 0);
    if (!total) {
        canvas.parentElement.innerHTML =
            '<p class="chart-empty">Sin datos para el periodo</p>';
        return;
    }

    new Chart(canvas, {
        type: "pie",
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: colors,
                borderColor: "#DDDDDD",
                borderWidth: 2
            }]
        },
        options: {
            ...pieOptions,
            plugins: {
                ...pieOptions.plugins,
                tooltip: {
                    callbacks: {
                        //mostrar el total y su porcentaje
                        label: (context) => {
                            const percentage = Math.round(
                                (context.parsed / total) * 100
                            );
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

//dibujar la grafica de pastel de tipos de turista
renderPie(
    "touristTypeChart",
    stadisticsData.tourist_types,
    CHART_COLORS
);

//dibujar la grafica de pastel de tipos de habitacion
renderPie(
    "roomTypeChart",
    stadisticsData.room_types,
    CHART_COLORS
);

//dibujar la grafica de pastel de estados de reserva
renderPie(
    "bookingStateChart",
    stadisticsData.booking_states,
    ["#E65353", "#3FA355"]
);

//dibujar la grafica de barras de reservas por dia
new Chart(document.getElementById("bookingsPerDayChart"), {
    type: "bar",
    data: {
        labels: stadisticsData.bookings_per_day.labels,
        datasets: [{
            label: "Reservas",
            data: stadisticsData.bookings_per_day.values,
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
                title: {
                    display: true,
                    text: "Dia del mes"
                },
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                },
                title: {
                    display: true,
                    text: "Reservas"
                }
            }
        }
    }
});
