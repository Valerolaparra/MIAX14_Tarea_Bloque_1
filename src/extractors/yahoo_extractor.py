import yfinance as yf
import pandas as pd
from abc import ABC, abstractmethod
from src.extractors.base_extractor import BaseAPIClient

class YahooFinanceExtractor(BaseAPIClient):
    """Extractor para Yahoo Finance."""
    
    def get_historical_prices(self, 
                             symbol: str,
                             start_date: str,
                             end_date: str) -> pd.DataFrame:
        """Descarga datos históricos de Yahoo Finance."""
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        return self._standardize_output(data)
    
    def _standardize_output(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Estandariza el formato de Yahoo Finance."""
        df = raw_data.reset_index()
        df.columns = df.columns.str.lower()
        
        # Renombrar columnas al formato estándar
        return df.rename(columns={
            'index': 'date',
            'adj close': 'adj_close'
        })
    
    def get_info(self, symbol: str) -> dict:
        """Obtiene información adicional del ticker."""
        return yf.Ticker(symbol).info