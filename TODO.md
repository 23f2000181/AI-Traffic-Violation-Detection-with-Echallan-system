# TODO - Traffic Violation Detection Web Application

## Information Gathered

- Backend is Python Flask with a basic file upload route.
- MongoDB integration exists with collections for violations, challans, owners, vehicles, and manual reviews.
- CentralDetectionManager in central_detection_manager.py handles detection for license plate, helmet, and red light violations.
- Current backend API is minimal, lacks full REST endpoints as specified.
- Frontend React app does not exist yet.
- File storage path for uploads is ./uploads; processed images go to results/combined or equivalent.
- Environment variables for MongoDB and Twilio are managed.
- Detection results are saved as JSON files and images.
- The system requires paginated, filtered violation queries, config management, and statistics endpoints.
- UI requires modern React components for upload, results display, history, and dashboards.

## Detailed Plan

### Backend - Flask API

1. Refactor and extend Flask API to implement these endpoints:

   - POST `/api/upload-image`: Accept image upload multipart/form-data, save file to uploads, process with CentralDetectionManager, save results to MongoDB (with schema as specified), return annotated image and detection results JSON.

   - GET `/api/violations`: Paginated query to MongoDB violations collection supporting filters on date range, violation type, confidence score.

   - GET `/api/violations/<id>`: Return detailed info for a specific violation including image URLs.

   - GET `/api/statistics`: Aggregate and return summary statistics for dashboard (totals by violation type, trends).

   - PUT `/api/config`: Update system config such as model paths, confidence thresholds.

   - DELETE `/api/violations/<id>`: Delete a violation record by ID.

2. Adjust MongoDB schema in violations collection to match prompt, with fields for timestamp, image_path, processed_image_path, detection_results (license_plates, helmet_violations, red_light_violations), processing_time, status.

3. Implement proper error handling, validation, and logging.

4. Manage file storage structure (uploads/, processed/) with local filesystem readiness for cloud migration.

5. Integration with CentralDetectionManager for detection logic.

### Frontend - React.js

1. Create React app structure with components:

   - UploadZone: Drag-and-drop (+ file browse) image upload with validation and progress.

   - ResultsViewer: Side-by-side original and processed images with bounding boxes and confidence overlays; export options.

   - ViolationTable: Paginated, searchable, sortable table with filters and bulk actions.

   - Dashboard: Summary cards, charts for trends, recent activity timeline.

   - Navigation: App header with links.

2. Use modern UI component library (e.g., Material-UI or Chakra-UI).

3. Implement frontend API service to interact with backend REST endpoints.

4. Make frontend responsive and mobile-friendly.

### Additional Points

- Add environment configuration for upload/processed folder paths, MongoDB URI.

- Include unit and integration tests for backend endpoints and React components.

- Set up Dockerfile and docker-compose for backend, frontend, and MongoDB.

- Add health check and logging endpoints.

- Documentation for setup and deployment.

## Dependent Files to be Edited or Created

- app.py (extend and refactor backend API)

- central_detection_manager.py (minor changes if needed for data saving)

- New React frontend directory (e.g., frontend/ or src/ with React app structure)

- config.json (for configs if needed)

- TODO.md (tracking task progress)

## Followup Steps

- Implement backend API endpoints and test them with tools like Postman.

- Develop React frontend components incrementally connecting to backend.

- Write unit and integration tests.

- Configure Docker and deployment scripts.

- Provide documentation.

---

Please review this plan and confirm to proceed with implementation, or let me know if you want to prioritize specific parts first.
