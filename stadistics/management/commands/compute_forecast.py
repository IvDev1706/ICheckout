from datetime import date

import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing

from booking.models import Booking
from stadistics.models import ForecastPoint, ForecastRun

# repeticiones usadas para estimar los intervalos de la prediccion
SIMULATIONS = 300


# primer dia del mes de una fecha
def month_start(day: date) -> date:
    return day.replace(day=1)


# desplazar una fecha por meses conservando el dia primero
def add_months(day: date, months: int) -> date:
    index = (day.year * 12 + day.month - 1) + months
    return date(index // 12, index % 12 + 1, 1)


# redondear cifras de la serie
def rounded(value) -> float:
    return round(float(value), 2)


class Command(BaseCommand):
    help = "Calcula la prediccion mensual de reservas con statsmodels y guarda el resultado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--months",
            type=int,
            default=24,
            help="Meses de historial a considerar (default 24).",
        )
        parser.add_argument(
            "--horizon",
            type=int,
            default=6,
            help="Meses a predecir (default 6).",
        )

    def handle(self, *args, **options):
        months = options["months"]
        horizon = options["horizon"]

        # validar parametros
        if months < 6:
            raise CommandError("Se necesitan al menos 6 meses de historial (--months).")
        if horizon < 1:
            raise CommandError("El horizonte debe ser de al menos 1 mes (--horizon).")

        # periodo del historial (hasta el mes actual)
        today = date.today()
        end_month = month_start(today)
        start_month = add_months(end_month, -(months - 1))

        periods = []
        current = start_month
        while current <= end_month:
            periods.append(current)
            current = add_months(current, 1)

        # contar reservas por mes de llegada
        counts = {}
        arrivals = Booking.objects.filter(
            arrive_date__gte=start_month,
            arrive_date__lte=today,
        ).values_list("arrive_date", flat=True)
        for arrive in arrivals:
            key = month_start(arrive)
            counts[key] = counts.get(key, 0) + 1

        # completar los meses sin reservas con cero
        series = np.array(
            [counts.get(period, 0) for period in periods],
            dtype=float,
        )

        if not series.any():
            raise CommandError("No hay reservas en el periodo para calcular la prediccion.")

        # ajustar el modelo (holtwinters con tendencia amortiguada)
        fitted, model_name = self._fit(series)

        # obtener prediccion, limites y error
        forecast = np.asarray(fitted.forecast(horizon), dtype=float)
        fitted_values = np.asarray(fitted.fittedvalues, dtype=float)
        lower, upper = self._intervals(fitted, series, fitted_values, forecast, horizon)

        residuals = series - fitted_values
        rmse = float(np.sqrt(np.mean(residuals ** 2))) if len(series) else 0.0

        # guardar el resultado reemplazando la ejecucion anterior
        with transaction.atomic():
            ForecastRun.objects.all().delete()
            run = ForecastRun.objects.create(
                model=model_name,
                history_start=periods[0],
                history_end=periods[-1],
                horizon=horizon,
                rmse=round(rmse, 4),
            )

            points = [
                ForecastPoint(
                    run=run,
                    period=period,
                    value=rounded(max(value, 0.0)),
                    is_future=False,
                )
                for period, value in zip(periods, fitted_values)
            ]

            for offset, (value, low, high) in enumerate(
                zip(forecast, lower, upper), start=1
            ):
                points.append(ForecastPoint(
                    run=run,
                    period=add_months(periods[-1], offset),
                    value=rounded(max(value, 0.0)),
                    lower=rounded(max(low, 0.0)),
                    upper=rounded(max(high, 0.0)),
                    is_future=True,
                ))

            ForecastPoint.objects.bulk_create(points)

        # resumen en consola
        self.stdout.write(self.style.SUCCESS("Prediccion calculada correctamente."))
        self.stdout.write(f"  modelo: {model_name}")
        self.stdout.write(f"  historial: {periods[0]:%m/%Y} - {periods[-1]:%m/%Y}")
        self.stdout.write(f"  rmse: {rmse:.2f}")
        for point in run.points.filter(is_future=True):
            self.stdout.write(
                f"  {point.period:%m/%Y}: {point.value:.2f} "
                f"[{point.lower:.2f} - {point.upper:.2f}]"
            )

    # ajustar el modelo de suavizamiento exponencial
    def _fit(self, series: np.ndarray):
        # holtwinters con tendencia amortiguada
        try:
            fitted = ExponentialSmoothing(
                series,
                trend="add",
                damped_trend=True,
                seasonal=None,
                initialization_method="estimated",
            ).fit()
            return fitted, "holt-winters amortiguado"
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"Holt-winters no convergio ({e}); se usa suavizamiento simple."
            ))

        # respaldo: suavizamiento exponencial simple
        fitted = SimpleExpSmoothing(
            series,
            initialization_method="estimated",
        ).fit()
        return fitted, "suavizamiento exponencial simple"

    # estimar los limites inferior y superior de la prediccion
    def _intervals(self, fitted, series, fitted_values, forecast, horizon: int):
        # limites por simulacion de trayectorias del modelo
        try:
            simulations = np.asarray(
                fitted.simulate(
                    nsimulations=horizon,
                    repetitions=SIMULATIONS,
                    error="add",
                ),
                dtype=float,
            )
            if simulations.ndim == 1:
                simulations = simulations.reshape(-1, 1)

            # asegurar la forma (horizonte, repeticiones)
            if simulations.shape[0] != horizon and simulations.shape[1] == horizon:
                simulations = simulations.T
            if simulations.shape[0] != horizon:
                raise ValueError("forma inesperada de las simulaciones")

            lower = np.percentile(simulations, 2.5, axis=1)
            upper = np.percentile(simulations, 97.5, axis=1)
            return lower, upper
        except Exception:
            pass

        # respaldo: desviacion de los residuales que crece con el horizonte
        residuals = series - fitted_values
        sigma = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
        steps = np.arange(1, horizon + 1, dtype=float)
        band = 1.96 * sigma * np.sqrt(steps)
        return forecast - band, forecast + band
