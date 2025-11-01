if __name__ == "__main__":
    # Extraer datos
    extractor = YahooFinanceExtractor()
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    data = extractor.get_multiple_symbols(
        symbols=symbols,
        start_date='2023-01-01',
        end_date='2024-01-01'
    )
    
    # Crear series de precios
    holdings = {
        symbol: PriceSeries(symbol=symbol, data=df, source='yahoo', asset_type='stock')
        for symbol, df in data.items()
    }
    
    # Crear cartera
    portfolio = Portfolio(
        holdings=holdings,
        weights={'AAPL': 0.4, 'MSFT': 0.3, 'GOOGL': 0.3},
        name="Tech Portfolio"
    )
    
    # Generar reporte
    report_gen = MarkdownReportGenerator()
    report = report_gen.generate_portfolio_report(portfolio)
    print(report)
    
    # Simulación Monte Carlo
    portfolio.plot_monte_carlo(n_simulations=1000, n_days=252, initial_investment=10000)