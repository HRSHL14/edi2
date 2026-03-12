import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import LLM_PROVIDER
from llm.groq_client import GroqClient
from llm.ollama_client import OllamaClient
from chatbot.query_parser import QueryParser
from database.db import get_db_connection

class ChatbotEngine:
    def __init__(self):
        # Instantiate both clients for fast switching
        self.groq_client = GroqClient()
        self.ollama_client = OllamaClient()
        
        # Default parser (will be updated per request)
        self.parser = QueryParser(self.groq_client)
        
        # Load Global Benchmarks
        self.benchmarks_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "benchmarks.json")
        self.benchmarks_data = {}
        self._load_benchmarks()

    def _load_benchmarks(self):
        try:
            import json
            if os.path.exists(self.benchmarks_path):
                with open(self.benchmarks_path, 'r') as f:
                    self.benchmarks_data = json.load(f)
            
            # Auto-populate districts if missing
            if "districts" not in self.benchmarks_data:
                self._populate_districts_benchmarks()
        except Exception as e:
            print(f"Warning: Could not load benchmarks.json: {e}")

    def _populate_districts_benchmarks(self):
        conn = get_db_connection()
        if not conn: return
        try:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        district,
                        AVG(rainfall) as rain, 
                        AVG(total_recharge) as rech, 
                        AVG(groundwater_extraction_total) as extr, 
                        AVG(extractable_groundwater) as ext_gw, 
                        AVG(agriculture_extraction) as agri 
                    FROM groundwater_data 
                    GROUP BY district
                """)
                rows = cur.fetchall()
                districts = {}
                for r in rows:
                    d = r['district'].upper()
                    ra, re, ex, eg, ag = r['rain'], r['rech'], r['extr'], r['ext_gw'], r['agri']
                    if eg and ex:
                        districts[d] = {
                            "name": f"{d} AVG",
                            "stress_index": round((ex/eg)*100, 1),
                            "sustainability_ratio": round(re/ex, 1) if ex else 0,
                            "recharge_efficiency": round(re/ra, 1) if ra else 0,
                            "agri_dependency": round((ag/ex)*100, 1) if ex else 0
                        }
                self.benchmarks_data["districts"] = districts
                import json
                with open(self.benchmarks_path, 'w') as f:
                    json.dump(self.benchmarks_data, f, indent=2)
        except Exception as e:
            print(f"Error populating benchmarks: {e}")
        finally:
            conn.close()

    def execute_sql(self, sql_query: str):
        conn = get_db_connection()
        if not conn:
            return "Error: Could not connect to the database."
        try:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if not sql_query.upper().strip().startswith("SELECT"):
                    return "Database error: Only SELECT queries are permitted."
                cur.execute(sql_query)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return f"Database execution error: {str(e)}"
        finally:
            conn.close()

    def get_benchmarks(self, district_name=None):
        # Load from self.benchmarks_data
        india_raw = self.benchmarks_data.get("india_2024_2025", {})
        mh_raw = self.benchmarks_data.get("maharashtra_2024_2025", {})
        
        # 1 BCM = 1000 MCM
        india = {
            "name": "India", 
            "stress": india_raw.get("stress_index", 60.6), 
            "sustainability": india_raw.get("sustainability_ratio", 1.8), 
            "efficiency": india_raw.get("recharge_efficiency", 425.0), 
            "agri_dep": india_raw.get("agri_dependency", 87.0),
            "stage": india_raw.get("stage_of_extraction", 60.6),
            "agri_pct": india_raw.get("agri_extraction_pct", 87.0),
            "dom_pct": india_raw.get("domestic_extraction_pct", 11.8),
            "ind_pct": india_raw.get("industrial_extraction_pct", 1.2),
            "rech_mcm": india_raw.get("recharge_bcm", 448.51) * 1000,
            "extr_mcm": india_raw.get("extraction_total_bcm", 247.22) * 1000
        }
        
        # 1 ham = 0.01 MCM
        mh = {
            "name": "Maharashtra", 
            "stress": mh_raw.get("stress_index", 51.8), 
            "sustainability": mh_raw.get("sustainability_ratio", 2.0), 
            "efficiency": mh_raw.get("recharge_efficiency", 32.6), 
            "agri_dep": mh_raw.get("agri_dependency", 91.3),
            "stage": mh_raw.get("stage_of_extraction", 51.8),
            "agri_pct": mh_raw.get("agri_extraction_pct", 91.3),
            "dom_pct": mh_raw.get("domestic_extraction_pct", 7.9),
            "ind_pct": mh_raw.get("industrial_extraction_pct", 0.8),
            "rech_mcm": mh_raw.get("recharge_ham", 3388867.94) * 0.01,
            "extr_mcm": mh_raw.get("extraction_total_ham", 1657040.9) * 0.01
        }
        
        benchmarks = [mh, india]
        
        if district_name:
            d_key = district_name.upper()
            d_benchmarks = self.benchmarks_data.get("districts", {})
            
            if d_key in d_benchmarks:
                d = d_benchmarks[d_key]
                # Note: benchmarks.json district values don't have volumes yet, 
                # we'll look them up or omit if we can't calculate them here easily.
                # Actually, I'll use the DB lookup for Districts to get accurate volumes.
                pass
            
            # Dynamic lookup for District volumes and metrics
            conn = get_db_connection()
            if conn:
                try:
                    from psycopg2.extras import RealDictCursor
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT 
                                AVG(rainfall) as rain, 
                                AVG(total_recharge) as rech, 
                                AVG(groundwater_extraction_total) as extr, 
                                AVG(extractable_groundwater) as ext_gw, 
                                AVG(agriculture_extraction) as agri,
                                AVG(domestic_extraction) as dom,
                                AVG(industrial_extraction) as ind
                            FROM groundwater_data 
                            WHERE district ILIKE %s
                        """, (district_name,))
                        r = cur.fetchone()
                        if r and r['ext_gw'] and r['extr']:
                            d_stress = round((r['extr']/r['ext_gw'])*100, 1)
                            d_sust = round(r['rech']/r['extr'], 1) if r['extr'] else 0
                            d_eff = round((r['rech']/r['rain'])*1000, 1) if r['rain'] else 0
                            d_agri_pct = round((r['agri']/r['extr'])*100, 1) if r['extr'] else 0
                            d_dom_pct = round((r['dom']/r['extr'])*100, 1) if r['extr'] else 0
                            d_ind_pct = round((r['ind']/r['extr'])*100, 1) if r['extr'] else 0
                            benchmarks.insert(0, {
                                "name": district_name.title(), 
                                "stress": d_stress, 
                                "sustainability": d_sust, 
                                "efficiency": d_eff, 
                                "agri_dep": d_agri_pct,
                                "stage": d_stress,
                                "agri_pct": d_agri_pct,
                                "dom_pct": d_dom_pct,
                                "ind_pct": d_ind_pct,
                                "rech_mcm": round(r['rech'], 1),
                                "extr_mcm": round(r['extr'], 1)
                            })
                finally:
                    conn.close()
        return benchmarks

    def handle_query(self, user_question: str, provider: str = "groq") -> dict:
        # Select client based on provider
        llm_client = self.ollama_client if provider.lower() == "ollama" else self.groq_client
        
        # Update parser to use the same client
        self.parser.llm_client = llm_client
        
        sql_query = self.parser.parse_to_sql(user_question)
        db_records = self.execute_sql(sql_query)
        
        # Pre-calculate Benchmarks for the prompt
        benchmarks = []
        if isinstance(db_records, list) and len(db_records) > 0:
            dist = db_records[0].get('district')
            benchmarks = self.get_benchmarks(dist)

        system_prompt = f"""
        You are a Groundwater Intelligence Dashboard Architect.
        MANDATORY OUTPUT: A SINGLE VALID JSON OBJECT ONLY.

        REQUIRED JSON SCHEMA:
        {{
          "explanation": "Markdown text containing:
             1. # [Location] Groundwater Health Dashboard (2024-25)
             2. A 3-Column Key Metrics Table: | Metric | Region Value | National/State Benchmark |
                Include: Stress Index, Sustainability, Efficiency, Stage, Agri-Dependency.
             3. Detailed Insights: Explicitly state if the region is better/worse than State and Nation.
             **DATA INTEGRITY**: India(Stress 60.6%, Sust 1.8), MH(Stress 51.8%, Sust 2.0).",
          "visuals": [
             {{ "type": "bar", "title": "...", "labels": [], "datasets": [{{ "label": "...", "data": [] }}] }}
          ]
        }}

        MANDATORY VISUALS (FOR SINGLE REGION - ALWAYS GENERATE ALL 6):
        1. Sustainability Index Comparison (Bar: Taluka vs District vs State vs Nation)
        2. Recharge vs Extraction Balance (Dual Bar: 4 levels, MCM)
        3. Stage of Extraction Comparison (Bar: 4 levels, %)
        4. Sector-wise Groundwater Use (Pie: Agri, Domestic, Industrial, Others)
        5. Groundwater Stress Index (Bar: 4 levels, %)
        6. Recharge Efficiency (Bar: 4 levels, scaled indicator)
        """
        
        user_prompt = f"USER QUERY: {user_question}\nRECORDS: {db_records}\nBENCHMARKS: {benchmarks}\n\nTASK: Generate the JSON report with the 6 MANDATORY DASHBOARD VISUALS. ROUND TO 1 DECIMAL."
        
        try:
            response_text = llm_client.generate_response(system_prompt, user_prompt)
        except Exception as e:
            return {"explanation": f"Assistant Error: {str(e)}", "visuals": []}
        
        try:
            import json, re
            clean_text = re.sub(r'```json\n?|```', '', response_text)
            json_matches = re.findall(r'(\{.+\})', clean_text, re.DOTALL)
            data = None
            if json_matches:
                json_matches.sort(key=len, reverse=True)
                for match in json_matches:
                    try: data = json.loads(match); break
                    except: continue
            
            if not data or "explanation" not in data or "visuals" not in data or len(data.get("visuals",[])) < 5:
                if isinstance(db_records, list) and len(db_records) > 0:
                    records = db_records
                    visuals, exps = [], []
                    
                    if len(records) > 2:
                        # Rankings (Multiple locations)
                        labels = [r.get("taluka") or r.get("district") or f"L{i+1}" for i, r in enumerate(records)]
                        m_key = "future_groundwater_availability"
                        for k in records[0].keys():
                            if k.lower() in user_question.lower(): m_key = k; break
                        visuals.append({"type": "bar", "title": f"Rank: {m_key.replace('_',' ').title()}", "labels": labels, "datasets": [{"label": "Value", "data": [round(float(r.get(m_key,0)),1) for r in records]}]})
                    else:
                        # Single Location Benchmarking (Unified Dashboard)
                        for r in records:
                            loc = r.get("taluka") or r.get("district") or "Region"
                            rain, rech, extr, egw = float(r.get("rainfall",0)), float(r.get("total_recharge",0)), float(r.get("groundwater_extraction_total",0)), float(r.get("extractable_groundwater",1))
                            agri, dom, ind = float(r.get("agriculture_extraction", 0)), float(r.get("domestic_extraction", 0)), float(r.get("industrial_extraction", 0))
                            
                            stress, sust, eff, stage = round((extr/egw)*100, 1), round(rech/extr, 1) if extr else 0, round((rech/rain)*1000, 1) if rain else 0, round((extr/egw)*100, 1)
                            
                            # Comparison Data Preparation (4 Levels)
                            b_labels = [loc] + [b['name'] for b in benchmarks]
                            stress_ds = [stress] + [b.get('stress',0) for b in benchmarks]
                            sust_ds = [sust] + [b.get('sustainability',0) for b in benchmarks]
                            eff_ds = [eff] + [b.get('efficiency',0) for b in benchmarks]
                            stage_ds = [stage] + [b.get('stage',0) for b in benchmarks]
                            
                            # Table Preparation
                            mh_b = next((b for b in benchmarks if 'maharashtra' in b['name'].lower()), None)
                            in_b = next((b for b in benchmarks if 'india' in b['name'].lower()), None)
                            
                            table_rows = [
                                "| Metric | Region Value | National/State Benchmark |",
                                "|---|---|---|",
                                f"| Stress Index % | {stress} | MH: {mh_b['stress'] if mh_b else 'N/A'} |",
                                f"| Sustainability Ratio | {sust} | India: {in_b['sustainability'] if in_b else 'N/A'} |",
                                f"| Recharge Efficiency | {eff} | MH: {mh_b['efficiency'] if mh_b else 'N/A'} |",
                                f"| Stage of Extraction % | {stage} | India: {in_b['stage'] if in_b else 'N/A'} |",
                                f"| Agri Dependency % | {round((agri/extr)*100,1) if extr else 0} | MH: {mh_b['agri_dep'] if mh_b else 'N/A'} |"
                            ]
                            
                            exps.append(f"### {loc} Groundwater Health Dashboard (2024-25)\n\n" + "\n".join(table_rows) + "\n\nDetailed Insights: ")
                            
                            # 1. Sustainability Index Comparison
                            visuals.append({"type": "bar", "title": "Sustainability Index Comparison", "labels": b_labels, "datasets": [{"label": "Index", "data": sust_ds}]})
                            
                            # 2. Recharge vs Extraction (Dual Bar - 4 Levels)
                            bal_rech = [round(rech,1)] + [round(b.get('rech_mcm',0),1) for b in benchmarks]
                            bal_extr = [round(extr,1)] + [round(b.get('extr_mcm',0),1) for b in benchmarks]
                            visuals.append({"type": "bar", "title": "Recharge vs Extraction (MCM)", "labels": b_labels, "datasets": [
                                {"label": "Recharge", "data": bal_rech},
                                {"label": "Extraction", "data": bal_extr}
                            ]})
                            
                            # 3. Stage Comparison
                            visuals.append({"type": "bar", "title": "Stage of Extraction Comparison (%)", "labels": b_labels, "datasets": [{"label": "Stage %", "data": stage_ds}]})
                            
                            # 4. Sector-wise Groundwater Use (Pie)
                            others = max(0, round(extr - (agri + dom + ind), 1))
                            visuals.append({"type": "pie", "title": f"Sector-wise Use: {loc}", "labels": ["Agriculture", "Domestic", "Industrial", "Others"], "datasets": [{"label": "MCM", "data": [round(agri,1), round(dom,1), round(ind,1), others]}]})
                            
                            # 5. Stress Index Comparison
                            visuals.append({"type": "bar", "title": "Groundwater Stress Index Comparison (%)", "labels": b_labels, "datasets": [{"label": "Stress %", "data": stress_ds}]})
                            
                            # 6. Recharge Efficiency Comparison
                            visuals.append({"type": "bar", "title": "Recharge Efficiency Comparison", "labels": b_labels, "datasets": [{"label": "Efficiency", "data": eff_ds}]})
                        
                    data = {"explanation": "\n".join(exps), "visuals": visuals}
                else: return {"explanation": "No records found.", "visuals": []}

            # Final Polish
            for vis in data.get("visuals", []):
                if vis.get("type") in ["bar", "pie", "line"]:
                    for ds in vis.get("datasets", []):
                        if "data" in ds: ds["data"] = [round(float(x), 1) if isinstance(x, (int, float)) else x for x in ds["data"]]
            return data
        except Exception as e:
            return {"explanation": response_text, "visuals": []}
