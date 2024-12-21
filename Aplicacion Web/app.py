import os
from flask import Flask, render_template, request, send_file, redirect, url_for
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los datos del formulario
        ticker = request.form['ticker']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Descargar los datos con intervalo mensual
        data = yf.download(ticker, start=start_date,
                           end=end_date, interval='1mo')

        # Verificar que los datos hayan sido descargados correctamente
        if data.empty:
            return render_template('index.html', error="No se pudieron descargar los datos. Verifica el ticker y las fechas.")

        # Calcular el rendimiento mensual
        data['Monthly Return (%)'] = data['Adj Close'].pct_change() * 100
        data = data.dropna(subset=['Monthly Return (%)'])

        # Crear columna de año y mes
        data['Year'] = data.index.year
        data['Month'] = data.index.month

        # Crear tabla pivote
        pivot_table = data.pivot_table(
            values='Monthly Return (%)', index='Year', columns='Month', aggfunc='mean')
        pivot_table = pivot_table.sort_index(axis=1)

        # Asignar nombres de los meses
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot_table.columns = months

        # Crear y guardar el heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, cmap='magma', annot=True,
                    fmt=".2f", linewidths=.5, center=0)
        plt.title(
            f'Rendimiento Mensual del {ticker} de los últimos años', fontsize=14)
        plt.xlabel('Mes')
        plt.ylabel('Año')
        heatmap_path = os.path.join('static', 'heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()

        # Calcular el rendimiento promedio mensual
        monthly_avg_returns = data.groupby(
            'Month')['Monthly Return (%)'].mean()
        monthly_avg_returns.index = months
        # Convertir a diccionario para enviar al HTML
        monthly_avg_returns = monthly_avg_returns.to_dict()

        # Redirigir al gráfico y resultados
        return render_template('index.html', heatmap_url=heatmap_path, monthly_avg_returns=monthly_avg_returns)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
