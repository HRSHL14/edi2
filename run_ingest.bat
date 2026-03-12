@echo off
cd /d "f:\sem 4\edi 2 v2\groundwater_ai"
call venv\Scripts\activate.bat
python data_pipeline\fetch_ingres_data.py > ingest.log 2>&1
echo INGEST_DONE
