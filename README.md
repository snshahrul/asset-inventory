# Company Asset Inventory Management System

A web-based inventory management system for tracking company assets, categories, and checkout records. Built with FastAPI and SQLAlchemy, featuring both REST API endpoints and a user-friendly web interface.

## Features

- **Asset Management**: Create, read, update, and delete company assets
- **Category Management**: Organize assets into custom categories
- **Checkout System**: Track asset checkouts and returns with detailed records
- **Search & Filter**: Search assets by name, brand, model, serial number, or location
- **Asset Status Tracking**: Monitor asset status (available, checked out, maintenance, retired)
- **Dashboard**: View inventory statistics and recent assets at a glance
- **Data Export**: Export asset data to CSV and JSON formats
- **Responsive UI**: Clean, user-friendly web interface with Jinja2 templates

## Tech Stack

- **Backend**: FastAPI 0.115.12
- **Database**: SQLAlchemy 2.0.40 with SQLite
- **Server**: Uvicorn 0.34.2
- **Frontend**: Jinja2 3.1.6 templates
- **Python**: 3.10+

## Installation

### 1. Clone or download the project

```bash
cd inventory_management
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**
```bash
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the development server

From the project root directory with the virtual environment activated:

```bash
python app/main.py
```

The application will start on `http://localhost:8000`

### Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## Project Structure

```
inventory_management/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and page routes
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models (Category, Asset, CheckoutRecord)
│   ├── schemas.py           # Pydantic schemas for request/response validation
│   ├── routers/             # API route handlers
│   │   ├── assets.py        # Asset CRUD operations
│   │   ├── categories.py    # Category CRUD operations
│   │   ├── checkout.py      # Checkout record management
│   │   └── export_routes.py # Data export (CSV/JSON)
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html        # Base template with navigation
│       ├── dashboard.html   # Dashboard/home page
│       ├── assets_list.html # Assets listing page
│       ├── asset_form.html  # Asset creation/edit form
│       ├── asset_detail.html # Asset details page
│       ├── categories.html  # Categories management page
│       └── checkout.html    # Checkout management page
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Models

### Category
- `id`: Primary key
- `name`: Unique category name
- `description`: Category description
- `assets`: Related assets (one-to-many relationship)

### Asset
- `id`: Primary key
- `name`: Asset name
- `brand`: Brand/manufacturer
- `model_number`: Model identifier
- `serial_number`: Serial number
- `purchase_date`: Date of purchase
- `purchase_price`: Cost of asset
- `location`: Physical location
- `status`: Current status (available, checked_out, maintenance, retired)
- `notes`: Additional notes
- `category_id`: Foreign key to Category
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### CheckoutRecord
- `id`: Primary key
- `checked_out_by`: Person who checked out the asset
- `checked_out_at`: Checkout timestamp
- `expected_return_at`: Expected return date
- `returned_at`: Actual return date (null if not returned)
- `notes`: Checkout notes
- `asset_id`: Foreign key to Asset

## API Endpoints

### Assets
- `GET /api/assets` - List all assets with filtering
- `GET /api/assets/{asset_id}` - Get asset details
- `POST /api/assets` - Create new asset
- `PUT /api/assets/{asset_id}` - Update asset
- `DELETE /api/assets/{asset_id}` - Delete asset

### Categories
- `GET /api/categories` - List all categories
- `GET /api/categories/{category_id}` - Get category details
- `POST /api/categories` - Create new category
- `PUT /api/categories/{category_id}` - Update category
- `DELETE /api/categories/{category_id}` - Delete category

### Checkout Records
- `GET /api/checkout` - List all checkout records
- `POST /api/checkout` - Create checkout record
- `PUT /api/checkout/{record_id}` - Return asset (mark as returned)

### Export
- `GET /export/csv` - Export assets to CSV
- `GET /export/json` - Export assets to JSON

## Web Pages

- **Dashboard** (`/`) - Overview with statistics and recent assets
- **Assets List** (`/assets`) - Browse and filter all assets
- **New Asset** (`/assets/new`) - Create new asset
- **Asset Detail** (`/assets/{id}`) - View asset details and checkout history
- **Categories** (`/categories`) - Manage asset categories
- **Checkout** (`/checkout`) - Manage asset checkouts and returns

## Query Parameters

### Assets Filtering
- `search`: Search in name, brand, model number, serial number, or location
- `category_id`: Filter by category ID
- `status`: Filter by asset status (available, checked_out, maintenance, retired)

Example:
```
GET /assets?search=laptop&category_id=2&status=available
```

## Usage Examples

### Using the Web Interface
1. Navigate to http://localhost:8000
2. View the dashboard with inventory statistics
3. Click "Assets" to browse the complete asset list
4. Use search and filters to find specific assets
5. Create new assets via the "New Asset" button
6. Manage categories via the "Categories" section
7. Check out and return assets from the "Checkout" section

### Using the API with cURL

**List assets:**
```bash
curl "http://localhost:8000/api/assets"
```

**Get asset details:**
```bash
curl "http://localhost:8000/api/assets/1"
```

**Create asset:**
```bash
curl -X POST "http://localhost:8000/api/assets" \
  -H "Content-Type: application/json" \
  -d '{"name": "MacBook Pro", "brand": "Apple", "category_id": 1}'
```

**Export to CSV:**
```bash
curl "http://localhost:8000/export/csv" > assets.csv
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can specify a different port by modifying `main.py` or running:
```bash
uvicorn app.main:app --port 8001 --reload
```

### Database Issues
The application uses SQLite by default. If you encounter database issues:
1. Delete `./inventory.db` (if it exists)
2. Restart the application - a new database will be created

### Missing Dependencies
If you encounter import errors:
```bash
pip install -r requirements.txt --upgrade
```

## Future Enhancements

- User authentication and authorization
- Email notifications for checkout reminders
- Asset depreciation tracking
- Barcode/QR code scanning
- Audit logging
- Multi-location support
- Asset lifecycle management
- Advanced reporting and analytics

## License

This project is proprietary and for internal use only.

## Support
For issues or questions, contact the development team.

