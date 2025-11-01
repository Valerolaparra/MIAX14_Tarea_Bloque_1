class DataCleaner:
    """Limpieza y preprocesado de datos."""
    
    @staticmethod
    def remove_outliers(series: PriceSeries, 
                       method: str = 'iqr',
                       threshold: float = 3.0) -> PriceSeries:
        """Elimina outliers de la serie."""
        returns = series.get_returns()
        
        if method == 'iqr':
            Q1 = returns.quantile(0.25)
            Q3 = returns.quantile(0.75)
            IQR = Q3 - Q1
            mask = (returns >= Q1 - 1.5 * IQR) & (returns <= Q3 + 1.5 * IQR)
        elif method == 'zscore':
            z_scores = np.abs((returns - returns.mean()) / returns.std())
            mask = z_scores < threshold
        else:
            raise ValueError(f"Método desconocido: {method}")
        
        # Aplicar máscara
        clean_data = series.data[mask].reset_index(drop=True)
        
        return PriceSeries(
            symbol=series.symbol,
            data=clean_data,
            source=series.source,
            asset_type=series.asset_type
        )
    
    @staticmethod
    def fill_missing_dates(series: PriceSeries, 
                          method: str = 'ffill') -> PriceSeries:
        """Rellena fechas faltantes."""
        # Crear rango completo de fechas
        date_range = pd.date_range(
            start=series.data['date'].min(),
            end=series.data['date'].max(),
            freq='D'
        )
        
        # Reindexar y rellenar
        df = series.data.set_index('date').reindex(date_range)
        
        if method == 'ffill':
            df = df.fillna(method='ffill')
        elif method == 'interpolate':
            df = df.interpolate(method='linear')
        
        df = df.reset_index().rename(columns={'index': 'date'})
        
        return PriceSeries(
            symbol=series.symbol,
            data=df,
            source=series.source,
            asset_type=series.asset_type
        )
