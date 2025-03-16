# HealthCheckAPI
A Python web API that checks the health of a system comprising of a multi-level correlated components in the form of a Directed Acyclic Graph (DAG).

This FastAPI-based Python application does the following:

1. Defines a Directed Acyclic Graph (DAG) through a JSON file where the nodes represent multi-level correlated components.
2. Performs a simulated health check on each node in the graph.
3. Stores health status results in an SQLite database.
4. Generates a graphical visualization of the DAG, highlighting failed components in red.
5. Provides an API endpoint (/run_health_check) to trigger the health check and return results in the form of a database and PNG file(picture).
