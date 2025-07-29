import streamlit as st
import numpy as np

'''
Utils = helper functions for Sperner's Game

'''


def get_css_styling():
    """Return all CSS styling for the app"""
    return """
    <style>
    .reset-button button {
        background-color: #d9534f;
        color: white;
        font-weight: bold;
        padding: 0.5em 1em;
        border-radius: 8px;
        border: none;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }
    .reset-button button:hover {
        background-color: #c9302c;
        cursor: pointer;
    }
    .player-box {
        position: absolute;
        top: 90px;
        right: 100px;
        background-color: #222;
        color: white;
        padding: 10px 15px;
        border-radius: 10px;
        z-index: 9999;
        font-weight: bold;
    }
    .color-label {
        text-align: center;
        font-weight: bold;
        color: #333;
        font-size: 1.1rem;
        padding-bottom: 10px;
    }
    .stButton > button {
        background: none !important;
        border: 3px solid transparent !important;
        border-radius: 50% !important;
        padding: 8px !important;
        font-size: 2.2rem !important;
        transition: all 0.3s ease !important;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2)) !important;
        width: 60px !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }
    .stButton > button:hover {
        transform: scale(1.1) !important;
        filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.3)) !important;
        border: 3px solid #666 !important;
    }
    .stButton > button:focus {
        border: 3px solid #333 !important;
        background-color: rgba(255,255,255,0.2) !important;
        transform: scale(1.05) !important;
        box-shadow: none !important;
    }
    </style>
    """


def reset_game_state(current_n):
    """Reset all game-related session state while preserving n value"""
    game_keys = [
        "vertex_colors", "vertex_color_n", "current_player", "color_picker", 
        "allowed_colors", "last_selected_event", "force_reset", "player1_role", 
        "player2_role", "game_started", "polychrome_count", "all_triangles"
    ]
    
    for key in game_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.n = current_n
    st.session_state.vertex_color_n = current_n
    st.session_state.force_reset = True


def initialize_session_state(n, points):
    """Initialize all session state variables for a new game"""
    st.session_state.vertex_colors = [None for _ in points]
    st.session_state.vertex_color_n = n
    st.session_state.current_player = "Player 1"
    st.session_state.color_picker = "red"
    st.session_state.game_started = False
    
    # Initialize allowed colors and triangles
    allowed_colors = assign_allowed_colors(n)
    st.session_state.allowed_colors = allowed_colors
    st.session_state.all_triangles = get_all_triangles(n)
    st.session_state.polychrome_count = 0
    
    # Pre-color 3 corners
    apex = 0
    left_corner = len(points) - n - 1
    right_corner = len(points) - 1
    st.session_state.vertex_colors[apex] = "red"
    st.session_state.vertex_colors[left_corner] = "blue"
    st.session_state.vertex_colors[right_corner] = "green"


def update_player_turn():
    """Switch to the other player"""
    st.session_state.current_player = (
        "Player 2" if st.session_state.current_player == "Player 1" else "Player 1"
    )


def set_player_roles(player1_role):
    """Set roles for both players based on player 1's choice"""
    st.session_state.player1_role = player1_role
    st.session_state.player2_role = "Minimizer" if player1_role == "Maximizer" else "Maximizer"
    st.session_state.game_started = True


def get_current_player_info():
    """Get current player's role and icon for display"""
    current_player_role = (
        st.session_state.player1_role if st.session_state.current_player == "Player 1" 
        else st.session_state.player2_role
    )
    role_icon = "🔺" if current_player_role == "Maximizer" else "🔻"
    return current_player_role, role_icon


def update_polychrome_count():
    """Update the polychrome triangle count in session state"""
    poly_triangles = get_polychrome_triangles(
        st.session_state.vertex_colors, 
        st.session_state.all_triangles
    )
    st.session_state.polychrome_count = len(poly_triangles)
    return poly_triangles


def handle_vertex_click(closest_vertex, click_x, click_y):
    """Handle clicking on a vertex, return success status and error message"""
    if st.session_state.vertex_colors[closest_vertex] is not None:
        return False, ""  # Return empty string instead of None for already-colored vertices
    
    allowed = st.session_state.allowed_colors.get(closest_vertex, {"red", "green", "blue"})
    if st.session_state.color_picker not in allowed:
        return False, f"Invalid move: You cannot color this vertex with {st.session_state.color_picker}."
    
    # Valid move - color the vertex and switch players
    st.session_state.vertex_colors[closest_vertex] = st.session_state.color_picker
    update_player_turn()
    
    # Clear saved clicks
    if "last_selected_event" in st.session_state:
        del st.session_state.last_selected_event
    
    return True, None


