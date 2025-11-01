from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import numpy as np
import pandas as pd


@dataclass
class PriceSeries:
    """Clase base para series temporales de precios."""
    
    symbol: str
    data: pd.DataFrame
    source: str
    asset_type: str = "unknown"
    _stats: dict = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        """Validación y cálculo automático de estadísticas básicas."""
        self._validate_data()
        self._standardize_columns()
        self._calculate_basic_stats()
    
    def _validate_data(self):
        """Valida que el DataFrame tenga las columnas necesarias."""
        required = ['date', 'close']
        if not all(col in self.data.columns for col in required):
            raise ValueError(f"DataFrame debe contener: {required}")
        
        # Asegurar que date sea datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['date']):
            self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Ordenar por fecha
        self.data = self.data.sort_values('date').reset_index(drop=True)
    
    def _standardize_columns(self):
        """Estandariza nombres de columnas."""
        column_mapping = {
            'Date': 'date',
            'Close': 'close',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        self.data.rename(columns=column_mapping, inplace=True)
        self.data.columns = self.data.columns.str.lower()
    
    def _calculate_basic_stats(self):
        """Calcula estadísticas básicas automáticamente."""
        returns = self.data['close'].pct_change().dropna()
        
        self._stats = {
            'mean_return': returns.mean(),
            'std_return': returns.std(),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'total_return': (self.data['close'].iloc[-1] / self.data['close'].iloc[0]) - 1,
            'volatility': returns.std() * np.sqrt(252),
            'max_drawdown': self._calculate_max_drawdown()
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calcula el máximo drawdown."""
        cumulative = (1 + self.data['close'].pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def get_returns(self) -> pd.Series:
        """Retorna la serie de rendimientos."""
        return self.data['close'].pct_change().dropna()
    
    def get_stats(self) -> dict:
        """Retorna las estadísticas calculadas."""
        return self._stats
    
    def rolling_stats(self, window: int = 30) -> pd.DataFrame:
        """Calcula estadísticas móviles."""
        returns = self.get_returns()
        return pd.DataFrame({
            'rolling_mean': returns.rolling(window).mean(),
            'rolling_std': returns.rolling(window).std(),
            'rolling_sharpe': (returns.rolling(window).mean() / 
                              returns.rolling(window).std() * np.sqrt(252))
        })

