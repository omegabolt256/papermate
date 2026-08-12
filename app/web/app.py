"""Flask web application for Medical Research Agent."""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from app.projects import ProjectManager
from app.chats import ChatManager
from app.search.engine import SearchEngine
from app.papers import PaperManager
from app.export import ResearchExporter
from app.models import get_model_provider
from config.settings import DATA_DIR
import os

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.secret_key = os.urandom(24)
    CORS(app)
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/projects', methods=['GET'])
    def get_projects():
        mgr = ProjectManager()
        projects = mgr.get_all_projects()
        return jsonify([p.to_dict() for p in projects])
    
    @app.route('/api/projects', methods=['POST'])
    def create_project():
        data = request.json or {}
        mgr = ProjectManager()
        project = mgr.create_project(name=data.get('name', 'New Project'))
        return jsonify(project.to_dict())
    
    @app.route('/api/search', methods=['POST'])
    def search():
        data = request.json or {}
        query = data.get('query', '')
        engine = SearchEngine()
        papers = engine.search_all(query, max_per_source=5)
        return jsonify([{
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "abstract": (p.abstract or "")[:300],
            "source": p.source,
            "doi": p.doi,
            "pmid": p.pmid,
            "pdf_url": p.pdf_url,
        } for p in papers[:15]])
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.json or {}
        question = data.get('question', '')
        if not question:
            return jsonify({"response": "Please ask a question."})
        
        model = get_model_provider("ollama")
        response = model.generate(question, max_tokens=500)
        return jsonify({"response": response})
    
    @app.route('/api/projects/<project_id>/papers', methods=['GET'])
    def get_papers(project_id):
        mgr = PaperManager()
        papers = mgr.get_project_papers(project_id)
        return jsonify([p.to_dict() for p in papers])
    
    @app.route('/api/projects/<project_id>/export/<fmt>', methods=['GET'])
    def export_data(project_id, fmt):
        proj_dir = DATA_DIR / "projects" / project_id
        exporter = ResearchExporter(project_id, proj_dir / "exports")
        
        if fmt == "bibtex":
            path = exporter.export_papers_bibtex()
        elif fmt == "csv":
            path = exporter.export_papers_csv()
        else:
            return jsonify({"error": "Unknown format"}), 400
        
        exporter.close()
        return jsonify({"path": path, "message": f"Exported to {path}"})
    
    @app.route('/api/projects/<project_id>/report', methods=['GET'])
    def get_report(project_id):
        from app.reports import ReportGenerator
        proj_dir = DATA_DIR / "projects" / project_id
        gen = ReportGenerator(project_id, proj_dir)
        report = gen.generate_full_report()
        gen.close()
        return jsonify({"report": report[:5000]})
    
    @app.route('/api/health', methods=['GET'])
    def health():
        model = get_model_provider("ollama")
        try:
            test = model.generate("Say OK", max_tokens=10)
            ollama_status = "connected" if "Error" not in test else "error"
        except:
            ollama_status = "unavailable"
        
        return jsonify({
            "status": "running",
            "ollama": ollama_status,
        })
    
    return app