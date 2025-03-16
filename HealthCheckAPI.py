#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Import libraries

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
import random
import sqlite3
import matplotlib.pyplot as plt
import asyncio
from collections import deque
import os
import networkx as nx


# In[ ]:


#Initialization

app = FastAPI()

# Serve static files (e.g., images) from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# In[ ]:


# Sample DAG as JSON

def get_sample_graph():
    return {
        "Step 1": ["Step 2"],
        "Step 2": ["Step 3", "Step 4"],
        "Step 3": ["Step 5", "Step 7"],
        "Step 4": ["Step 9"],
        "Step 5": ["Step 6"],
        "Step 6": ["Step 10"],
        "Step 7": ["Step 8"],
        "Step 8": ["Step 10"],
        "Step 9": ["Step 10"],
        "Step 10": ["Step 11"],
        "Step 11": []
    }


# In[ ]:


# Database setup

def init_db():
    conn = sqlite3.connect("health_check.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS health_status (
        node TEXT PRIMARY KEY,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()


# In[ ]:


# Simulate health checks

async def check_health(node: str):
    await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate async delay
    return random.choice(["healthy", "unhealthy"])


# In[ ]:


# Store results in the database

def store_health_status(results: dict):
    conn = sqlite3.connect("health_check.db")
    c = conn.cursor()
    for node, status in results.items():
        c.execute("REPLACE INTO health_status (node, status) VALUES (?, ?)", (node, status))
    conn.commit()
    conn.close()


# In[ ]:


# BFS traversal and health check

async def process_graph(graph_data: dict):
    queue = deque([list(graph_data.keys())[0]])  # Start from an arbitrary node (Step 1)
    visited = set()
    tasks = {}
    
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            tasks[node] = check_health(node)
            for neighbor in graph_data.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)
    
    results = await asyncio.gather(*tasks.values())
    health_results = dict(zip(tasks.keys(), results))
    
    store_health_status(health_results)
    return health_results


# In[ ]:


# Graph visualization

def visualize_graph(graph_data, health_results):
    os.makedirs("static", exist_ok=True)  # Create 'static' directory if it doesn't exist
    
    # Create the directed graph using networkx
    G = nx.DiGraph(graph_data)
    
    # Use shell_layout for better node positioning in layers
    pos = nx.shell_layout(G)  # Layers are determined based on the node's connectivity
    
    plt.figure(figsize=(12, 10))

    # Draw the nodes with color indicating health status
    node_colors = [("green" if health_results.get(node) == "healthy" else "red") for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=4000, node_color=node_colors, edgecolors="black")

    # Draw the edges with arrows
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="black", width=2, arrowstyle='-|>', arrowsize=60, connectionstyle='arc3,rad=0.1')

    # Draw labels for nodes
    nx.draw_networkx_labels(G, pos, font_size=10, font_color="white", font_weight="bold")
    
    plt.axis("off")  # Hide the axes
    plt.tight_layout()  # Improve layout
    plt.savefig("static/dag_health.png")  # Save the graph image in the 'static' folder


# In[ ]:


# Main function

@app.get("/run_health_check")
async def run_health_check():
    graph_data = get_sample_graph()
    health_results = await process_graph(graph_data)
    visualize_graph(graph_data, health_results)
    return {"message": "Health check completed", "results": health_results, "image_url": "/static/dag_health.png"}

