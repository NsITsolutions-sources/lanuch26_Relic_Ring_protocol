import json
import math
import heapq

class Planet:
    def __init__(self, data):
        self.id = data['id']
        self.codex = data['codex']
        self.x = data['x']
        self.y = data['y']
        self.r = data['radius_km']
        self.towers = data['active_towers']
        self.h = data['atmosphere_thickness_km']
        self.n = data['refraction_index']

class RelicRingProtocol:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        self.meta = config['universe_metadata']
        self.S = self.meta['coordinate_scale_unit_km']
        self.C = self.meta['speed_of_light_kms']
        self.max_void_hop = self.meta['max_void_hop_distance_km']
        self.tower_delay = self.meta['tower_processing_delay_ms']
        self.fiber_speed_fraction = self.meta['fiber_speed_fraction']
        
        self.planets = {p_data['id']: Planet(p_data) for p_data in config['nodes']}
        self.active_nodes = set(self.planets.keys()) # For Chaos Testing (node failures)

    def revive_node(self, node_id):
        """Revive a previously disabled node."""
        if node_id in self.planets and node_id not in self.active_nodes:
            self.active_nodes.add(node_id)
            print(f"✅ RECOVERY: Node '{node_id}' is back online!")
        else:
            print(f"Node '{node_id}' is already active or does not exist.")

    def calculate_void_distance(self, p1, p2):
        """Calculates Void Distance (L) between two planets."""
        dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2) * self.S
        L = dist - (p1.r + p1.h) - (p2.r + p2.h)
        return max(0, L)

    def calculate_tv(self, p1, p2, L):
        """Calculates Void Travel Time (Tv)."""
        return ((p1.h * p1.n) + (p2.h * p2.n) + L) / self.C

    def calculate_tp(self, planet, num_towers_hit):
        """Calculates Internal Crust Transit Time (Tp) for simplification in routing."""
        # Note: In a full geometric calculation, 's' (segments) depends on line of sight.
        # For base shortest-path estimation, we assume minimum tower hops.
        s = num_towers_hit - 1 if num_towers_hit > 1 else 0
        m = num_towers_hit
        
        fiber_delay = (2 * math.pi * planet.r * s) / (planet.towers * self.fiber_speed_fraction * self.C)
        processing_delay = m * (self.tower_delay / 1000) # Convert ms to seconds
        return fiber_delay + processing_delay

    def get_shortest_path(self, start_id, end_id):
        """Dijkstra's Algorithm to find the lowest-latency route."""
        if start_id not in self.active_nodes or end_id not in self.active_nodes:
            return None, float('inf')

        distances = {node: float('inf') for node in self.active_nodes}
        distances[start_id] = 0
        previous_nodes = {node: None for node in self.active_nodes}
        pq = [(0, start_id)]

        while pq:
            current_dist, current_id = heapq.heappop(pq)
            if current_dist > distances[current_id]: continue
            if current_id == end_id: break

            p1 = self.planets[current_id]
            for neighbor_id in self.active_nodes:
                if neighbor_id == current_id: continue
                
                p2 = self.planets[neighbor_id]
                L = self.calculate_void_distance(p1, p2)
                
                # Constraint: Wireless Signal Threshold
                if L > self.max_void_hop: continue
                
                # Assume 2 towers hit per transit for simplification (Entry & Exit)
                Tp = self.calculate_tp(p1, 2) 
                Tv = self.calculate_tv(p1, p2, L)
                
                weight = Tp + Tv
                distance = current_dist + weight

                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    previous_nodes[neighbor_id] = current_id
                    heapq.heappush(pq, (distance, neighbor_id))

        # Reconstruct path
        path, current = [], end_id
        while current is not None:
            path.append(current)
            current = previous_nodes[current]
        path = path[::-1]
        
        return (path, distances[end_id]) if path[0] == start_id else (None, float('inf'))

    @staticmethod
    def encode_payload(text, base):
        """Converts ASCII text to the required numeric base."""
        def to_base(n, b):
            if n == 0: return "0"
            digits = []
            while n:
                digits.append(int(n % b))
                n //= b
            # Handle bases up to 16
            return "".join(str(x) if x < 10 else chr(ord('A') + x - 10) for x in digits[::-1])
        
        return [to_base(ord(char), base) for char in text]

    def transmit_packet(self, origin, destination, payload_text):
        """Simulates the full transmission workflow."""
        print(f"\n--- Initiating Transmission: {origin} -> {destination} ---")
        path, total_latency = self.get_shortest_path(origin, destination)
        
        if not path:
            print("ERROR: Route undeliverable! No valid path found.")
            return

        print(f"Optimal Route Found: {' -> '.join(path)}")
        print(f"Total Estimated Latency: {total_latency:.4f} seconds")
        
        # Step-by-step trace
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i+1]
            current_planet = self.planets[current_id]
            next_planet = self.planets[next_id]
            
            print(f"\n[Node: {current_id}] Internal Representation (ASCII): {[ord(c) for c in payload_text]}")
            encoded = self.encode_payload(payload_text, next_planet.codex)
            print(f"[Node: {current_id}] Next Hop Codex (Base {next_planet.codex}): {encoded}")
            
            L = self.calculate_void_distance(current_planet, next_planet)
            print(f"[Void] Beaming to {next_id}... (Distance: {L:,.2f} km)")
            
        print(f"\n[Node: {destination}] Payload Delivered Successfully: '{payload_text}'")

    def kill_node(self, node_id):
        """For Chaos Testing (M4 milestone)."""
        if node_id in self.active_nodes:
            self.active_nodes.remove(node_id)
            print(f"⚠️  CRITICAL: Node '{node_id}' has gone offline!")

# --- EXECUTION / DEMONSTRATION ---
if __name__ == "__main__":
    # M1: Universe Initialization
    print("M1: Initializing Relic Ring Network...")
    network = RelicRingProtocol('universe-config.json')
    
    # M2 & M3: Multi-Hop Proof and Latency Breakdown
    network.transmit_packet("Aegis", "Caelum", "Hello world")
    
    # M4: Chaos Test (Dynamic Rerouting)
    print("\n--- Initiating Chaos Test ---")
    network.kill_node("Boreas")  # Simulate node failure
    network.transmit_packet("Aegis", "Caelum", "Hello world")