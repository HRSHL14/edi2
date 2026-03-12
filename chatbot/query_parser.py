import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.abstract_client import AbstractLLMClient

class QueryParser:
    def __init__(self, llm_client: AbstractLLMClient):
        self.llm_client = llm_client
        self.schema_prompt = """
You are a precision SQL generator for a PostgreSQL database. 
Given the user's question, output ONLY the raw SQL query. NO markdown, NO notes.

DATABASE SCHEMA:
TABLE: groundwater_data
COLUMNS:
- id (INT)
- district (VARCHAR) - Case-insensitive name (e.g., 'Pune', 'Nashik', 'Jalgaon')
- taluka (VARCHAR) - Case-insensitive name (e.g., 'Haveli', 'Amalner')
- rainfall (FLOAT)
- total_recharge (FLOAT)
- rainfall_recharge (FLOAT)
- surface_irrigation_recharge (FLOAT)
- groundwater_irrigation_recharge (FLOAT)
- canal_recharge (FLOAT) -- CRITICAL: Do NOT use 'can_al_recharge'
- water_body_recharge (FLOAT)
- artificial_structure_recharge (FLOAT)
- extractable_groundwater (FLOAT)
- groundwater_extraction_total (FLOAT)
- agriculture_extraction (FLOAT)
- domestic_extraction (FLOAT)
- industrial_extraction (FLOAT)
- natural_discharge (FLOAT)
- stage_of_extraction (FLOAT) -- Percentage (e.g., 85.5)
- category (VARCHAR) -- Values: 'Safe', 'Semi-Critical', 'Critical', 'Over-Exploited'
- future_groundwater_availability (FLOAT)
- year (VARCHAR)

RULES:
1. ALWAYS use ILIKE for string comparisons (e.g., district ILIKE 'Pune').
2. Use EXACT column names from the list above.
3. If the user asks for 'safe' talukas, filter by category ILIKE 'Safe'.
4. If the user asks for a 'report', 'full summary', 'detailed', 'which', 'highest', 'lowest', or 'rank/top' view, ALWAYS use 'SELECT *' to ensure all data points (20+ fields) are available for the assistant.
5. For comparisons between locations, use OR (e.g., district ILIKE 'Pune' OR district ILIKE 'Nashik').
6. Do NOT use LIMIT unless explicitly asked for 'top' (e.g., top 10) or 'recent' records. For 'highest' or 'lowest', use ORDER BY ... LIMIT 1.
7. For district-wide rankings, use 'SELECT * FROM groundwater_data WHERE level ILIKE 'district'' (if applicable) or group by accordingly. (Actually, just ensure SELECT * is used).
        """

    def parse_to_sql(self, user_query: str) -> str:
        response = self.llm_client.generate_response(
            system_prompt=self.schema_prompt, 
            user_prompt=f"User Question: {user_query}\n\nSQL Query:"
        )
        # Clean up any markdown
        clean_sql = response.replace("```sql", "").replace("```", "").strip()
        return clean_sql
