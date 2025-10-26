import logging
import csv
import os
import io
from datetime import datetime, timedelta
from flask import current_app, render_template
from sqlalchemy import func
from app.extensions import db
from app.models.models import Professional, ServiceRequest, ServiceStatus, User, Customer, Service

logger = logging.getLogger(__name__)

def send_daily_reminders():
    """
    Send daily reminders to professionals who have pending service requests
    or haven't visited the platform recently.
    """
    logger.info("Starting daily reminders job")
    try:
        # Get professionals with pending service requests
        pending_requests = db.session.query(Professional).join(
            ServiceRequest, ServiceRequest.professional_id == Professional.id
        ).filter(
            ServiceRequest.status == ServiceStatus.ASSIGNED,
            ServiceRequest.is_active == True,
            Professional.is_active == True
        ).all()
        
        # Get professionals who haven't logged in for more than 2 days
        two_days_ago = datetime.now() - timedelta(days=2)
        inactive_professionals = db.session.query(Professional).join(
            User, User.id == Professional.user_id
        ).filter(
            (User.last_login == None) | (User.last_login < two_days_ago),
            Professional.is_active == True
        ).all()
        
        # Combine both lists and remove duplicates
        professionals_to_remind = list(set(pending_requests + inactive_professionals))
        
        # Send reminders
        for professional in professionals_to_remind:
            # Get user details
            user = User.query.get(professional.user_id)
            if not user:
                continue
                
            # Count pending requests
            pending_count = ServiceRequest.query.filter_by(
                professional_id=professional.id,
                status=ServiceStatus.ASSIGNED,
                is_active=True
            ).count()
            
            # Prepare message
            message = f"Hello {user.name}, you have {pending_count} pending service requests. "
            if pending_count > 0:
                message += "Please log in to accept or reject them."
            else:
                message += "Please log in to check for new service requests."
            
            # Send notification (placeholder for actual implementation)
            # This would be replaced with actual email/SMS/webhook implementation
            logger.info(f"Sending reminder to {user.email}: {message}")
            send_email(user.email, "Daily Reminder", message)
            # or send_sms(user.phone, message)
            # or send_gchat_webhook(webhook_url, message)
        
        logger.info(f"Sent reminders to {len(professionals_to_remind)} professionals")
        return True
    except Exception as e:
        logger.error(f"Error sending daily reminders: {str(e)}")
        return False

def generate_monthly_reports():
    """
    Generate and send monthly activity reports to all customers
    at the beginning of each month.
    """
    logger.info("Starting monthly reports job")
    try:
        # Get the previous month's date range
        today = datetime.now()
        first_day_previous_month = datetime(today.year, today.month, 1) - timedelta(days=1)
        first_day_previous_month = datetime(first_day_previous_month.year, first_day_previous_month.month, 1)
        last_day_previous_month = datetime(today.year, today.month, 1) - timedelta(days=1)
        
        # Get all active customers
        customers = Customer.query.filter_by(is_active=True).all()
        
        for customer in customers:
            # Get user details
            user = User.query.get(customer.user_id)
            if not user:
                continue
                
            # Get service requests for this customer in the previous month
            service_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer.id,
                ServiceRequest.request_time >= first_day_previous_month,
                ServiceRequest.request_time <= last_day_previous_month,
                ServiceRequest.is_active == True
            ).all()
            
            # Skip if no activity
            if not service_requests:
                logger.info(f"No activity for customer {user.email} in the previous month")
                continue
                
            # Calculate statistics
            total_requests = len(service_requests)
            completed_requests = sum(1 for req in service_requests if req.status == ServiceStatus.COMPLETED)
            cancelled_requests = sum(1 for req in service_requests if req.status == ServiceStatus.CANCELLED)
            pending_requests = total_requests - completed_requests - cancelled_requests
            
            # Get service details
            service_details = []
            for req in service_requests:
                service = Service.query.get(req.service_id)
                professional = None
                if req.professional_id:
                    professional_obj = Professional.query.get(req.professional_id)
                    if professional_obj:
                        professional_user = User.query.get(professional_obj.user_id)
                        if professional_user:
                            professional = professional_user.name
                
                service_details.append({
                    'service_name': service.name if service else 'Unknown',
                    'status': req.status.value,
                    'request_date': req.request_time.strftime('%Y-%m-%d'),
                    'professional': professional or 'Not assigned',
                    'location': req.location
                })
            
            # Prepare report data
            report_data = {
                'customer_name': user.name,
                'month': first_day_previous_month.strftime('%B %Y'),
                'total_requests': total_requests,
                'completed_requests': completed_requests,
                'cancelled_requests': cancelled_requests,
                'pending_requests': pending_requests,
                'service_details': service_details
            }
            
            # Generate HTML report
            # In a real implementation, you would use a template engine like Jinja2
            html_content = render_template('monthly_report.html', **report_data)
            
            # Send email with HTML report
            send_email(user.email, f"Monthly Activity Report - {report_data['month']}", html_content, is_html=True)
            
            logger.info(f"Sent monthly report to {user.email}")
        
        logger.info("Completed monthly reports job")
        return True
    except Exception as e:
        logger.error(f"Error generating monthly reports: {str(e)}")
        return False

