"""
Updated Flask app integration for RAG functionality
Add this to your existing app.py after the imports
"""

# Add to imports section:
# from rag.api.rag_routes import rag_bp

# In create_app() function, after registering other blueprints:
# app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')

# Example integration code to add to app.py:

def integrate_rag_routes(app):
    """
    Integrate RAG routes into existing Flask app
    This function should be called in create_app()
    """
    try:
        from rag.api.rag_routes import rag_bp
        app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')
        print("RAG routes registered successfully at /api/v1/rag")
    except ImportError as e:
        print(f"Warning: Could not import RAG routes: {e}")
        print("Make sure all dependencies are installed")
