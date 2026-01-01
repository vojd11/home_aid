from fastapi import APIRouter

router = APIRouter()


@router.post("/{household_id}/tags")
async def create_tag():
    """Create a new tag"""
    return {"message": "Create tag endpoint"}


@router.delete("/{household_id}/tags/{tag_id}")
async def delete_tag():
    """Delete a tag"""
    return {"message": "Delete tag endpoint"}
