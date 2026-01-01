from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, households, medications, tags, instructions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(households.router, prefix="/households", tags=["households"])
api_router.include_router(medications.router, prefix="/households", tags=["medications"])
api_router.include_router(tags.router, prefix="/households", tags=["tags"])
api_router.include_router(instructions.router, prefix="/instructions", tags=["instructions"])

# Add global DRLZ endpoints (not household-specific)
from fastapi import APIRouter as GlobalAPIRouter, Depends, HTTPException, status, Query
from app.core.deps import get_current_active_user
from app.models.user import User

drlz_router = GlobalAPIRouter()

@drlz_router.get("/search-drlz")
async def search_drlz_medications(
    query: str = Query(..., description="Medication name to search for"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
):
    """Search for medications in the Ukrainian DRLZ registry"""
    try:
        from app.services.drlz_csv import drlz_service
        
        # Get medication details with instructions
        medications = drlz_service.get_medication_with_instructions(query, limit)
        
        return {
            "query": query,
            "medications": medications,
            "total": len(medications)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching DRLZ: {str(e)}"
        )

@drlz_router.get("/drlz-stats")
async def get_drlz_statistics(
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics about the DRLZ medication database"""
    try:
        from app.services.drlz_csv import drlz_service
        
        stats = drlz_service.get_statistics()
        return {
            "database_stats": stats,
            "status": "loaded" if stats['total_medications'] > 0 else "not_loaded"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting DRLZ statistics: {str(e)}"
        )

api_router.include_router(drlz_router, prefix="/drlz", tags=["drlz"])
