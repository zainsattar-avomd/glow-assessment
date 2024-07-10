from flask import Flask, request, jsonify
from models import Business
from http import HTTPStatus

app = Flask(__name__)

# In-memory storage for businesses
businesses = {}

def error_response(message, status=HTTPStatus.BAD_REQUEST):
    return jsonify({'error': message}), status

def get_business_by_fein(fein):
    if fein not in businesses:
        return None, error_response(f'No Business in records with fein: {fein}', HTTPStatus.NOT_FOUND)
    return Business(**businesses[fein]), None

def validate_json(data, required_fields):
    for field in required_fields:
        if field not in data:
            return error_response(f'Missing required field: {field}')
    return None

@app.route('/business/<string:fein>', methods=['GET'])
def get_business(fein):
    """Returns business data based on FEIN"""
    business, error = get_business_by_fein(fein)
    if error:
        return error
    return jsonify(businesses[fein]), HTTPStatus.OK

@app.route('/business/', methods=['POST'])
def create_business():
    """Creates a new business"""
    data = request.json
    error = validate_json(data, ['name', 'fein'])
    if error:
        return error
    
    if data['fein'] in businesses:
        return error_response('Business already exists', HTTPStatus.CONFLICT)

    business = Business(fein=data['fein'], name=data['name'])
    business.add_to_storage(businesses)
    
    return jsonify({
        'fein': business.fein,
        'message': 'Business created.',
        'next_step': Business.get_next_step(business.stage)
    }), HTTPStatus.CREATED

@app.route('/business/<string:fein>/industry/', methods=['POST'])
def add_industry(fein):
    """Adds an industry to a business" and updates status"""
    business, error = get_business_by_fein(fein)
    if error:
        return error
    
    data = request.json
    error = validate_json(data, ['industry'])
    if error:
        return error
    
    error = business.add_industry_and_update_stage(data['industry'])
    if error:
        return jsonify(error), HTTPStatus.BAD_REQUEST
    
    business.add_to_storage(businesses)
    return jsonify({
        'fein': business.fein,
        'message': 'Industry Added.',
        'next_step': Business.get_next_step(business.stage)        
    }), HTTPStatus.OK

@app.route('/business/<string:fein>/contact/', methods=['POST'])
def add_contact(fein):
    """Adds a contact to a business and updates status"""
    business, error = get_business_by_fein(fein)
    if error:
        return error
    
    data = request.json
    error = validate_json(data, ['contact'])
    if error:
        return error
    
    contact = data['contact']
    error = validate_json(contact, ['name', 'phone'])
    if error:
        return error
    
    error = business.add_contact_and_update_stage(contact)
    if error:
        return jsonify(error), HTTPStatus.BAD_REQUEST
    
    business.add_to_storage(businesses)
    return jsonify({
        'fein': business.fein,
        'message': 'Contact Added.',
        'next_step': Business.get_next_step(business.stage)        
    }), HTTPStatus.OK

@app.route('/business/<string:fein>/complete-process/', methods=['POST'])
def complete_process(fein):
    """Completes the business process"""
    business, error = get_business_by_fein(fein)
    if error:
        return error    

    data = request.json
    error = validate_json(data, ['stage'])
    if error:
        return error
    
    if data['stage'] not in ['Won', 'Lost']:
        return error_response('Invalid stage. This API accepts {"stage": "Lost|Won"}', HTTPStatus.BAD_REQUEST)
    
    error = business.update_stage(data['stage'])
    if error:
        error['next_step'] = Business.get_next_step(business.stage)
        return jsonify(error), HTTPStatus.BAD_REQUEST
    
    business.add_to_storage(businesses)
    return jsonify({
        'fein': business.fein,
        'message': 'Status updated',
        'next_step': Business.get_next_step(business.stage)        
    }), HTTPStatus.OK

if __name__ == '__main__':
    app.run(debug=True)