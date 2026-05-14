# 🎲 Rubik's Cube Solver

A web application that solves 3x3 Rubik's cubes using optimal algorithms and color detection. Input your cube state manually or upload a photo for automatic color recognition.

## Features

- **Manual Input**: Input cube colors through an intuitive web interface
- **Image Detection**: Upload a photo of your cube for automatic color recognition
- **Optimal Solving**: Uses Kociemba's algorithm to find solutions in ~20 moves
- **Step-by-Step Guide**: Clear move notation and visual instructions
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Python (Flask)
  - Kociemba solver for optimal cube solving
  - OpenCV for image-based color detection
  - RESTful API

- **Frontend**: React
  - Interactive color picker interface
  - Image upload and preview
  - Solution display with move-by-move guide

- **Deployment**: Vercel (frontend) + Railway/Heroku (backend)

## Project Structure

```
rubiks-cube-solver/
├── backend/                          # Python Flask backend
│   ├── solvers/
│   │   ├── cube.py                   # Cube state representation
│   │   ├── solver.py                 # Kociemba solver wrapper
│   │   ├── color_detector.py         # OpenCV-based color detection
│   │   └── __init__.py
│   ├── app.py                        # Flask application
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment configuration
│   └── tests/                        # Unit tests
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CubeInput.jsx        # Manual color input
│   │   │   ├── ColorGrid.jsx        # 3x3 color grid display
│   │   │   ├── ImageUpload.jsx      # Image upload form
│   │   │   └── SolutionDisplay.jsx  # Solution display
│   │   ├── styles/                  # Component CSS files
│   │   ├── App.jsx                  # Main app component
│   │   ├── App.css                  # Global styles
│   │   └── index.jsx                # React entry point
│   ├── public/
│   │   └── index.html               # HTML template
│   └── package.json                 # Node.js dependencies
│
└── README.md                         # This file
```

## Setup Instructions

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 14+** with npm
- Git

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment** (optional):
   ```bash
   # Edit .env if needed
   # FLASK_DEBUG=True (for development)
   # API_PORT=5000
   ```

3. **Run the backend**:
   ```bash
   python app.py
   ```

   Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

   Frontend will be available at `http://localhost:3000`

3. **Build for production**:
   ```bash
   npm run build
   ```

## Usage

### Manual Input Mode

1. Open the application in your browser
2. Select "Manual Input" tab
3. Click on each face button to select which face to edit
4. Click on color squares to cycle through colors
5. Use the color legend to understand the color mapping
6. Click "Solve Cube" to get the solution
7. Follow the step-by-step moves to solve your cube

### Image Detection Mode

1. Click "Image Detection" tab
2. Upload a clear photo of your Rubik's cube
3. The system will automatically detect the colors
4. Review the detected colors and adjust if needed
5. Click "Solve Cube" to get the solution

## Cube Notation

### Move Notation
- **U, D, L, R, F, B**: Rotate that face 90° clockwise
- **U', D', L', R', F', B'**: Rotate 90° counterclockwise (add ')
- **U2, D2, L2, R2, F2, B2**: Rotate 180° (add 2)

### Face Labels
- **U**: Up (Yellow on solved cube)
- **D**: Down (White on solved cube)
- **R**: Right (Red on solved cube)
- **L**: Left (Green on solved cube)
- **F**: Front (Orange on solved cube)
- **B**: Back (Blue on solved cube)

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Solve Cube
```bash
POST /api/solve
Content-Type: application/json

{
  "state": "UUUUU... (54 characters)"
}
```

Response:
```json
{
  "success": true,
  "moves": ["U", "R", "F'", "U2"],
  "move_count": 4,
  "solved": false
}
```

### Detect Colors from Image
```bash
POST /api/detect-colors
Content-Type: multipart/form-data

(image file)
```

Response:
```json
{
  "success": true,
  "colors": {
    "U": "YYYYYYYYY",
    "R": "RRRRRRRRR",
    ...
  }
}
```

### Validate Cube State
```bash
POST /api/validate-cube
Content-Type: application/json

{
  "state": "UUUUU..."
}
```

### Create Cube from Faces
```bash
POST /api/cube-faces
Content-Type: application/json

{
  "faces": {
    "U": "WWWWWWWWW",
    "R": "RRRRRRRRR",
    ...
  }
}
```

## Deployment

### Deploy Backend (Railway/Heroku)

1. **Create account** on [Railway.app](https://railway.app) or [Heroku](https://heroku.com)

2. **Push to GitHub** (required for deployment):
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Connect repository** to Railway/Heroku and deploy

4. **Set environment variables**:
   ```
   FLASK_ENV=production
   ```

5. **Update frontend** `.env` with your deployed backend URL:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   ```

### Deploy Frontend (Vercel)

1. **Create account** on [Vercel](https://vercel.com)

2. **Import project** from GitHub

3. **Configure build settings**:
   - Build command: `npm run build`
   - Output directory: `build`
   - Root directory: `frontend`

4. **Deploy** (Vercel handles this automatically)

## Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Manual Testing
```bash
# Test cube solver
python -c "from solvers.cube import Cube; from solvers.solver import solve; c = Cube(); print(solve(c))"

# Start API server
python app.py

# In another terminal, test endpoints
curl http://localhost:5000/api/health
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Known Limitations & Future Improvements

### Current Limitations
- Image detection v1: Simplified single-face detection
- Assumes standard cube color scheme
- May struggle with poor lighting or angled photos

### Future Enhancements
- **Multi-face detection**: Detect all 6 faces from a single image
- **ML-based color detection**: Train CNN for better color recognition
- **3D visualization**: 3D cube visualization with animation
- **Tutorial mode**: Step-by-step animated solution guide
- **Mobile app**: Native React Native mobile application
- **Solver optimization**: Support for different solving strategies

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Verify dependencies: `pip list | grep -E "Flask|kociemba|opencv"`
- Check port 5000 is available

### Frontend won't connect to backend
- Verify backend is running on `http://localhost:5000`
- Check CORS is enabled in Flask
- Check browser console for network errors

### Image detection not working
- Ensure image is clear and well-lit
- Try uploading a photo of an actual cube face
- Check OpenCV is installed: `python -c "import cv2; print(cv2.__version__)"`

### Cube state validation errors
- Ensure state is exactly 54 characters
- Each color must appear exactly 9 times
- Use only valid colors: W, Y, R, O, B, G

## License

MIT License - Feel free to use and modify

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

- [Kociemba Algorithm](http://kociemba.org/) - Optimal cube solver
- [OpenCV](https://opencv.org/) - Computer vision library
- [React](https://react.dev/) - UI framework
- [Flask](https://flask.palletsprojects.com/) - Web framework

## Support

For issues or questions, please open an issue on GitHub.

---

**Happy solving! 🎲**
