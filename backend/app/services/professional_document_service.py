import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app.models.models import ProfessionalDocument
from app.extensions import db
from .base_service import BaseService, ServiceException, ValidationException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class ProfessionalDocumentService(BaseService):
    def __init__(self):
        super().__init__(ProfessionalDocument)
        
    def save_document(self, file, professional_id, document_type):
        """
        Save a professional document file and create a database entry
        
        Args:
            file: The uploaded file object
            professional_id: The ID of the professional
            document_type: The type of document (e.g., 'id_proof', 'certificate', etc.)
            
        Returns:
            The created ProfessionalDocument object
        """
        if not file:
            raise ValidationException("No file provided")
            
        if not document_type:
            raise ValidationException("Document type is required")
            
        # Validate file extension
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValidationException(f"File type not allowed. Allowed types: {', '.join(current_app.config['ALLOWED_EXTENSIONS'])}")
            
        # Generate a unique filename
        unique_filename = f"{str(uuid.uuid4())}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = os.path.join(
            current_app.config['UPLOAD_FOLDER'], 
            'professional_documents',
            str(professional_id)
        )
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        
        try:
            # Save the file
            file.save(file_path)
            
            # Get relative path for database storage
            relative_path = os.path.join(
                'professional_documents', 
                str(professional_id), 
                unique_filename
            )
            
            # Create document entry in database
            document = ProfessionalDocument(
                professional_id=professional_id,
                document_type=document_type,
                document_url=relative_path,
                is_verified=False
            )
            
            db.session.add(document)
            db.session.commit()
            
            return document
            
        except IOError as e:
            raise ServiceException(f"Failed to save document: {str(e)}")
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error saving document: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error saving document: {str(e)}")
            
    def get_professional_documents(self, professional_id):
        """Get all documents for a professional"""
        return ProfessionalDocument.query.filter_by(professional_id=professional_id).all()
        
    def get_unverified_documents(self):
        """Get all unverified documents"""
        return ProfessionalDocument.query.filter_by(is_verified=False).all()
        
    def get_document_url(self, document_id):
        """Get the full URL for a document"""
        document = self.get_or_404(document_id)
        return os.path.join(current_app.config['UPLOAD_FOLDER'], document.document_url)
