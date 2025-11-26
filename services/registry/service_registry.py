import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Consul URL for service registration
CONSUL_URL = "http://consul:8500/v1/agent/service/register" # For registering services
CONSUL_SERVICES_URL = "http://consul:8500/v1/catalog/services"  # For discovering services
CONSUL_SPECIFIC_SERVICE_URL = "http://consul:8500/v1/catalog/service" # For specific services details
CONSUL_DEREGISTER_URL = "http://consul:8500/v1/agent/service/deregister"  # URL for deregistering services



# Service registration model
class Service(BaseModel):
    service_name: str
    service_url: str
    port: int

@app.post("/register")
def register_service(service: Service):
    """Register a service with Consul."""
    payload = {
        "ID": service.service_name,
        "Name": service.service_name,
        "Address": service.service_url,
        "Port": service.port,
        "Check": {
            "http": f"http://{service.service_url}:{service.port}/health",
            "interval": "20s"  # Health check frequency
        }
    }
    response = requests.put(CONSUL_URL, json=payload)

    if response.status_code == 200:
        return {"message": f"Service {service.service_name} registered successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to register service with Consul")


@app.get("/services/{service_name}")
def get_service_url(service_name: str):
    try:
        # Query Consul for the service details
        response = requests.get(f"{CONSUL_SPECIFIC_SERVICE_URL}/{service_name}")
        if response.status_code == 200:
            services = response.json()
            if services:
                # Take the first service instance
                service_address = services[0]["ServiceAddress"]
                service_port = services[0]["ServicePort"]
                service_url = f"http://{service_address}:{service_port}"
                return {"service_url": service_url}
            else:
                raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch from Consul")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Consul: {str(e)}")

@app.delete("/deregister/{service_name}")
def deregister_service(service_name: str):
    try:
        response = requests.put(f"{CONSUL_DEREGISTER_URL}/{service_name}")
        if response.status_code == 200:
            return {"message": f"Service {service_name} deregistered successfully from Consul."}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to deregister {service_name} from Consul")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deregistering service from Consul: {str(e)}")


@app.get("/services")
def get_services():
    try:
        response = requests.get(CONSUL_SERVICES_URL)
        if response.status_code == 200:
            return response.json()  # Returns a dictionary of services registered in Consul
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve services from Consul")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving services from Consul: {e}")


@app.get("/health/{service_name}")
def health_check(service_name: str):
    # Consul health check endpoint
    health_check_url = f"http://consul:8500/v1/health/service/{service_name}"

    try:
        response = requests.get(health_check_url)
        if response.status_code == 200:
            # Service is healthy
            return {"status": "healthy", "service_name": service_name}
        else:
            # Service is unhealthy or doesn't exist
            return {"status": "unhealthy", "service_name": service_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Consul health check: {e}")
