"""
examples/complete_analysis.py

Script completo que demuestra todas las funcionalidades del toolkit.
"""

import sys
sys.path.append('..')

from src.extractors.yahoo_extractor import YahooFinanceExtractor
from src.models.price_series import PriceSeries
from src.models.portfolio import Portfolio
from src.processors.cleaner import DataCleaner
from src.reporting.markdown_generator import MarkdownReportGenerator
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


def main():
    print("=" * 70)
    print("🚀 MARKET ANALYSIS TOOLKIT - Demo Completo")
    print("=" * 70)
    
    # ========================================================================
    # PASO 1: Extracción de Datos
    # ========================================================================
    print("\n📥 PASO 1: Extrayendo datos históricos...")
    
    extractor = YahooFinanceExtractor()
    
    # Símbolos a analizar
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', '^GSPC']  # Incluye S&P 500
    
    # Fechas
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    print(f"Período: {start_date} a {end_date}")
    print(f"Símbolos: {', '.join(symbols)}")
    
    # Descargar datos
    raw_data = extractor.get_multiple_symbols(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"✓ {len(raw_data)} activos descargados correctamente\n")
    
    # ========================================================================
    # PASO 2: Crear Series de Precios
    # ========================================================================
    print("📊 PASO 2: Creando objetos PriceSeries...")
    
    price_series = {}
    for symbol, data in raw_data.items():
        if symbol.startswith('^'):
            asset_type = 'index'
        else:
            asset_type = 'stock'
        
        price_series[symbol] = PriceSeries(
            symbol=symbol,
            data=data,
            source='yahoo',
            asset_type=asset_type
        )
        
        # Mostrar estadísticas básicas
        stats = price_series[symbol].get_stats()
        print(f"  {symbol:6} - Retorno: {stats['total_return']*100:6.2f}% | "
              f"Volatilidad: {stats['volatility']*100:5.2f}% | "
              f"Sharpe: {stats['sharpe_ratio']:5.2f}")
    
    # ========================================================================
    # PASO 3: Limpieza de Datos
    # ========================================================================
    print("\n🧹 PASO 3: Limpieza de datos...")
    
    cleaned_series = {}
    for symbol, series in price_series.items():
        if symbol.startswith('^'):  # Índices normalmente no necesitan limpieza
            cleaned_series[symbol] = series
            continue
        
        # Eliminar outliers
        clean = DataCleaner.remove_outliers(series, method='iqr')
        
        # Rellenar fechas faltantes
        clean = DataCleaner.fill_missing_dates(clean, method='ffill')
        
        cleaned_series[symbol] = clean
        
        original_count = len(series.data)
        clean_count = len(clean.data)
        print(f"  {symbol}: {original_count} → {clean_count} observaciones")
    
    # ========================================================================
    # PASO 4: Crear Cartera
    # ========================================================================
    print("\n💼 PASO 4: Creando cartera de inversión...")
    
    # Separar índice de acciones
    stocks = {k: v for k, v in cleaned_series.items() if not k.startswith('^')}
    
    # Definir pesos (equiponderado)
    n_stocks = len(stocks)
    weights = {symbol: 1/n_stocks for symbol in stocks.keys()}
    
    portfolio = Portfolio(
        holdings=stocks,
        weights=weights,
        name="Tech Portfolio"
    )
    
    print(f"✓ Cartera creada con {len(stocks)} activos")
    print("\nComposición:")
    for symbol, weight in weights.items():
        print(f"  {symbol}: {weight*100:.2f}%")
    
    # Estadísticas de la cartera
    portfolio_stats = portfolio.get_stats()
    print("\nEstadísticas de la Cartera:")
    print(f"  Retorno Anualizado: {portfolio_stats['annualized_return']*100:.2f}%")
    print(f"  Volatilidad Anualizada: {portfolio_stats['annualized_volatility']*100:.2f}%")
    print(f"  Ratio de Sharpe: {portfolio_stats['sharpe_ratio']:.2f}")
    
    # ========================================================================
    # PASO 5: Comparación con Benchmark
    # ========================================================================
    print("\n📈 PASO 5: Comparación con S&P 500...")
    
    if '^GSPC' in price_series:
        sp500 = price_series['^GSPC']
        portfolio_returns = portfolio.get_portfolio_returns()
        sp500_returns = sp500.get_returns()
        
        # Alinear fechas
        comparison = pd.DataFrame({
            'Portfolio': portfolio_returns,
            'S&P 500': sp500_returns
        }).dropna()
        
        # Rendimiento acumulado
        cumulative = (1 + comparison).cumprod()
        
        # Gráfico de comparación
        plt.figure(figsize=(12, 6))
        plt.plot(cumulative.index, cumulative['Portfolio'], 
                label='Tech Portfolio', linewidth=2)
        plt.plot(cumulative.index, cumulative['S&P 500'], 
                label='S&P 500', linewidth=2, linestyle='--')
        plt.title('Rendimiento Acumulado: Portfolio vs S&P 500', fontsize=14, fontweight='bold')
        plt.xlabel('Fecha')
        plt.ylabel('Rendimiento Acumulado')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('portfolio_vs_benchmark.png', dpi=300)
        print("✓ Gráfico guardado: portfolio_vs_benchmark.png")
        
        # Estadísticas comparativas
        portfolio_total = (cumulative['Portfolio'].iloc[-1] - 1) * 100
        sp500_total = (cumulative['S&P 500'].iloc[-1] - 1) * 100
        
        print(f"\nRendimientos Totales:")
        print(f"  Portfolio: {portfolio_total:.2f}%")
        print(f"  S&P 500: {sp500_total:.2f}%")
        print(f"  Diferencia: {portfolio_total - sp500_total:+.2f}%")
    
    # ========================================================================
    # PASO 6: Simulación Monte Carlo
    # ========================================================================
    print("\n🎲 PASO 6: Ejecutando simulación Monte Carlo...")
    
    n_sims = 5000
    n_days = 252  # 1 año
    initial = 10000
    
    print(f"Parámetros:")
    print(f"  - Simulaciones: {n_sims:,}")
    print(f"  - Días: {n_days}")
    print(f"  - Inversión inicial: ${initial:,}")
    
    # Ejecutar simulación
    simulations = portfolio.monte_carlo_simulation(
        n_simulations=n_sims,
        n_days=n_days,
        initial_investment=initial
    )
    
    # Análisis de resultados
    final_values = simulations[:, -1]
    
    print(f"\nResultados:")
    print(f"  Valor esperado: ${final_values.mean():,.2f}")
    print(f"  Mediana: ${np.median(final_values):,.2f}")
    print(f"  Desv. estándar: ${final_values.std():,.2f}")
    print(f"  Valor mínimo: ${final_values.min():,.2f}")
    print(f"  Valor máximo: ${final_values.max():,.2f}")
    print(f"  VaR (5%): ${np.percentile(final_values, 5):,.2f}")
    print(f"  VaR (1%): ${np.percentile(final_values, 1):,.2f}")
    
    prob_loss = (final_values < initial).sum() / n_sims * 100
    prob_double = (final_values >= initial * 2).sum() / n_sims * 100
    
    print(f"\nProbabilidades:")
    print(f"  Pérdida: {prob_loss:.2f}%")
    print(f"  Duplicar inversión: {prob_double:.2f}%")
    
    # Visualización
    portfolio.plot_monte_carlo(
        n_simulations=1000,  # Menos para visualización
        n_days=n_days,
        initial_investment=initial
    )
    
    # ========================================================================
    # PASO 7: Generar Reporte
    # ========================================================================
    print("\n📄 PASO 7: Generando reporte en Markdown...")
    
    report_gen = MarkdownReportGenerator()
    report = report_gen.generate_portfolio_report(portfolio)
    
    # Guardar reporte
    report_filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Reporte guardado: {report_filename}")
    
    # ========================================================================
    # PASO 8: Matriz de Correlación
    # ========================================================================
    print("\n🔗 PASO 8: Análisis de correlaciones...")
    
    # Construir matriz de retornos
    returns_df = pd.DataFrame()
    for symbol, series in stocks.items():
        returns_df[symbol] = series.get_returns()
    
    returns_df = returns_df.dropna()
    
    # Calcular correlación
    corr_matrix = returns_df.corr()
    
    # Visualizar
    plt.figure(figsize=(10, 8))
    import seaborn as sns
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Matriz de Correlación de Retornos', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300)
    print("✓ Matriz de correlación guardada: correlation_matrix.png")
    
    # Mostrar correlaciones más altas
    print("\nCorrelaciones más altas:")
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr = corr_matrix.iloc[i, j]
            if abs(corr) > 0.7:  # Umbral de correlación alta
                print(f"  {corr_matrix.columns[i]} - {corr_matrix.columns[j]}: {corr:.3f}")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 70)
    print("\nArchivos generados:")
    print(f"  1. {report_filename}")
    print("  2. portfolio_vs_benchmark.png")
    print("  3. correlation_matrix.png")
    print("  4. Gráficos de Monte Carlo (mostrados en pantalla)")
    
    print("\n💡 Próximos pasos sugeridos:")
    print("  - Revisar el reporte en Markdown")
    print("  - Ajustar los pesos de la cartera según análisis")
    print("  - Ejecutar simulaciones con diferentes horizontes temporales")
    print("  - Incorporar más activos o clases de activos")
    print("  - Implementar estrategias de rebalanceo")
    
    print("\n¡Gracias por usar Market Analysis Toolkit! 📊\n")


if __name__ == "__main__":
    import numpy as np  # Asegurar importación
    main()