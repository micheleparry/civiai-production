# CiviAI - Intelligent Permitting & Compliance Engine

CiviAI is an AI-powered permitting and compliance system designed for small to medium-sized cities. It provides a "TurboTax-style" guided intake process, real-time compliance checking, and automated fee calculation.

## Features

### 🏛️ **Geo-Spatial Core**
- Property database with zoning, overlays, and constraints
- Automatic property lookup by address or tax lot number
- Integration with floodplain and riparian buffer overlays
- Support for easements and rights-of-way tracking

### 🧠 **AI-Powered Guidance**
- TurboTax-style guided permit application process
- Real-time compliance checking against local codes
- Intelligent fee calculation based on project parameters
- Natural language processing for code questions

### ⚡ **Automated Processing**
- Instant permit issuance for simple, compliant projects
- Automated document processing and validation
- Digital plan review and code compliance checking
- Streamlined workflow from application to approval

### 🎛️ **Permit Configurator**
- Backend system for managing local codes and rules
- Configurable permit types and fee structures
- Customizable compliance rules engine
- Multi-jurisdiction support for scaling

## Technology Stack

- **Backend**: Django 5.2.4 (Python)
- **Database**: SQLite (development) / PostgreSQL with PostGIS (production)
- **Frontend**: Bootstrap 5.3 with responsive design
- **API**: Django REST Framework
- **Deployment**: Vercel-ready with Docker support

## Quick Start

### Prerequisites
- Python 3.11+
- pip3

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd civiai
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python3 manage.py migrate
   ```

4. **Load sample data**
   ```bash
   python3 manage.py load_sample_data
   ```

5. **Create superuser**
   ```bash
   python3 manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python3 manage.py runserver
   ```

7. **Access the application**
   - Main application: http://localhost:8000/
   - Admin interface: http://localhost:8000/admin/

## Sample Data

The system comes with sample data for Shady Cove, Oregon including:

- **5 Properties** with realistic addresses, zoning, and overlays
- **6 Permit Types** covering residential, commercial, and accessory uses
- **Zoning Rules** for R-1, R-2, and C-G districts
- **Sample Applications** demonstrating the workflow

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=civiai_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### Customizing for Your City

1. **Update City Information**
   - Edit `civiai_project/settings.py` CIVIAI_SETTINGS
   - Modify templates to reflect your city name and contact info

2. **Configure Zoning Rules**
   - Use the admin interface at `/admin/`
   - Add your city's zoning districts and rules
   - Configure permit types and fee structures

3. **Load Property Data**
   - Import your property/parcel data
   - Update the Property model as needed for your data structure

## API Endpoints

### Public API
- `GET /api/property/<id>/` - Get property information
- `POST /api/calculate-fee/` - Calculate permit fees
- `POST /api/compliance-check/` - Run compliance check
- `GET /api/dashboard-stats/` - Get dashboard statistics

### Admin Features
- Property management
- Permit type configuration
- Zoning rules management
- Application review and approval

## Deployment

### Vercel Deployment

1. **Connect to GitHub**
   - Push your code to a GitHub repository
   - Connect the repository to Vercel

2. **Configure Environment Variables**
   - Add production environment variables in Vercel dashboard
   - Set up PostgreSQL database (recommended: Supabase or Railway)

3. **Deploy**
   - Vercel will automatically build and deploy your application

### Docker Deployment

```bash
# Build the image
docker build -t civiai .

# Run the container
docker run -p 8000:8000 civiai
```

## Contributing

CiviAI is designed to be a scalable solution for multiple cities. Contributions are welcome!

### Development Guidelines

1. Follow Django best practices
2. Maintain responsive design for mobile compatibility
3. Ensure all new features include appropriate tests
4. Document API changes and new configuration options

### Roadmap

- [ ] Advanced AI plan review capabilities
- [ ] Integration with state/county systems
- [ ] Mobile app for field inspections
- [ ] Multi-language support
- [ ] Advanced reporting and analytics

## Support

For technical support or questions about implementing CiviAI in your city:

- **Documentation**: See the `/docs` folder for detailed guides
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join our discussion forum for implementation tips

## License

CiviAI is open source software designed to help cities modernize their planning departments. See LICENSE file for details.

---

**Built for cities, by cities.** CiviAI transforms the permitting process from a bureaucratic maze into an intelligent, user-friendly experience that serves both residents and staff.

