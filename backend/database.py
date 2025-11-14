import sqlite3
import time
from contextlib import contextmanager
from config import DATABASE, SQLITE_PRAGMAS, DATA_LIMITS, SENSOR_RANGES


class Database:
    """Gerenciador otimizado de banco de dados SQLite para Raspberry Pi"""
    
    def __init__(self):
        self.db_path = DATABASE['path']
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões - garante fechamento automático"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=DATABASE['timeout'],
            check_same_thread=DATABASE['check_same_thread']
        )
        
        # Aplica PRAGMAs de otimização
        for pragma, value in SQLITE_PRAGMAS.items():
            conn.execute(f'PRAGMA {pragma} = {value}')
        
        # Retorna Row objects ao invés de tuplas (facilita acesso por nome)
        conn.row_factory = sqlite3.Row
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Cria tabela e índices se não existirem"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela principal
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leituras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperatura REAL NOT NULL,
                    umidade_ar REAL NOT NULL,
                    umidade_solo REAL NOT NULL,
                    luminosidade REAL NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            ''')
            
            # Índice para queries por data (DESC = mais recentes primeiro)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON leituras(timestamp DESC)
            ''')
    
    def validate_sensor_data(self, data):
        """
        Valida ranges dos sensores
        Retorna: (bool, str) -> (válido?, mensagem de erro)
        """
        # Itera sobre as regras de range, e não sobre os dados de entrada
        for sensor_name, config in SENSOR_RANGES.items():
            # Verifica se o sensor a ser validado está presente nos dados
            if sensor_name in data:
                value = data[sensor_name]
                if not (config['min'] <= value <= config['max']):
                    return False, f"{sensor_name} fora do range: {value}"
        
        return True, ""
    
    def insert_reading(self, temperatura, umidade_ar, umidade_solo, luminosidade):
        """
        Insere uma leitura no banco
        Retorna: ID da leitura inserida ou None se falhar
        """
        # Validação
        data = {
            'temperatura': temperatura,
            'umidade_ar': umidade_ar,
            'umidade_solo': umidade_solo,
            'luminosidade': luminosidade
        }
        
        is_valid, error_msg = self.validate_sensor_data(data)
        if not is_valid:
            raise ValueError(f"Dados inválidos: {error_msg}")
        
        # Inserção
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO leituras 
                (temperatura, umidade_ar, umidade_solo, luminosidade, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (temperatura, umidade_ar, umidade_solo, luminosidade, int(time.time())))
            
            return cursor.lastrowid

    def _get_safe_query_limit(self, limit=None):
        """Helper privado para calcular e travar o limite de queries SQL."""
        max_limit = DATA_LIMITS['max_records_query']
        
        # Se limite não for fornecido, usa o teto padrão
        if limit is None:
            return max_limit
        
        # Garante que o limite seja positivo (min 0) e não exceda o teto
        return min(max(0, limit), max_limit)

    def get_recent_readings(self, limit=None):
        """
        Retorna leituras mais recentes
        limit: quantidade de registros (padrão do config.py)
        """
        safe_limit = self._get_safe_query_limit(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT id, temperatura, umidade_ar, umidade_solo, 
                       luminosidade, timestamp
                FROM leituras
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (safe_limit,))
            
            rows = cursor.fetchall()
            
            # Converte Row objects para dicts
            return [dict(row) for row in rows]
    
    def get_readings_by_timerange(self, start_timestamp, end_timestamp, limit=None):
        """
        Retorna leituras em um intervalo de tempo específico
        Útil para análises do Edu
        """
        safe_limit = self._get_safe_query_limit(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, temperatura, umidade_ar, umidade_solo,
                       luminosidade, timestamp
                FROM leituras
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (start_timestamp, end_timestamp, safe_limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_statistics(self):
        """
        Retorna estatísticas básicas (otimizado - uma query só)
        Útil para endpoint de análise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_registros,
                    AVG(temperatura) as temp_media,
                    AVG(umidade_ar) as umid_ar_media,
                    AVG(umidade_solo) as umid_solo_media,
                    AVG(luminosidade) as lum_media,
                    MIN(timestamp) as primeira_leitura,
                    MAX(timestamp) as ultima_leitura
                FROM leituras
            ''')
            
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def cleanup_old_data(self):
        """
        Remove dados antigos (conforme retention_days no config)
        Executa automaticamente para economizar espaço
        """
        retention_seconds = DATA_LIMITS['retention_days'] * 86400
        cutoff_timestamp = int(time.time()) - retention_seconds
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM leituras
                WHERE timestamp < ?
            ''', (cutoff_timestamp,))
            
            deleted_count = cursor.rowcount
            
            # VACUUM para liberar espaço no disco (importante no SD card)
            if deleted_count > 0:
                conn.execute('VACUUM')
            
            return deleted_count


# Instância global (singleton)
db = Database()