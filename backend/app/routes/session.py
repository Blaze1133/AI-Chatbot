from fastapi import APIRouter
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/api/session", tags=["session"])

@router.post("/clear")
async def clear_session():
    """Clear all session data - useful for testing or manual cleanup"""
    try:
        vector_store_service.clear_session()
        return {"status": "success", "message": "Session data cleared successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to clear session: {str(e)}"}

@router.get("/info")
async def get_session_info():
    """Get current session information"""
    return {
        "session_id": vector_store_service.session_id,
        "temp_dir": vector_store_service.temp_dir,
        "vector_store_initialized": vector_store_service._vector_store is not None
    }

@router.get("/test")
async def test_session_storage():
    """Test that session storage is working"""
    return {
        "message": "Session storage is working!",
        "session_id": vector_store_service.session_id,
        "temp_dir_exists": os.path.exists(vector_store_service.temp_dir),
        "temp_dir": vector_store_service.temp_dir,
        "session_created_at": vector_store_service.session_created_at.isoformat(),
        "session_duration_minutes": vector_store_service.session_duration.total_seconds() / 60,
        "note": "Session auto-clears after 30 minutes or when forced"
    }

@router.post("/new")
async def force_new_session():
    """Force create a new session (clears all data)"""
    vector_store_service.force_new_session()
    return {
        "message": "New session created!",
        "new_session_id": vector_store_service.session_id,
        "temp_dir": vector_store_service.temp_dir
    }
