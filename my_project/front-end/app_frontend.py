import streamlit as st

# Set the background color for the main body of the app
st.markdown(
    """
    <style>
    body {
        background-color: #FFB3C1;  /* Main background color */

    }
    .navbar {
        background-color: #B2E2D6;  /* Soft Lavender for the navbar background */
        padding: 10px;  /* Vertical and horizontal padding for navbar */
        width: 100%;  /* Full width */
        position: fixed;  /* Keep it fixed at the top */
        left:0;
        z-index: 999;  /* Ensure it is above other elements */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow for better visibility */
        margin: 0 auto;
        display: flex;  /* Use flexbox for layout */
        justify-content: space-between;  /* Space between items */
        align-items: center;  /* Center items vertically */
    }
    .navbar a {
        color: #000000;  /* Text color */
        padding: 5px;  /* Padding for each link (top-bottom, left-right) */
        text-decoration: none;
        margin-right: 15px; /* Space between links */
        display: inline-block;  /* Display links in a line */
        transition: background-color 0.3s; /* Smooth transition for hover effect */
    }
    .navbar a:hover {
        background-color: #FFB3C1;  /* Deep Rose on hover */
        border-radius: 5px;  /* Rounded corners on hover */
    }
    .content {
        padding-top: 70px;  /* Space for fixed navbar */
    }
    .cake-card {
        display: inline-block;  /* Allow cards to be inline */
        margin: 15px;  /* Margin around each card */
        text-align: center;  /* Center the text */
        background-color: #FFFFFF;  /* Card background color */
        border-radius: 5px;  /* Rounded corners */
        padding: 10px;  /* Padding inside the card */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);  /* Shadow for the card */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add the navbar HTML directly
st.markdown(
    """
     <nav class="navbar">
        <div>
            <a class="navbar-brand" href="#">SWEET SPOT</a>
            <a href="#">Home</a>
            <a href="#">Cakes</a>
            <a href="#">Customizations</a>
            <a href="#">My Cart</a>
            <a href="#">Orders</a>
            <a href="#">Profile</a>
        </div>
        <div>
            <a href="#">Login</a>
            <a href="#">Signup</a>
        </div>
    </nav>
    """,
    unsafe_allow_html=True
)

# Content below the navbar
st.markdown('<div class="content">', unsafe_allow_html=True)
st.title("Welcome to SweetSpot Delivery App")
st.markdown('</div>', unsafe_allow_html=True)
cakes = [
    {
        "name": "Chocolate Cake",
        "price": 25.99,
        "image": "https://example.com/chocolate_cake.jpg",  # Replace with actual image URLs
    },
    {
        "name": "Vanilla Cake",
        "price": 22.99,
        "image": "https://example.com/vanilla_cake.jpg",
    },
    {
        "name": "Red Velvet Cake",
        "price": 27.99,
        "image": "https://example.com/red_velvet_cake.jpg",
    },
    {
        "name": "Carrot Cake",
        "price": 24.99,
        "image": "https://example.com/carrot_cake.jpg",
    },
]

