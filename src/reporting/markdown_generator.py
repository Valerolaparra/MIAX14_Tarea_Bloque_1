class MarkdownReportGenerator:
    """Generador de reportes en formato Markdown."""
    
    @staticmethod
    def generate_portfolio_report(portfolio: Portfolio) -> str:
        """Genera un reporte completo de la cartera."""
        report = [
            f"# 📊 Reporte de Cartera: {portfolio.name}",
            f"\n**Fecha de Generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n---\n",
            "## 🎯 Composición de la Cartera\n",
            "| Símbolo | Peso | Tipo |",
            "|---------|------|------|"
        ]
        
        for symbol, weight in portfolio.weights.items():
            asset_type = portfolio.holdings[symbol].asset_type
            report.append(f"| {symbol} | {weight*100:.2f}% | {asset_type} |")
        
        # Estadísticas generales
        stats = portfolio.get_stats()
        report.extend([
            "\n## 📈 Estadísticas de la Cartera\n",
            f"- **Retorno Medio Diario:** {stats['mean_return']*100:.4f}%",
            f"- **Volatilidad Diaria:** {stats['std_return']*100:.4f}%",
            f"- **Ratio de Sharpe:** {stats['sharpe_ratio']:.4f}",
            f"- **Retorno Anualizado:** {stats['annualized_return']*100:.2f}%",
            f"- **Volatilidad Anualizada:** {stats['annualized_volatility']*100:.2f}%",
        ])
        
        # Análisis individual
        report.append("\n## 🔍 Análisis por Activo\n")
        
        for symbol, series in portfolio.holdings.items():
            asset_stats = series.get_stats()
            report.extend([
                f"\n### {symbol}",
                f"- Retorno Total: {asset_stats['total_return']*100:.2f}%",
                f"- Volatilidad: {asset_stats['volatility']*100:.2f}%",
                f"- Sharpe Ratio: {asset_stats['sharpe_ratio']:.4f}",
                f"- Max Drawdown: {asset_stats['max_drawdown']*100:.2f}%",
            ])
        
        # Advertencias
        report.extend([
            "\n## ⚠️ Advertencias y Consideraciones\n",
        ])
        
        # Advertencia por alta volatilidad
        if stats['annualized_volatility'] > 0.3:
            report.append("- ⚠️ **Alta Volatilidad:** La cartera muestra volatilidad superior al 30% anualizado.")
        
        # Advertencia por concentración
        max_weight = max(portfolio.weights.values())
        if max_weight > 0.4:
            report.append(f"- ⚠️ **Concentración:** Un activo representa más del 40% de la cartera.")
        
        return "\n".join(report)