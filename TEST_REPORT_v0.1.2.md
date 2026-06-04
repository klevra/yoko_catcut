# Yoko CatCut v0.1.2 Functional Test Report

Date: 2026-06-04
Test Environment: macOS (Docker Desktop)
Backend Port: 8000
Frontend Port: 4000

## Test Cases

### 1. ✅ Service Startup
- **Test**: Start services via `start.command`
- **Result**: PASS
- **Details**: Both backend and frontend containers started successfully in ~30 seconds.

### 2. ✅ Frontend Accessibility
- **Test**: Access frontend at http://localhost:4000
- **Result**: PASS
- **Details**: Frontend loads HTML correctly (Vite dev server responding with index.html and React app)

### 3. ✅ Project Creation
- **Endpoint**: POST /api/v1/projects
- **Request**: `{"user_id": "test_user", "project_name": "test_project_001"}`
- **Result**: PASS (HTTP 200)
- **Response**: Project and workspace directories created successfully.

### 4. ❌ Project List Retrieval (ISSUE FOUND)
- **Endpoint**: GET /api/v1/projects/{user_id}
- **Result**: FAIL (HTTP 400)
- **Error**: `"'str' object has no attribute 'isoformat'"`
- **Root Cause**: Datetime serialization issue in project service
- **Impact**: Frontend cannot fetch project list; blocks dashboard display.

### 5. ❌ Project Detail Retrieval (ISSUE FOUND)
- **Endpoint**: GET /api/v1/projects/{user_id}/{project_name}
- **Result**: FAIL (HTTP 404)
- **Root Cause**: Likely same datetime serialization issue.

### 6. ✅ File Upload (MP4 Test - Case 3)
- **Endpoint**: POST /api/v1/uploads
- **Request**: Multipart form with test_video.mp4 (140 bytes)
- **Result**: PASS (HTTP 200)
- **Verification**: File confirmed saved to workspace directory
- **Path**: workspace/test_user/test_project_001/original/{upload_id}.mp4

### 7. 🔄 Drag-Drop Upload (BLOCKED)
- **Status**: Cannot test in headless mode
- **Recommendation**: Requires browser automation or manual testing

## Issues Found

### Issue #1: Datetime Serialization Error [HIGH PRIORITY]
- **Affected Endpoints**: GET /api/v1/projects/{user_id}, GET /api/v1/projects/{user_id}/{project_name}
- **Problem**: Response models return datetime fields improperly formatted
- **Fix Required**: Convert datetime values properly in serialization

### Issue #2: Frontend Project Display [HIGH PRIORITY]
- **Impact**: Dashboard cannot display project list (blocked by Issue #1)

## Summary

| Feature         | Status | Notes                           |
|-----------------|--------|--------------------------------|
| Service Startup | ✅     | All containers running         |
| Frontend Load   | ✅     | React app loaded               |
| Project Create  | ✅     | POST successful                |
| Project List    | ❌     | Datetime bug                   |
| Project Detail  | ❌     | Datetime bug                   |
| File Upload     | ✅     | MP4 saved successfully         |
| Drag-Drop       | 🔄     | Manual test needed             |

## Next Steps

1. Fix datetime serialization in project service
2. Re-test GET endpoints
3. Manual browser testing for drag-drop feature
4. Consider v0.1.3 patch release