def generate_csv_export(admin_id, filters=None):
    """
    Generate a CSV export of service requests based on filters.
    This is triggered by an admin user.
    
    Args:
        admin_id: The ID of the admin user who triggered the export
        filters: Optional dictionary of filters to apply
    
    Returns:
        str: Path to the generated CSV file
    """
    logger.info(f"Starting CSV export job triggered by admin ID {admin_id}")
    try:
        # Build query for closed service requests
        query = db.session.query(
            ServiceRequest.id.label('service_request_id'),
            Service.name.label('service_name'),
            ServiceRequest.request_time.label('request_date'),
            ServiceRequest.status.label('status'),
            ServiceRequest.location.label('location'),
            ServiceRequest.pin_code.label('pin_code'),
            User.name.label('customer_name'),
            User.email.label('customer_email'),
            User.phone.label('customer_phone')
        ).join(
            Service, ServiceRequest.service_id == Service.id
        ).join(
            Customer, ServiceRequest.customer_id == Customer.id
        ).join(
            User, Customer.user_id == User.id
        ).filter(
            ServiceRequest.status == ServiceStatus.COMPLETED,
            ServiceRequest.is_active == True
        )
        
        # Apply additional filters if provided
        if filters:
            if 'start_date' in filters and filters['start_date']:
                query = query.filter(ServiceRequest.request_time >= filters['start_date'])
            if 'end_date' in filters and filters['end_date']:
                query = query.filter(ServiceRequest.request_time <= filters['end_date'])
            if 'service_id' in filters and filters['service_id']:
                query = query.filter(ServiceRequest.service_id == filters['service_id'])
            if 'professional_id' in filters and filters['professional_id']:
                query = query.filter(ServiceRequest.professional_id == filters['professional_id'])
        
        # Execute query
        results = query.all()
        
        if not results:
            logger.info("No data found for CSV export")
            return None
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Service Request ID', 'Service Name', 'Request Date', 'Status',
            'Location', 'Pin Code', 'Customer Name', 'Customer Email', 'Customer Phone'
        ])
        
        # Write data rows
        for row in results:
            writer.writerow([
                row.service_request_id,
                row.service_name,
                row.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                row.status.value,
                row.location,
                row.pin_code,
                row.customer_name,
                row.customer_email,
                row.customer_phone
            ])
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"service_requests_export_{timestamp}.csv"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', newline='') as f:
            f.write(output.getvalue())
        
        # Log completion
        logger.info(f"CSV export completed: {file_path}")
        
        # In a real implementation, you would notify the admin
        # notify_admin(admin_id, f"Your CSV export is ready: {filename}")
        
        return file_path
    except Exception as e:
        logger.error(f"Error generating CSV export: {str(e)}")
        return None