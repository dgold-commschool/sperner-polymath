import streamlit as st
import plotly.graph_objects as go
import numpy as np
from streamlit_plotly_events import plotly_events
import utils

# Page layout
st.set_page_config(layout="wide")
st.title("The Sperner Game - Maximizer vs Minimizer")

# Add CSS styling
st.markdown(utils.get_css_styling(), unsafe_allow_html=True)

with st.expander("How to Play:"):
    st.markdown("""
    **Goal:**  
    Complete the triangle by assigning colors to the inner vertices according to **Sperner's Lemma** rules. One player acts as a maximizer, attempting to maximize the number of polychrome (tricolored) 
    triangles on the board after all vertices have been colored. The other player acts as the minimizer. Player 1 starts the game by clicking the button indicating whether they are a maximizer or minimizer, and player 2 is assigned the other role.
    
    **Rules:**
    - The triangle has 3 colored corners: red, green, and blue.
    - Each edge of the triangle can only use the colors of its endpoints.
    - Interior vertices may use any of the three colors.
    - Players take turns coloring uncolored vertices, following the rules above.
    - The game ends when all vertices are colored. 
    - For this version of Sperner's game, the **Maximizer** wins if the number of polychrome triangles is greater than the midpoint number that can be formed at that triangulation level (rework this definition)

    **Tip:** Click a vertex to color it. Use the buttons above to select your current color.
    """)

# Retrieve n from session state or default to 5
default_n = st.session_state.get("n", 5)
st.session_state.n = default_n
n = st.slider("Triangulation level n", 2, 8, value=default_n)

# Update session state with the current slider value
st.session_state.n = n

top_left = st.columns([2, 8])[0]
with top_left:
    if st.button("🔄 Reset Game", key="reset_btn", help="Restart the game"):
        utils.reset_game_state(n)
        st.rerun()

    st.markdown('<div class="reset-button"></div>', unsafe_allow_html=True)

# Reset state if triangulation level changes 
if "vertex_color_n" in st.session_state and st.session_state.vertex_color_n != n:
    st.session_state.clear()
    st.session_state.n = n
    st.session_state.vertex_color_n = n
    st.session_state.force_reset = True
    st.rerun()

# Geometry
points = utils.generate_triangle_coords(n)
edges = utils.generate_edges(n)

# Initialize session state
if (
    "vertex_colors" not in st.session_state
    or "vertex_color_n" not in st.session_state
    or st.session_state.vertex_color_n != n
):
    utils.initialize_session_state(n, points)

plot_colors = [color if color else "white" for color in st.session_state.vertex_colors]

# Live Polychrome Count Display
poly_triangles = utils.update_polychrome_count()

# Role Selection (before game starts)
if not st.session_state.get("game_started", False):
    st.markdown("---")
    st.markdown("### Role Selection")
    st.markdown("**Player 1**, choose your role to start the game:")
    
    role_col1, role_col2, role_col3 = st.columns([0.3, 0.3, 2.4])
    
    with role_col1:
        if st.button("🔺 Maximizer", key="maximizer_btn", help="Try to maximize polychrome triangles"):
            utils.set_player_roles("Maximizer")
            st.rerun()
    
    with role_col2:
        if st.button("🔻 Minimizer", key="minimizer_btn", help="Try to minimize polychrome triangles"):
            utils.set_player_roles("Minimizer")
            st.rerun()
    
    with role_col3:
        st.markdown("&nbsp;&nbsp;**Player 2** will automatically be assigned the opposite role.")
    
    # Show the triangle but disable interaction
    st.markdown("---")
    st.markdown("*Select your role above to begin playing*")
    
    # Get hover data with warnings for role selection phase
    hover_data = utils.create_hover_data_with_warnings(
        points, 
        st.session_state.vertex_colors, 
        st.session_state.allowed_colors, 
        st.session_state.color_picker
    )
    
    fig = go.Figure()
    x, y = zip(*points)

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers',
        marker=dict(size=16, color=plot_colors, line=dict(color='black', width=1)),
        text=hover_data,
        hovertemplate='%{text}<extra></extra>',
        showlegend=False,
        name='vertices'
    ))

    for i, j in edges:
        xi, yi = points[i]
        xj, yj = points[j]
        fig.add_trace(go.Scatter(
            x=[xi, xj], y=[yi, yj],
            mode='lines',
            line=dict(color='grey', width=1),
            hoverinfo='skip',
            showlegend=False
        ))
    fig.update_layout(
        height=600,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(visible=False, scaleanchor='y', scaleratio=1, constrain='domain'),
        yaxis=dict(visible=False, constrain='domain', autorange='reversed'),
        plot_bgcolor='rgb(40,40,40)',
        title=dict(text="Waiting for role selection...", x=0.5, font=dict(color='white'))
    )

    st.plotly_chart(fig, use_container_width=True)
    st.stop()

