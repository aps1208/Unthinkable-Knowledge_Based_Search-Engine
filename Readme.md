# Knowledge-base Search Engine

A modern RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and ask questions about their content using AI-powered search and synthesis.

## Features

- **User Authentication**: Secure registration and login system with JWT tokens
- **Document Upload**: Support for PDF document ingestion with automatic text extraction
- **AI-Powered Search**: Vector-based semantic search using embeddings
- **Intelligent Q&A**: LLM-powered answer synthesis from retrieved document chunks
- **User Isolation**: Each user's documents and queries are completely isolated
- **Modern UI**: Clean, responsive interface with real-time chat functionality
- **Multi-document Support**: Handle multiple documents per user with source filtering

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database for user management
- **SQLAlchemy** - ORM for database operations
- **LangChain** - Framework for LLM applications
- **ChromaDB** - Vector database for embeddings storage
- **Google Gemini** - LLM for answer generation and embeddings
- **HuggingFace** - Local embeddings fallback
- **Argon2** - Secure password hashing
- **JWT** - Authentication tokens

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering

## Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- PostgreSQL database
- Google Gemini API key

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/adityapandeydev/knowledge_based_search.git
cd knowledge-base-search
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Create Database Folder
```bash
mkdir db
```

#### Environment Configuration
Create `backend/.env` file:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/knowledge_base

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

```

#### Database Setup
1. Create PostgreSQL database:
```sql
CREATE DATABASE knowledge_base;
```

2. The application will automatically create tables on first run.

### 3. Frontend Setup

```bash
cd frontend
npm install
# or
bun install
```

### 4. Run the Application

#### Start Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend will be available at `http://127.0.0.1:8000`

#### Start Frontend
```bash
cd frontend
npm run dev
# or
bun run dev
```
Frontend will be available at `http://localhost:5173`

## Usage

### 1. User Registration/Login
- Navigate to the application
- Register a new account or login with existing credentials
- Each user has isolated document storage and query history

### 2. Document Upload
- Click "Upload" and select a PDF file
- The system will:
  - Extract text from the PDF
  - Split into manageable chunks
  - Generate embeddings using Gemini (with HuggingFace fallback)
  - Store in user-specific vector database

### 3. Ask Questions
- Type your question in the chat interface
- The system will:
  - Search for relevant document chunks
  - Synthesize an answer using Gemini
  - Display formatted response with markdown support

### 4. Multi-Document Support
- Upload multiple documents
- Each upload replaces the previous index (single-document mode)
- Queries automatically use the most recently uploaded document
- Source filtering available via API for specific document queries

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login

### Document Management
- `POST /upload` - Upload PDF document (requires authentication)
- `POST /ask` - Ask question about documents (requires authentication)

## Project Structure

```
knowledge-base-search/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── auth.py              # Authentication logic
│   ├── database.py          # Database models
│   ├── ingestion.py         # Document processing
│   ├── retrieval.py         # Query processing
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── db/                  # Vector database storage
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth.tsx     # Login/Register UI
│   │   │   ├── Upload.tsx   # File upload UI
│   │   │   └── Chat.tsx     # Q&A interface
│   │   ├── api/
│   │   │   └── client.ts    # API client
│   │   └── App.tsx          # Main application
│   └── package.json         # Node dependencies
└── README.md
```

## Security Features

- **Password Hashing**: Argon2 algorithm for secure password storage
- **JWT Authentication**: Stateless authentication with configurable expiration
- **User Isolation**: Complete separation of user data and queries
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configurable cross-origin resource sharing

## Development Notes

### Embedding Models
- **Primary**: Google Gemini `models/embedding-001`
- **Fallback**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`

### Vector Database
- Uses ChromaDB with persistent storage
- User-specific collections prevent data mixing
- Automatic model-specific directory creation

### Error Handling
- Graceful fallbacks for API failures
- User-friendly error messages
- Comprehensive logging for debugging

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure database exists

2. **Gemini API Errors**
   - Verify GEMINI_API_KEY is set correctly
   - Check API quota and billing
   - System will fallback to local embeddings

3. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

4. **Frontend Build Issues**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility

## Production Deployment

### Environment Variables
- Set strong `SECRET_KEY` for JWT signing
- Use production PostgreSQL database
- Configure proper CORS origins
- Set up SSL/TLS certificates

### Security Considerations
- Use environment variables for all secrets
- Implement rate limiting
- Add input sanitization
- Configure proper logging
- Set up monitoring and alerts

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