def create_hover_data_with_warnings(points, vertex_colors, allowed_colors, current_color):
    """Create hover data that includes warning info for invalid moves"""
    
    custom_hover_data = []
    
    for i, (px, py) in enumerate(points):
        allowed = allowed_colors.get(i, {"red", "green", "blue"})
        current_vertex_color = vertex_colors[i]
        
        # Base hover info
        base_info = f'<b>Vertex {i}</b>'# xy label, can add back x={px:.2f}<br>y={py:.2f}'
        
        if current_vertex_color is None:  # Uncolored vertex
            if current_color not in allowed:
                # Show warning for invalid color
                warning_text = f'<br><span style="color:red;font-weight:bold;">❌ Cannot use {current_color}!</span><br><span style="color:black;">Allowed: {", ".join(sorted(allowed))}</span>'
                hover_text = base_info + warning_text
            else:
                # Show valid move info
                hover_text = base_info + f'<br><span style="color:green;font-weight:bold">✓ Can use {current_color}</span><br><span style="color:black;">Allowed: {", ".join(sorted(allowed))}</span>'
        else:
            # Already colored vertex
            hover_text = base_info + f'<span style="color:{current_vertex_color};">Current: {current_vertex_color}</span>'
        
        custom_hover_data.append(hover_text)
    
    return custom_hover_data


def initialize_game(n, points):
    '''Initilize game with session state'''
    st.session_state.vertex_colors = [None for _ in points]
    st.session_state.vertex_color_n = n
    st.session_state.current_player = "Player 1"
    st.session_state.color_picker = "red"
    # roles are selected first before initialization 
    st.session_state.game_started = False

    # Pre-color 3 corners
    apex = 0
    left_corner = len(points) - n - 1
    right_corner = len(points) - 1
    st.session_state.vertex_colors[apex] = "red"
    st.session_state.vertex_colors[left_corner] = "blue"
    st.session_state.vertex_colors[right_corner] = "green"


def generate_triangle_coords(n_rows):
    '''Compute vertex positions '''
    coords = []
    x_spacing = 1.0
    y_spacing = np.sqrt(3) / 2
    for row in range(n_rows + 1):
        for col in range(row + 1):
            x = float(col * x_spacing + (n_rows - row) * x_spacing / 2)
            y = float(row * y_spacing)
            coords.append((x, y))
    return coords


def generate_edges(n_rows):
    '''Generate triangle edges'''
    edges = []
    idx = lambda r, c: r * (r + 1) // 2 + c
    for r in range(n_rows):
        for c in range(r + 1):
            i = idx(r, c)
            edges.append((i, idx(r + 1, c)))
            edges.append((i, idx(r + 1, c + 1)))
            edges.append((idx(r + 1, c), idx(r + 1, c + 1)))
    return edges

def assign_allowed_colors(n):
    '''Apply Sperner's Lemma rules'''
    allowed = {}
    total_vertices = (n + 1) * (n + 2) // 2

    apex = 0  # red
    left_corner = total_vertices - n - 1  # blue
    right_corner = total_vertices - 1    # green

    for i in range(total_vertices):
        allowed[i] = {"red", "green", "blue"}  # internal default

    # Red-Blue edge (top to bottom-left)
    for i in range(1, n):
        idx = i * (i + 1) // 2  # (row i, col 0)
        allowed[idx] = {"red", "blue"}

    # Red-Green edge (top to bottom-right)
    for i in range(1, n):
        idx = i * (i + 1) // 2 + i  # (row i, col i)
        allowed[idx] = {"red", "green"}

    # Blue-Green edge (bottom row)
    base_start = n * (n + 1) // 2
    for i in range(1, n):  # skip the two corners
        allowed[base_start + i] = {"blue", "green"}

    # Corners
    allowed[apex] = {"red"}
    allowed[left_corner] = {"blue"}
    allowed[right_corner] = {"green"}

    return allowed


def get_player_role_display(player, player1_role, player2_role):
    """Return formatted role display for a player"""
    if player == "Player 1":
        return f"Player 1 ({player1_role})"
    else:
        return f"Player 2 ({player2_role})"
    

def get_all_triangles(n):
    """Generate all triangles in the triangulation"""
    triangles = []
    idx = lambda r, c: r * (r + 1) // 2 + c

    # Generate triangles systematically
    for r in range(n):
        for c in range(r + 1):
            # Upward-pointing triangle: vertex at (r,c) with two vertices below
            v1 = idx(r, c)
            v2 = idx(r + 1, c)
            v3 = idx(r + 1, c + 1)
            triangles.append((v1, v2, v3))
            
            # Downward-pointing triangle: vertex at (r+1, c+1) with two vertices above
            # This triangle exists if c < r (not at the rightmost position of the row)
            if c < r:
                v1 = idx(r + 1, c + 1)  # bottom vertex
                v2 = idx(r, c)          # top-left vertex  
                v3 = idx(r, c + 1)      # top-right vertex
                triangles.append((v1, v2, v3))

    return triangles


def get_polychrome_triangles(vertex_colors, triangles):
    """Find triangles that have all three colors (red, green, blue)"""
    polychrome = []
    
    for tri in triangles:
        # Get the colors of the three vertices
        tri_colors = [vertex_colors[v] for v in tri]
        
        # Skip if any vertex is uncolored
        if None in tri_colors:
            continue
            
        # Check if we have exactly the three different colors
        color_set = set(tri_colors)
        if color_set == {"red", "green", "blue"}:
            print(f"Polychrome triangle: vertices {tri} -> colors {tri_colors}")
            polychrome.append(tri)
    
    return polychrome