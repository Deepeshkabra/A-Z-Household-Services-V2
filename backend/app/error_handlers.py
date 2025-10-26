from flask import jsonify
import traceback
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    This ensures that all errors are properly logged and returned with appropriate details.
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"400 Bad Request: {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error),
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.error(f"401 Unauthorized: {error}")
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error),
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.error(f"403 Forbidden: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': str(error),
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 Not Found: {error}")
        return jsonify({
            'error': 'Not Found',
            'message': str(error),
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        logger.error(f"422 Unprocessable Entity: {error}")
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': str(error),
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"500 Internal Server Error: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error),
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log the stack trace for any unhandled exception
        logger.error(f"Unhandled Exception: {error}")
        logger.error(traceback.format_exc())
        
        # Return a generic error response
        return jsonify({
            'error': 'Server Error',
            'message': str(error),
            'details': traceback.format_exc() if app.config.get('DEBUG', False) else None
        }), 500