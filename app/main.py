from fastapi import FastAPI
from app.routes.customers import router as customer_router
from app.routes.orders import router as order_router
from app.routes.payments import router as payment_router
from app.routes.refunds import router as refund_router
from app.routes.support_cases import router as support_case_router
from app.routes.resolution import router as resolution_router
from app.routes.ai_resolution import router as ai_resolution_router
from app.routes.human_escalations import (
    router as human_escalation_router,
)
app = FastAPI(
    title= "ResolveAI",
    description= "ResolveAI is a powerful AI-powered platform that provides advanced solutions for data analysis, natural language processing, and machine learning. With ResolveAI, users can easily analyze large datasets, extract valuable insights, and build intelligent applications with ease.",
    version= "1.0.0",
)

app.include_router(customer_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(refund_router)
app.include_router(support_case_router)
app.include_router(resolution_router)
app.include_router(ai_resolution_router)
app.include_router(human_escalation_router)

@app.get("/health")
def health_check()-> dict[str, str]:
    """
    Health check endpoint to verify the status of the application.
    
    Returns:
        dict: A dictionary containing the status of the application.
    """
    return {"status": "healthy"}