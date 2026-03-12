@echo off
cd /d "f:\sem 4\edi 2 v2\groundwater_ai"
call venv\Scripts\activate.bat
python data_pipeline\test_payloads.py > test_api.log 2>&1
echo TEST_DONE
