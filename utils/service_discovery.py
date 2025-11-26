import requests
import os
import json

SERVICE_REGISTRY_URL = "http://service_registry:8010"  # Replace with the actual service registry URL

# Function to fetch services registered in Consul
def get_available_services():
    """Fetch all available services from the service registry, excluding 'consul' service."""
    try:
        # Send request to fetch services from the registry
        response = requests.get(f"{SERVICE_REGISTRY_URL}/services")
        print(f"Response from service registry: {response}")

        if response.status_code == 200:
            services = response.json()  # Returns the list of services as a dictionary
            # Filter out the consul service (you can modify this check if your service has a different name)
            filtered_services = {k: v for k, v in services.items() if 'consul' not in k.lower()}  # Exclude Consul
            # Modify service names for better UI display (e.g., replace underscores with spaces)
            formatted_services = {}
            for service_name, details in filtered_services.items():
                display_name = service_name.replace('_', ' ').title()  # Replace _ with space and capitalize each word
                formatted_services[display_name] = details  # Store with the modified name

            return formatted_services  # Return services in a usable format for the frontend
        else:
            print(f"Failed to retrieve services: {response.text}")
            return {}
    except Exception as e:
        print(f"Error contacting service registry: {e}")
        return {}

def get_service_url(service_name):
    #Fetch the service URL from the service registry microservice.
    try:
        response = requests.get(f"{SERVICE_REGISTRY_URL}/services/{service_name}")

        if response.status_code == 200:
            # Parse the JSON response to get the service URL
            service_data = response.json()
            service_url = service_data.get('service_url')
            if service_url:
                return service_url
            else:
                raise Exception(f"Service {service_name} URL not found.")
        else:
            raise Exception(f"Failed to fetch service URL for {service_name}.")
    except Exception as e:
        raise Exception(f"Error contacting service registry: {e}")


def deregister_service(service_name):
    """Deregister a service from the service registry (remove it)."""
    try:
        service_name_for_registry = service_name.replace(' ', '_')
        # Send a DELETE request to remove the service from the registry
        response = requests.delete(f"{SERVICE_REGISTRY_URL}/deregister/{service_name_for_registry}")

        if response.status_code == 200:
            print(f"Service {service_name} deregistered successfully.")
        else:
            raise Exception(f"Failed to deregister service: {response.text}")
    except Exception as e:
        raise Exception(f"Error deregistering service: {e}")