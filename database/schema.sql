-- Database Schema for Groundwater Data Chatbot System

CREATE TABLE IF NOT EXISTS districts (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS talukas (
    taluka_id SERIAL PRIMARY KEY,
    district_id INT REFERENCES districts(district_id),
    taluka_name VARCHAR(255) NOT NULL,
    UNIQUE(district_id, taluka_name)
);

CREATE TABLE IF NOT EXISTS groundwater_data (
    id SERIAL PRIMARY KEY,
    district VARCHAR(255),
    taluka VARCHAR(255),
    rainfall FLOAT,
    total_recharge FLOAT,
    rainfall_recharge FLOAT,
    surface_irrigation_recharge FLOAT,
    groundwater_irrigation_recharge FLOAT,
    canal_recharge FLOAT,
    water_body_recharge FLOAT,
    artificial_structure_recharge FLOAT,
    extractable_groundwater FLOAT,
    groundwater_extraction_total FLOAT,
    agriculture_extraction FLOAT,
    domestic_extraction FLOAT,
    industrial_extraction FLOAT,
    natural_discharge FLOAT,
    stage_of_extraction FLOAT,
    category VARCHAR(255),
    future_groundwater_availability FLOAT,
    year VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS groundwater_raw_json (
    id SERIAL PRIMARY KEY,
    district VARCHAR(255),
    taluka VARCHAR(255),
    year VARCHAR(50),
    json_data JSONB
);
