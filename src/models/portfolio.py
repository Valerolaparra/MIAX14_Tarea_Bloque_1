from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from dataclasses import dataclass
from src.models.price_series import PriceSeries



@dataclass
class Portfolio:
    """Representa una cartera de inversión."""
    
    holdings: Dict[str, PriceSeries]
    weights: Dict[str, float]
    name: str = "Portfolio"
    
    def __post_init__(self):
        """Valida pesos y normaliza si es necesario."""
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0):
            print(f"⚠️ Pesos no suman 1.0 ({total_weight}). Normalizando...")
            self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
        # Verificar que todos los activos tengan peso
        if set(self.holdings.keys()) != set(self.weights.keys()):
            raise ValueError("Los símbolos en holdings y weights deben coincidir")
    
    def get_portfolio_returns(self) -> pd.Series:
        """Calcula los retornos ponderados de la cartera."""
        # Alinear todas las fechas
        all_returns = pd.DataFrame()
        
        for symbol, series in self.holdings.items():
            returns = series.get_returns()
            all_returns[symbol] = returns
        
        # Eliminar NaN y calcular retorno ponderado
        all_returns = all_returns.dropna()
        weighted_returns = sum(all_returns[symbol] * self.weights[symbol] 
                              for symbol in self.holdings.keys())
        
        return weighted_returns
    
    def get_stats(self) -> dict:
        """Estadísticas de la cartera completa."""
        portfolio_returns = self.get_portfolio_returns()
        
        return {
            'mean_return': portfolio_returns.mean(),
            'std_return': portfolio_returns.std(),
            'sharpe_ratio': portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252),
            'annualized_return': portfolio_returns.mean() * 252,
            'annualized_volatility': portfolio_returns.std() * np.sqrt(252)
        }
    
    def monte_carlo_simulation(self, 
                               n_simulations: int = 1000,
                               n_days: int = 252,
                               initial_investment: float = 10000) -> np.ndarray:
        """
        Simulación de Monte Carlo para la evolución de la cartera.
        
        Args:
            n_simulations: Número de simulaciones
            n_days: Días a proyectar
            initial_investment: Inversión inicial
            
        Returns:
            Array con las simulaciones (n_simulations x n_days)
        """
        portfolio_returns = self.get_portfolio_returns()
        mean_return = portfolio_returns.mean()
        std_return = portfolio_returns.std()
        
        # Generar retornos aleatorios
        simulations = np.zeros((n_simulations, n_days))
        
        for i in range(n_simulations):
            daily_returns = np.random.normal(mean_return, std_return, n_days)
            price_path = initial_investment * (1 + daily_returns).cumprod()
            simulations[i] = price_path
        
        return simulations
    
    def plot_monte_carlo(self, 
                        n_simulations: int = 1000,
                        n_days: int = 252,
                        initial_investment: float = 10000):
        """Visualiza las simulaciones de Monte Carlo."""
        simulations = self.monte_carlo_simulation(n_simulations, n_days, initial_investment)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1: Trayectorias
        for i in range(min(100, n_simulations)):
            ax1.plot(simulations[i], alpha=0.1, color='blue', linewidth=0.5)
        
        ax1.plot(simulations.mean(axis=0), color='red', linewidth=2, label='Media')
        ax1.fill_between(range(n_days), 
                         np.percentile(simulations, 5, axis=0),
                         np.percentile(simulations, 95, axis=0),
                         alpha=0.2, color='red', label='90% Intervalo')
        ax1.set_title(f'Simulación Monte Carlo - {self.name}')
        ax1.set_xlabel('Días')
        ax1.set_ylabel('Valor de la Cartera ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Distribución final
        final_values = simulations[:, -1]
        ax2.hist(final_values, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax2.axvline(final_values.mean(), color='red', linestyle='--', linewidth=2, label='Media')
        ax2.axvline(initial_investment, color='green', linestyle='--', linewidth=2, label='Inversión Inicial')
        ax2.set_title('Distribución de Valores Finales')
        ax2.set_xlabel('Valor Final ($)')
        ax2.set_ylabel('Frecuencia')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
        # Estadísticas
        print(f"\n📊 Resultados de la Simulación ({n_simulations} iteraciones, {n_days} días)")
        print(f"{'='*60}")
        print(f"Inversión Inicial: ${initial_investment:,.2f}")
        print(f"Valor Final Esperado: ${final_values.mean():,.2f}")
        print(f"Valor Mínimo (5%): ${np.percentile(final_values, 5):,.2f}")
        print(f"Valor Máximo (95%): ${np.percentile(final_values, 95):,.2f}")
        print(f"Probabilidad de pérdida: {(final_values < initial_investment).sum() / n_simulations * 100:.2f}%")

