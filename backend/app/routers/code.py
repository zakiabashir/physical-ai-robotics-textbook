"""
Code execution API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from fastapi import Body

from ..services.code_execution import CodeExecutionService
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/code", tags=["Code Execution"])
code_service = CodeExecutionService()


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    language: str = Field(default="python", description="Programming language")
    files: Optional[List[Dict[str, str]]] = Field(None, description="Additional files for execution")
    timeout: Optional[int] = Field(None, description="Execution timeout in seconds")


class CodeExecutionResponse(BaseModel):
    id: str
    success: bool
    output: str
    error: str
    execution_time: float
    language: str


router = APIRouter()


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute code in a WebContainer"""

    try:
        # Validate code first
        validation = await code_service.validate_code(request.code, request.language)

        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Code validation failed",
                    "details": validation["errors"] + validation["security_issues"]
                }
            )

        # Execute the code
        result = await code_service.execute_code(
            code=request.code,
            language=request.language,
            files=request.files,
            timeout=request.timeout
        )

        return CodeExecutionResponse(**result)

    except Exception as e:
        logger.error(f"Code execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}"
        )


@router.get("/status/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get the status of a code execution"""

    try:
        status = await code_service.get_execution_status(execution_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get execution status: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )


@router.delete("/{execution_id}")
async def kill_execution(execution_id: str):
    """Kill a running code execution"""

    try:
        success = await code_service.kill_execution(execution_id)
        if success:
            return {"message": f"Execution {execution_id} killed successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail="Execution not found or not running"
            )

    except Exception as e:
        logger.error(f"Failed to kill execution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to kill execution"
        )


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""

    try:
        languages = await code_service.get_supported_languages()
        return {"languages": languages}

    except Exception as e:
        logger.error(f"Failed to get supported languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get supported languages"
        )


@router.post("/validate")
async def validate_code(
    code: str = Body(..., description="Code to validate"),
    language: str = Body(default="python", description="Programming language")
):
    """Validate code for security and syntax"""

    try:
        validation = await code_service.validate_code(code, language)
        return validation

    except Exception as e:
        logger.error(f"Code validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code validation failed: {str(e)}"
        )


@router.get("/ros2/environment")
async def get_ros2_environment():
    """Get ROS 2 environment configuration"""

    try:
        env = await code_service.create_ros2_environment()
        return env

    except Exception as e:
        logger.error(f"Failed to get ROS 2 environment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get ROS 2 environment"
        )