# Game Interface (only shown after role selection)
st.markdown("---")

# Display current roles
st.markdown(f"### Current Roles")
role_icon = "🔺" if st.session_state.player1_role == "Maximizer" else "🔻"
st.markdown(f"**Player 1**: {role_icon} {st.session_state.player1_role}")
role_icon = "🔺" if st.session_state.player2_role == "Maximizer" else "🔻"
st.markdown(f"**Player 2**: {role_icon} {st.session_state.player2_role}")

st.markdown("---")

# Centered label
st.markdown("<div style='text-align:center; font-weight:bold; font-size:1.1rem;'>Choose your color:</div>", unsafe_allow_html=True)

# Center real buttons without using columns
center, buttons, _ = st.columns([4, 2, 4])

with buttons:
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🔴", key="red_btn"):
            st.session_state.color_picker = "red"
            st.rerun()
    with b2:
        if st.button("🟢", key="green_btn"):
            st.session_state.color_picker = "green"
            st.rerun()
    with b3:
        if st.button("🔵", key="blue_btn"):
            st.session_state.color_picker = "blue"
            st.rerun()

# Get current player info for display
current_player_role, role_icon = utils.get_current_player_info()

# Floating player box
st.markdown(
    f"""
    <div class="player-box">
    {st.session_state.current_player} ({role_icon} {current_player_role})<br>
    Using Color: <span style='color:{st.session_state.color_picker}'>{st.session_state.color_picker}</span><br>
    Polychrome Count: <span style= font-weight: bold;'>{st.session_state.polychrome_count}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Get hover data with warnings for game phase
hover_data = utils.create_hover_data_with_warnings(
    points, 
    st.session_state.vertex_colors, 
    st.session_state.allowed_colors, 
    st.session_state.color_picker
)

# Plotly chart / visualization of board
fig = go.Figure()
x, y = zip(*points)
fig.add_trace(go.Scatter(
    x=x, y=y,
    mode='markers',
    marker=dict(size=16, color=plot_colors, line=dict(color='black', width=1)),
    text=hover_data,
    hovertemplate='%{text}<extra></extra>',
    showlegend=False,
    name='vertices'
))
for i, j in edges:
    xi, yi = points[i]
    xj, yj = points[j]
    fig.add_trace(go.Scatter(
        x=[xi, xj], y=[yi, yj],
        mode='lines',
        line=dict(color='grey', width=1),
        hoverinfo='skip',
        showlegend=False
    ))
fig.update_layout(
    height=600,
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis=dict(visible=False, scaleanchor='y', scaleratio=1, constrain='domain'),
    yaxis=dict(visible=False, constrain='domain', autorange='reversed'),
    plot_bgcolor='rgb(40,40,40)',
    hovermode='closest'
)

# Highlight polychrome triangles only when all vertices are colored (game end)
if all(color is not None for color in st.session_state.vertex_colors) and poly_triangles:
    for tri in poly_triangles:
        triangle_pts = [points[v] for v in tri]
        
        # Compute centroid
        cx = sum(p[0] for p in triangle_pts) / 3
        cy = sum(p[1] for p in triangle_pts) / 3

        # Sort vertices around the centroid to ensure proper triangle fill
        triangle_pts.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))

        x_coords = [p[0] for p in triangle_pts] + [triangle_pts[0][0]]
        y_coords = [p[1] for p in triangle_pts] + [triangle_pts[0][1]]

        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            fill='toself',
            fillcolor='rgba(255,255,0, 1)',
            line=dict(width=1, color='black'),
            hoverinfo='skip',
            showlegend=False
        ))

# Create space for warning
warning_spot = st.empty()

# Handle plot interactions
selected = st.session_state.get("last_selected_event", None)
new_selected = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=600,
    key="plot"
)

if new_selected:
    selected = new_selected
    st.session_state.last_selected_event = selected

if selected:
    clicked_trace = selected[0]["curveNumber"]
    if clicked_trace == 0:
        click_x = selected[0]["x"]
        click_y = selected[0]["y"]
        min_distance = float('inf')
        closest_vertex = -1
        for i, (px, py) in enumerate(points):
            distance = (click_x - px)**2 + (click_y - py)**2
            if distance < min_distance:
                min_distance = distance
                closest_vertex = i

        success, error_msg = utils.handle_vertex_click(closest_vertex, click_x, click_y)
        
        if not success:
            fig.add_annotation(
                x=click_x,
                y=click_y,
                text="❌ Invalid",
                showarrow=True,
                arrowhead=4,
                ax=0,
                ay=-30,
                font=dict(color="red", size=13),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="red",
                borderwidth=1,
                borderpad=4
            )
            warning_spot.warning(error_msg)
            # Clear the event so it doesn't stick around
            if "last_selected_event" in st.session_state:
                del st.session_state.last_selected_event
        else:
            st.rerun()