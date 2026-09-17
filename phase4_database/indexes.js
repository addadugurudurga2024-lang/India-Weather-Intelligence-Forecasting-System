// MongoDB Index Specifications for India Weather Intelligence
// Execute in mongosh or MongoDB Compass Shell:

use india_weather_intelligence;

// 1. Stations Collection Indexes
db.stations.createIndex({ station_id: 1 }, { unique: true, name: "idx_station_id_unique" });
db.stations.createIndex({ state: 1, district: 1 }, { name: "idx_state_district" });
db.stations.createIndex({ location: "2dsphere" }, { name: "idx_geo_2dsphere" });
db.stations.createIndex({ elevation_m: 1 }, { name: "idx_elevation" });

// 2. Weather Observations Collection Indexes
db.weather_observations.createIndex(
  { station_id: 1, date_of_record: -1 },
  { unique: true, name: "idx_station_date_unique" }
);
db.weather_observations.createIndex({ date_of_record: -1 }, { name: "idx_date_desc" });
db.weather_observations.createIndex({ state: 1, date_of_record: -1 }, { name: "idx_state_date" });
db.weather_observations.createIndex({ rainfall: 1 }, { sparse: true, name: "idx_rainfall_sparse" });

// 3. Forecast Results Collection Indexes
db.forecast_results.createIndex(
  { station_id: 1, forecast_date: -1 },
  { name: "idx_forecast_station_date" }
);
db.forecast_results.createIndex({ forecast_date: 1 }, { name: "idx_forecast_date" });

// 4. Model Metadata Collection Indexes
db.model_metadata.createIndex({ model_id: 1 }, { unique: true, name: "idx_model_id_unique" });
db.model_metadata.createIndex({ target: 1, status: 1 }, { name: "idx_target_status" });

print("All compound and geospatial indexes created successfully!");
