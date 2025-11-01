from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Optional
import pandas as pd


class BaseAPIClient(ABC):
    """Clase base abstracta para clientes de API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
    
    @abstractmethod
    def get_historical_prices(self, 
                             symbol: str, 
                             start_date: str,
                             end_date: str) -> pd.DataFrame:
        """Método abstracto para obtener precios históricos."""
        pass
    
    @abstractmethod
    def _standardize_output(self, raw_data: Dict) -> pd.DataFrame:
        """Estandariza la salida al formato común."""
        pass
    
    def get_multiple_symbols(self, 
                            symbols: List[str],
                            start_date: str,
                            end_date: str) -> Dict[str, pd.DataFrame]:
        """Descarga múltiples símbolos en paralelo."""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get_historical_prices(symbol, start_date, end_date)
                print(f"✓ {symbol} descargado")
            except Exception as e:
                print(f"✗ Error en {symbol}: {str(e)}")
        return results
