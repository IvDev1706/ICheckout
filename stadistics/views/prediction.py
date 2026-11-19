from datetime import date
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View
from ..constants import MONTHS
from ..models import ClusterRun, ForecastRun

#vista del apartado de prediccion y deteccion
class PredictionView(View):
    #atributos
    template_name = "prediction.html"

    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #ultima ejecucion guardada de cada calculo
        forecast = ForecastRun.objects.first()
        clusters = ClusterRun.objects.first()

        #preparar contexto
        context = {
            "title": "ICheckout - Predicción y detección",
            "subtitle": "ICheckout - Predicción y detección",
            "forecast": forecast,
            "cluster_run": clusters,
            "groups": self._group_rows(clusters),
            "chart_data": self._chart_data(forecast, clusters),
        }

        #retorno de plantilla
        return render(request, self.template_name, context)

    #etiqueta de un periodo mensual
    def _label(self, day:date) -> str:
        return f"{MONTHS[day.month - 1]} {day.year}"

    #series para las graficas del apartado
    def _chart_data(self, forecast:ForecastRun, clusters:ClusterRun):
        return {
            "forecast": self._forecast_data(forecast),
            "clusters": self._cluster_data(clusters),
        }

    #serie historica y prediccion con su banda de confianza
    def _forecast_data(self, forecast:ForecastRun):
        #sin ejecucion no hay serie
        if forecast is None:
            return {
                "labels": [],
                "history": [],
                "future": [],
                "lower": [],
                "upper": [],
            }

        #separar puntos historicos y futuros
        points = list(forecast.points.all())
        history = [point for point in points if not point.is_future]
        future = [point for point in points if point.is_future]

        #valores de cada tramo
        labels = [self._label(point.period) for point in points]
        history_values = [point.value for point in history]
        future_values = [point.value for point in future]

        #historial con huecos en los meses futuros
        history_series = history_values + [None] * len(future)

        #prediccion enlazada con el ultimo punto del historial
        if history_values:
            future_series = [None] * (len(history_values) - 1)
            future_series.append(history_values[-1])
            future_series += future_values
        else:
            future_series = [None] * len(future)

        #banda de confianza solo para los meses futuros
        lower = [None] * len(history_values) + [point.lower for point in future]
        upper = [None] * len(history_values) + [point.upper for point in future]

        return {
            "labels": labels,
            "history": history_series,
            "future": future_series,
            "lower": lower,
            "upper": upper,
        }

    #filas de los patrones detectados
    def _group_rows(self, clusters:ClusterRun):
        #sin ejecucion no hay grupos
        if clusters is None:
            return []

        return [{
            "label": group.label,
            "size": group.size,
            "utilization": round(group.avg_utilization * 100, 2),
            "revenue": round(group.avg_revenue, 2),
            "bookings": round(group.avg_bookings, 2),
            "guests": round(group.avg_guests, 2),
        } for group in clusters.groups.all()]

    #series para las graficas de los patrones
    def _cluster_data(self, clusters:ClusterRun):
        rows = self._group_rows(clusters)

        return {
            "labels": [row["label"] for row in rows],
            "sizes": [row["size"] for row in rows],
            "utilization": [row["utilization"] for row in rows],
            "revenue": [row["revenue"] for row in rows],
        }
