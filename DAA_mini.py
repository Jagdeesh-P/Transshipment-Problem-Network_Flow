import tkinter as tk
from pulp import *
import random

# Define the network with Tamil Nadu city names
nodes = ['S1:Chennai', 'S2:Salem', 'S3:Nagercoil',
         'T1:Madurai', 'T2:Erode', 'T3:Tuticorin',
         'D1:Coimbatore', 'D2:Tirunelveli', 'D3:Trichy']

# Define the supply, transshipment, and demand nodes
supply_nodes = ['S1:Chennai', 'S2:Salem', 'S3:Nagercoil']
transshipment_nodes = ['T1:Madurai', 'T2:Erode', 'T3:Tuticorin']
demand_nodes = ['D1:Coimbatore', 'D2:Tirunelveli', 'D3:Trichy']

# Generate random supply and demand
supply = {node: random.randint(30, 50) for node in supply_nodes}
demand = {node: random.randint(30, 50) for node in demand_nodes}

# Ensure total supply equals total demand by balancing among all sources and destinations
total_supply = sum(supply.values())
total_demand = sum(demand.values())
difference = total_supply - total_demand

if difference > 0:
    for key in demand:
        demand[key] += difference // len(demand)
elif difference < 0:
    for key in supply:
        supply[key] += -difference // len(supply)

# Print input data
print("Nodes:", nodes)
print("Supply:", supply)
print("Demand:", demand)

# Define the cost matrix for logical pairs, including transshipment points
costs = {
    ('S1:Chennai', 'T1:Madurai'): 10, ('S1:Chennai', 'T2:Erode'): 6, ('S1:Chennai', 'T3:Tuticorin'): 13,
    ('S1:Chennai', 'D1:Coimbatore'): 12, ('S1:Chennai', 'D2:Tirunelveli'): 20, ('S1:Chennai', 'D3:Trichy'): 12,
    ('S2:Salem', 'T1:Madurai'): 6, ('S2:Salem', 'T2:Erode'): 2, ('S2:Salem', 'T3:Tuticorin'): 12,
    ('S2:Salem', 'D1:Coimbatore'): 8, ('S2:Salem', 'D2:Tirunelveli'): 20, ('S2:Salem', 'D3:Trichy'): 10,
    ('S3:Nagercoil', 'T1:Madurai'): 5, ('S3:Nagercoil', 'T2:Erode'): 12, ('S3:Nagercoil', 'T3:Tuticorin'): 3,
    ('S3:Nagercoil', 'D1:Coimbatore'): 18, ('S3:Nagercoil', 'D2:Tirunelveli'): 6, ('S3:Nagercoil', 'D3:Trichy'): 10,
    ('T1:Madurai', 'D1:Coimbatore'): 8, ('T1:Madurai', 'D2:Tirunelveli'): 4, ('T1:Madurai', 'D3:Trichy'): 2,
    ('T2:Erode', 'D1:Coimbatore'): 3, ('T2:Erode', 'D2:Tirunelveli'): 9, ('T2:Erode', 'D3:Trichy'): 3,
    ('T3:Tuticorin', 'D1:Coimbatore'): 11, ('T3:Tuticorin', 'D2:Tirunelveli'): 2, ('T3:Tuticorin', 'D3:Trichy'): 9,
}

# Create a LP minimization problem
prob = LpProblem("Transshipment Problem", LpMinimize)

# Define decision variables for the flow between nodes
flow = LpVariable.dicts("Flow", (nodes, nodes), lowBound=0, cat='Continuous')

# Add the objective function to the problem with costs
prob += lpSum([flow[i][j] * costs[(i, j)] for i in nodes for j in nodes if (i, j) in costs])

# Add the supply and demand constraints
for node in nodes:
    if node in supply:
        prob += lpSum([flow[node][j] for j in nodes if (node, j) in costs]) == supply[node]
    elif node in demand:
        prob += lpSum([flow[i][node] for i in nodes if (i, node) in costs]) == demand[node]
    else:  # Transshipment nodes
        prob += lpSum([flow[i][node] for i in nodes if (i, node) in costs]) == lpSum([flow[node][j] for j in nodes if (node, j) in costs])

# Solve the problem
prob.solve()
# Print the optimal flow
print("\nOptimal Flow:")
for v in prob.variables():
    if v.varValue > 0:
        print(f"{v.name} = {v.varValue}")


# Create a Tkinter GUI
root = tk.Tk()
root.title("Transshipment Problem")

canvas = tk.Canvas(root, width=1000, height=800, bg='white')
canvas.pack()

# Display the network with better visualization using provided node_positions
node_positions = {
    'S1:Chennai': (850, 80), 'S2:Salem': (300, 240), 'S3:Nagercoil': (380, 700),
    'T1:Madurai': (400, 450), 'T2:Erode': (180, 250), 'T3:Tuticorin': (500, 550),
    'D1:Coimbatore': (80, 300), 'D2:Tirunelveli': (400, 600), 'D3:Trichy': (480, 350),
}

# Draw nodes and labels with supply and demand information
for node, pos in node_positions.items():
    canvas.create_oval(pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10, fill='blue')
    canvas.create_text(pos[0], pos[1] + 20, text=node, fill='black', font=('Arial', 10, 'bold'))
    if node in supply_nodes:
        canvas.create_text(pos[0] - 20, pos[1] - 20, text=f"Supply: {supply[node]}", fill='green',
                           font=('Arial', 8, 'italic'))
    elif node in demand_nodes:
        canvas.create_text(pos[0] + 20, pos[1] -20, text=f"Demand: {demand[node]}", fill='red', font=('Arial', 8, 'italic'))

# Function to animate flow with correct parsing
def animate_flow():
    for v in prob.variables():
        if v.varValue > 0:
            _, start_node, end_node = v.name.split('_')
            start_pos = node_positions[start_node]
            end_pos = node_positions[end_node]
            arrow_id = canvas.create_line(start_pos[0], start_pos[1], end_pos[0], end_pos[1], arrow=tk.LAST,
                                          fill='red')

            # Animate arrow movement
            for i in range(1, 51):  # Number of steps for animation
                x = start_pos[0] + (end_pos[0] - start_pos[0]) * i / 50
                y = start_pos[1] + (end_pos[1] - start_pos[1]) * i / 50
                canvas.coords(arrow_id, start_pos[0], start_pos[1], x, y)
                root.update()
                root.after(20)  # Animation speed (milliseconds)

# Call the animation function after drawing nodes and labels
animate_flow()

root.mainloop()

