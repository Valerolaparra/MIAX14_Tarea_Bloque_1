# ============================================================================
# src/extractors/alpha_extractor.py
# ============================================================================
"""
Extractor para Alpha Vantage API.

Alpha Vantage ofrece datos financieros gratuitos con límites:
- 25 requests por día (free tier)
- 5 API calls por minuto

Documentación: https://www.alphavantage.co/documentation/
"""

import pandas as pd
import requests
import time
from typing import Dict, Optional, List
from datetime import datetime
import json

# Importar la clase base
from .base_extractor import BaseAPIClient


class AlphaVantageExtractor(BaseAPIClient):
    """
    Extractor para Alpha Vantage API.
    
    Requiere API key gratuita de: https://www.alphavantage.co/support/#api-key
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str):
        """
        Inicializa el extractor con API key.
        
        Args:
            api_key: API key de Alpha Vantage (obtener en alphavantage.co)
        
        Raises:
            ValueError: Si no se proporciona API key
        """
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError(
                "Se requiere un API key válido de Alpha Vantage.\n"
                "Obtén uno gratis en: https://www.alphavantage.co/support/#api-key"
            )
        
        super().__init__(api_key)
        self.call_count = 0
        self.last_call_time = None
        
    def _rate_limit(self):
        """Implementa rate limiting (5 llamadas por minuto)."""
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < 12:  # 60 segundos / 5 llamadas = 12 segundos entre llamadas
                sleep_time = 12 - elapsed
                print(f"⏳ Rate limit: esperando {sleep_time:.1f}s...")
                time.sleep(sleep_time)
        
        self.last_call_time = time.time()
        self.call_count += 1
    
    def get_historical_prices(self, 
                             symbol: str,
                             start_date: str,
                             end_date: str,
                             outputsize: str = "full") -> pd.DataFrame:
        """
        Obtiene precios históricos diarios.
        
        Args:
            symbol: Símbolo del activo (ej: 'AAPL', 'MSFT')
            start_date: Fecha inicio (formato: 'YYYY-MM-DD')
            end_date: Fecha fin (formato: 'YYYY-MM-DD')
            outputsize: 'compact' (últimos 100 días) o 'full' (hasta 20 años)
        
        Returns:
            DataFrame estandarizado con columnas: date, open, high, low, close, volume
        
        Raises:
            ValueError: Si el símbolo no existe o hay error en la API
        """
        self._rate_limit()
        
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': outputsize,
            'datatype': 'json'
        }
        
        try:
            print(f"📡 Descargando {symbol} desde Alpha Vantage...")
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar errores de la API
            if "Error Message" in data:
                raise ValueError(f"Símbolo inválido: {symbol}")
            
            if "Note" in data:
                raise ValueError(
                    f"Límite de API excedido. Alpha Vantage free tier: 25 llamadas/día.\n"
                    f"Mensaje: {data['Note']}"
                )
            
            if "Time Series (Daily)" not in data:
                raise ValueError(f"No se encontraron datos para {symbol}")
            
            # Estandarizar output
            df = self._standardize_output(data)
            
            # Filtrar por rango de fechas
            df = self._filter_by_date_range(df, start_date, end_date)
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error de conexión con Alpha Vantage: {str(e)}")
    
    def _standardize_output(self, raw_data: Dict) -> pd.DataFrame:
        """
        Estandariza el formato de Alpha Vantage al formato común.
        
        Alpha Vantage devuelve:
        {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "150.00",
                    "2. high": "152.00",
                    "3. low": "149.00",
                    "4. close": "151.00",
                    "5. adjusted close": "151.00",
                    "6. volume": "1000000",
                    ...
                }
            }
        }
        """
        time_series = raw_data.get("Time Series (Daily)", {})
        
        # Convertir a lista de diccionarios
        rows = []
        for date_str, values in time_series.items():
            rows.append({
                'date': pd.to_datetime(date_str),
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'adj_close': float(values['5. adjusted close']),
                'volume': int(values['6. volume'])
            })
        
        # Crear DataFrame
        df = pd.DataFrame(rows)
        
        # Ordenar por fecha (más antigua primero)
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _filter_by_date_range(self, 
                              df: pd.DataFrame,
                              start_date: str,
                              end_date: str) -> pd.DataFrame:
        """Filtra DataFrame por rango de fechas."""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        mask = (df['date'] >= start) & (df['date'] <= end)
        return df[mask].reset_index(drop=True)
    
    def get_intraday_prices(self,
                           symbol: str,
                           interval: str = '5min',
                           outputsize: str = 'compact') -> pd.DataFrame:
        """
        Obtiene precios intraday (dentro del día).
        
        Args:
            symbol: Símbolo del activo
            interval: '1min', '5min', '15min', '30min', '60min'
            outputsize: 'compact' (últimos 100 puntos) o 'full' (últimos 30 días)
        
        Returns:
            DataFrame con datos intraday
        """
        self._rate_limit()
        
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': outputsize,
            'datatype': 'json'
        }
        
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        data = response.json()
        
        if f"Time Series ({interval})" not in data:
            raise ValueError(f"No se encontraron datos intraday para {symbol}")
        
        return self._standardize_intraday_output(data, interval)
    
    def _standardize_intraday_output(self, raw_data: Dict, interval: str) -> pd.DataFrame:
        """Estandariza datos intraday."""
        time_series = raw_data.get(f"Time Series ({interval})", {})
        
        rows = []
        for datetime_str, values in time_series.items():
            rows.append({
                'datetime': pd.to_datetime(datetime_str),
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(rows)
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Para compatibilidad con PriceSeries, añadir columna 'date'
        df['date'] = df['datetime']
        
        return df
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Obtiene cotización en tiempo real (o más reciente).
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Diccionario con información de la cotización
        """
        self._rate_limit()
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        data = response.json()
        
        if "Global Quote" not in data:
            raise ValueError(f"No se pudo obtener cotización para {symbol}")
        
        quote = data["Global Quote"]
        
        return {
            'symbol': quote.get('01. symbol', symbol),
            'price': float(quote.get('05. price', 0)),
            'volume': int(quote.get('06. volume', 0)),
            'latest_trading_day': quote.get('07. latest trading day', ''),
            'previous_close': float(quote.get('08. previous close', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%')
        }
    
    def get_company_overview(self, symbol: str) -> Dict:
        """
        Obtiene información fundamental de la empresa.
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Diccionario con información de la empresa
        """
        self._rate_limit()
        
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        data = response.json()
        
        if not data or "Symbol" not in data:
            raise ValueError(f"No se encontró información para {symbol}")
        
        return {
            'symbol': data.get('Symbol', ''),
            'name': data.get('Name', ''),
            'sector': data.get('Sector', ''),
            'industry': data.get('Industry', ''),
            'market_cap': data.get('MarketCapitalization', ''),
            'pe_ratio': data.get('PERatio', ''),
            'dividend_yield': data.get('DividendYield', ''),
            'description': data.get('Description', '')
        }
    
    def search_symbol(self, keywords: str) -> List[Dict]:
        """
        Busca símbolos por palabra clave.
        
        Args:
            keywords: Términos de búsqueda (ej: 'Apple', 'Microsoft')
        
        Returns:
            Lista de diccionarios con resultados
        """
        self._rate_limit()
        
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords,
            'apikey': self.api_key
        }
        
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        data = response.json()
        
        if "bestMatches" not in data:
            return []
        
        results = []
        for match in data["bestMatches"]:
            results.append({
                'symbol': match.get('1. symbol', ''),
                'name': match.get('2. name', ''),
                'type': match.get('3. type', ''),
                'region': match.get('4. region', ''),
                'currency': match.get('8. currency', '')
            })
        
        return results
    
    def get_multiple_symbols(self,
                            symbols: List[str],
                            start_date: str,
                            end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Descarga múltiples símbolos con rate limiting.
        
        Args:
            symbols: Lista de símbolos
            start_date: Fecha inicio
            end_date: Fecha fin
        
        Returns:
            Diccionario {símbolo: DataFrame}
        """
        results = {}
        total = len(symbols)
        
        print(f"\n🔄 Descargando {total} símbolos de Alpha Vantage...")
        print(f"⚠️  Rate limit: ~12 segundos entre llamadas")
        print(f"⏱️  Tiempo estimado: ~{total * 12 / 60:.1f} minutos\n")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"[{i}/{total}] {symbol}...", end=" ")
                df = self.get_historical_prices(symbol, start_date, end_date)
                results[symbol] = df
                print(f"✓ ({len(df)} registros)")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
        
        print(f"\n✓ Completado: {len(results)}/{total} símbolos descargados")
        return results


# ============================================================================
# EJEMPLO DE USO
# ============================================================================
if __name__ == "__main__":
    # Configuración
    API_KEY = "YOUR_API_KEY_HERE"  # Reemplazar con tu API key
    
    try:
        # Inicializar extractor
        extractor = AlphaVantageExtractor(api_key=API_KEY)
        
        # ========================================================================
        # 1. BUSCAR SÍMBOLOS
        # ========================================================================
        print("=" * 70)
        print("🔍 BÚSQUEDA DE SÍMBOLOS")
        print("=" * 70)
        
        results = extractor.search_symbol("Apple")
        print(f"\nResultados para 'Apple':")
        for r in results[:3]:
            print(f"  {r['symbol']:6} - {r['name']} ({r['region']})")
        
        # ========================================================================
        # 2. COTIZACIÓN EN TIEMPO REAL
        # ========================================================================
        print("\n" + "=" * 70)
        print("💹 COTIZACIÓN EN TIEMPO REAL")
        print("=" * 70)
        
        quote = extractor.get_quote('AAPL')
        print(f"\n{quote['symbol']}:")
        print(f"  Precio: ${quote['price']:.2f}")
        print(f"  Cambio: {quote['change_percent']}")
        print(f"  Volumen: {quote['volume']:,}")
        
        # ========================================================================
        # 3. INFORMACIÓN DE LA EMPRESA
        # ========================================================================
        print("\n" + "=" * 70)
        print("🏢 INFORMACIÓN DE LA EMPRESA")
        print("=" * 70)
        
        info = extractor.get_company_overview('AAPL')
        print(f"\n{info['symbol']} - {info['name']}")
        print(f"  Sector: {info['sector']}")
        print(f"  Industria: {info['industry']}")
        print(f"  Market Cap: ${info['market_cap']}")
        print(f"  P/E Ratio: {info['pe_ratio']}")
        
        # ========================================================================
        # 4. DATOS HISTÓRICOS
        # ========================================================================
        print("\n" + "=" * 70)
        print("📊 DATOS HISTÓRICOS")
        print("=" * 70)
        
        data = extractor.get_historical_prices(
            symbol='AAPL',
            start_date='2023-01-01',
            end_date='2024-01-01'
        )
        
        print(f"\nDatos de AAPL:")
        print(f"  Registros: {len(data)}")
        print(f"  Rango: {data['date'].min()} a {data['date'].max()}")
        print(f"\nPrimeras filas:")
        print(data.head())
        
        # ========================================================================
        # 5. MÚLTIPLES SÍMBOLOS
        # ========================================================================
        print("\n" + "=" * 70)
        print("📦 DESCARGA MÚLTIPLE")
        print("=" * 70)
        
        symbols = ['AAPL', 'MSFT']
        data_dict = extractor.get_multiple_symbols(
            symbols=symbols,
            start_date='2024-01-01',
            end_date='2024-02-01'
        )
        
        print("\nResumen:")
        for symbol, df in data_dict.items():
            print(f"  {symbol}: {len(df)} registros")
        
        # ========================================================================
        # 6. INTEGRACIÓN CON PRICESERIES
        # ========================================================================
        print("\n" + "=" * 70)
        print("🔗 INTEGRACIÓN CON PRICESERIES")
        print("=" * 70)
        
        # Importar PriceSeries
        import sys
        sys.path.append('..')
        from models.price_series import PriceSeries
        
        # Crear objeto PriceSeries
        apple = PriceSeries(
            symbol='AAPL',
            data=data,
            source='alpha_vantage',
            asset_type='stock'
        )
        
        stats = apple.get_stats()
        print(f"\nEstadísticas de AAPL:")
        print(f"  Retorno Total: {stats['total_return']*100:.2f}%")
        print(f"  Volatilidad: {stats['volatility']*100:.2f}%")
        print(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        
        print("\n✅ Extractor de Alpha Vantage funcionando correctamente!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Para usar este extractor:")
        print("   1. Ve a https://www.alphavantage.co/support/#api-key")
        print("   2. Obtén tu API key gratuito")
        print("   3. Reemplaza 'YOUR_API_KEY_HERE' con tu key")
        print("   4. Límite free tier: 25 llamadas/día, 5 llamadas/minuto")