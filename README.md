README_CONTENT = """
# 📊 Market Analysis Toolkit

Herramienta completa para el análisis de mercados financieros, gestión de carteras y simulaciones de Monte Carlo.

## 🚀 Características

- **Extracción de Datos Multi-Fuente**: Obtén datos de múltiples APIs (Yahoo Finance, Alpha Vantage, etc.)
- **Formato Estandarizado**: Independientemente de la fuente, todos los datos siguen el mismo formato
- **Análisis Estadístico Completo**: Métricas automáticas y personalizables
- **Simulaciones Monte Carlo**: Proyecciones probabilísticas de carteras
- **Reportes Profesionales**: Generación automática de reportes en Markdown
- **Visualizaciones Avanzadas**: Gráficos interactivos y profesionales

## 📦 Instalación

### Instalación Rápida (Plug-n-Play)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/market-analysis-toolkit.git
cd market-analysis-toolkit

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete
pip install -e .
```

### Requisitos

- Python 3.9+
- pip
- Git

## 🎯 Uso Básico

### 1. Extraer Datos

```python
from src.extractors.yahoo_extractor import YahooFinanceExtractor
from src.models.price_series import PriceSeries

# Inicializar extractor
extractor = YahooFinanceExtractor()

# Descargar un símbolo
data = extractor.get_historical_prices(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# Crear serie de precios
apple = PriceSeries(symbol='AAPL', data=data, source='yahoo', asset_type='stock')

# Obtener estadísticas
print(apple.get_stats())
```

### 2. Descargar Múltiples Activos

```python
# Descargar varios símbolos a la vez
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
data_dict = extractor.get_multiple_symbols(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2024-01-01'
)
```

### 3. Crear y Analizar Cartera

```python
from src.models.portfolio import Portfolio

# Crear holdings
holdings = {
    symbol: PriceSeries(symbol=symbol, data=df, source='yahoo', asset_type='stock')
    for symbol, df in data_dict.items()
}

# Definir pesos
weights = {
    'AAPL': 0.25,
    'MSFT': 0.25,
    'GOOGL': 0.25,
    'AMZN': 0.25
}

# Crear cartera
portfolio = Portfolio(
    holdings=holdings,
    weights=weights,
    name="Tech Giants Portfolio"
)

# Estadísticas de la cartera
print(portfolio.get_stats())
```

### 4. Simulación Monte Carlo

```python
# Ejecutar simulación con visualización
portfolio.plot_monte_carlo(
    n_simulations=1000,
    n_days=252,  # 1 año trading
    initial_investment=10000
)
```

### 5. Generar Reporte

```python
from src.reporting.markdown_generator import MarkdownReportGenerator

# Generar reporte
report_gen = MarkdownReportGenerator()
report = report_gen.generate_portfolio_report(portfolio)

# Guardar reporte
with open('portfolio_report.md', 'w') as f:
    f.write(report)

print(report)
```

### 6. Limpieza de Datos

```python
from src.processors.cleaner import DataCleaner

# Eliminar outliers
clean_series = DataCleaner.remove_outliers(
    apple, 
    method='iqr'
)

# Rellenar fechas faltantes
filled_series = DataCleaner.fill_missing_dates(
    apple,
    method='ffill'
)
```

## 🏗️ Arquitectura

El proyecto sigue una arquitectura en capas:

1. **Data Extraction Layer**: Obtención de datos de APIs
2. **Data Models**: Representación estandarizada de datos
3. **Processing Layer**: Limpieza y validación
4. **Analysis & Simulation**: Análisis estadístico y Monte Carlo
5. **Reporting & Visualization**: Generación de reportes y gráficos

Ver el diagrama completo en la documentación.

## 📊 Estructura del Proyecto

```
market-analysis-toolkit/
├── src/
│   ├── extractors/      # Clientes de APIs
│   ├── models/          # DataClasses (PriceSeries, Portfolio)
│   ├── processors/      # Limpieza y validación
│   ├── analysis/        # Análisis estadístico y simulaciones
│   └── reporting/       # Generación de reportes
├── tests/              # Tests unitarios
├── examples/           # Ejemplos de uso
├── config/             # Configuraciones
└── docs/               # Documentación adicional
```

## 🔧 Configuración Avanzada

### Agregar Nueva Fuente de Datos

1. Crear nueva clase heredando de `BaseAPIClient`
2. Implementar métodos abstractos
3. Asegurar que `_standardize_output` devuelva el formato común

```python
class NewAPIExtractor(BaseAPIClient):
    def get_historical_prices(self, symbol, start_date, end_date):
        # Tu implementación
        pass
    
    def _standardize_output(self, raw_data):
        # Convertir al formato estándar
        return standardized_df
```

## 📈 Métricas Disponibles

### Para Series de Precios
- Retorno medio
- Desviación estándar
- Ratio de Sharpe
- Volatilidad anualizada
- Máximo drawdown
- Estadísticas móviles

### Para Carteras
- Retornos ponderados
- Correlaciones entre activos
- Diversificación
- VAR (Value at Risk)
- Simulaciones de Monte Carlo

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest --cov=src tests/
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 🙏 Agradecimientos

- yfinance por el acceso a datos de Yahoo Finance
- Pandas y NumPy por el procesamiento de datos
- Matplotlib y Seaborn por las visualizaciones

## 📧 Contacto

Tu Nombre - tu.email@ejemplo.com

Proyecto Link: [https://github.com/tu-usuario/market-analysis-toolkit](https://github.com/tu-usuario/market-analysis-toolkit)

---

**⚠️ Disclaimer**: Esta herramienta es solo para fines educativos. No constituye asesoramiento financiero.
"""