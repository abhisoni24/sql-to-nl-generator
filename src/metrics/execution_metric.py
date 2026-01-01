
import sqlite3
import random
from collections import Counter
from faker import Faker

class ExecutionVerifier:
    def __init__(self, schema, foreign_keys):
        self.schema = schema
        self.fks = foreign_keys
        self.fake = Faker()
        
    def _get_sqlite_type(self, type_str):
        mapping = {"int": "INTEGER", "varchar": "TEXT", "text": "TEXT", "datetime": "TIMESTAMP", "boolean": "INTEGER"}
        return mapping.get(type_str, "TEXT")

    def _create_tables(self, cursor):
        for table, cols in self.schema.items():
            col_defs = [f"{col} {self._get_sqlite_type(dtype)}" for col, dtype in cols.items()]
            cursor.execute(f"CREATE TABLE {table} ({', '.join(col_defs)})")

    def _generate_row(self, table, col_types, inserted_ids):
        row = []
        for col, dtype in col_types.items():
            # 1. Check if column is a Foreign Key
            fk_source = None
            for (t_left, t_right), (k_left, k_right) in self.fks.items():
                if t_left == table and k_left == col:
                    fk_source = t_right
                    break # Found the source
            
            val = None
            # 2. Generate Data
            if col == 'id' and dtype == 'int': # Simple Primary Key assumption
                val = len(inserted_ids.get(table, [])) + 1
            elif fk_source: # Pick valid ID from parent table
                if fk_source in inserted_ids and inserted_ids[fk_source]:
                    val = random.choice(inserted_ids[fk_source])
                else:
                    val = None
            else:
                # Context-aware Faker mapping
                if 'username' in col: val = self.fake.user_name()
                elif 'name' in col: val = self.fake.first_name()
                elif 'email' in col: val = self.fake.email()
                elif 'country_code' in col: val = self.fake.country_code()
                elif 'content' in col or 'comment_text' in col: val = self.fake.sentence()
                elif 'date' in col or '_at' in col: val = self.fake.date_time_this_year()
                elif dtype == 'boolean': val = random.choice([0, 1])
                elif dtype == 'int': val = random.randint(0, 1000)
                elif dtype in ['text', 'varchar']: val = self.fake.sentence() if dtype == 'text' else self.fake.word()
                else: val = self.fake.word()
            row.append(val)
        return tuple(row)

    def verify(self, gold_sql, gen_sql, num_rows=100):
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        
        try:
            self._create_tables(cur)
            
            # Track IDs for FK constraints
            inserted_ids = {t: [] for t in self.schema.keys()}
            
            # POPULATION ORDER: Users -> Posts -> Others
            tables_order = ['users', 'posts', 'comments', 'likes', 'follows']
            
            for table in tables_order:
                if table not in self.schema: continue
                cols = self.schema[table]
                rows = []
                for _ in range(num_rows): 
                    row = self._generate_row(table, cols, inserted_ids)
                    rows.append(row)
                    if 'id' in cols: 
                        id_idx = list(cols.keys()).index('id')
                        inserted_ids[table].append(row[id_idx])
                
                placeholders = ', '.join(['?'] * len(cols))
                cur.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)

            # EXECUTE AND COMPARE
            gold_res = cur.execute(gold_sql).fetchall()
            try:
                gen_res = cur.execute(gen_sql).fetchall()
            except Exception as e:
                # print(f"Generated SQL execution failed: {e}")
                return False

            # Strict order check if ORDER BY is present in Gold SQL
            # Simple heuristic:
            if "order by" in gold_sql.lower():
                return gold_res == gen_res
            else:
                return Counter(gold_res) == Counter(gen_res)
            
        except Exception as e:
            # print(f"Verification Error: {e}")
            return False
        finally:
            conn.close()
