from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class PDF(FPDF):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme

    def apply_theme_colors(self, is_content=False):
        """Apply theme-specific colors. `is_content=True` changes content color differently for Modern theme"""
        if self.theme == "classic":
            return (0, 0, 0)  # Black text
        elif self.theme == "creative":
            return (0, 102, 204)  # Blue text
        elif self.theme == "modern":
            return (255, 102, 0) if is_content else (50, 50, 50)  # Orange for content, Dark Gray for headers

    def header(self):
        r, g, b = self.apply_theme_colors()
        self.set_text_color(r, g, b)

        if self.theme == "classic":
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Resume", ln=True, align='C')
        elif self.theme == "creative":
            self.set_font("Courier", "B", 20)
            self.cell(0, 10, "Creative Resume", ln=True, align='C')
        elif self.theme == "modern":
            self.set_font("Helvetica", "B", 18)
            self.set_fill_color(200, 200, 200)
            self.cell(0, 10, "Modern Resume", ln=True, align='C', fill=True)
        self.ln(10)

    def section_header(self, title):
        r, g, b = self.apply_theme_colors()
        self.set_text_color(r, g, b)

        if self.theme == "classic":
            self.set_font("Arial", "B", 12)
        elif self.theme == "creative":
            self.set_font("Courier", "B", 14)
        elif self.theme == "modern":
            self.set_font("Helvetica", "B", 13)

        self.cell(0, 10, title, ln=True, align='L', border=1)
        self.ln(5)

    def section_content(self, content):
        r, g, b = self.apply_theme_colors(is_content=True)  # Use special color for Modern theme
        self.set_text_color(r, g, b)

        if self.theme == "classic":
            self.set_font("Arial", size=10)
        elif self.theme == "creative":
            self.set_font("Courier", size=11)
        elif self.theme == "modern":
            self.set_font("Helvetica", size=11)

        self.multi_cell(0, 10, content)
        self.ln(5)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    github = request.form.get('github', 'N/A')
    dob = request.form['dob']
    native_place = request.form['native_place']
    age = request.form['age']
    gender = request.form['gender']
    linkedin = request.form.get('linkedin', 'N/A')
    experience = request.form['experience']
    education = request.form['education']
    skills = request.form['skills']
    achievements = request.form.get('achievements', 'N/A')
    hobbies = request.form.get('hobbies', 'N/A')
    languages = request.form.get('languages', 'N/A')
    theme = request.form.get('theme', 'classic')

    pdf = PDF(theme)
    pdf.add_page()

    profile_pic = request.files.get('profile_pic')
    if profile_pic:
        filename = secure_filename(profile_pic.filename)
        profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_pic.save(profile_pic_path)
        img = Image.open(profile_pic_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        jpg_path = profile_pic_path.rsplit(".", 1)[0] + ".jpg"
        img.save(jpg_path, "JPEG")
        pdf.image(jpg_path, x=75, y=30, w=60, h=60)
        pdf.ln(70)

    # Apply header color
    r, g, b = pdf.apply_theme_colors()
    pdf.set_text_color(r, g, b)

    pdf.cell(0, 10, name, ln=True, align='C')
    pdf.cell(0, 10, email, ln=True, align='C')
    pdf.cell(0, 10, f"Phone: {phone}", ln=True, align='C')
    pdf.cell(0, 10, f"GitHub: {github}", ln=True, align='C')
    pdf.cell(0, 10, f"Date of Birth: {dob}", ln=True, align='C')
    pdf.cell(0, 10, f"Native Place: {native_place}", ln=True, align='C')
    pdf.cell(0, 10, f"Age: {age}", ln=True, align='C')
    pdf.cell(0, 10, f"Gender: {gender}", ln=True, align='C')
    pdf.cell(0, 10, f"LinkedIn: {linkedin}", ln=True, align='C')
    pdf.ln(10)

    pdf.section_header("Work Experience")
    pdf.section_content(experience)
    pdf.section_header("Education")
    pdf.section_content(education)
    pdf.section_header("Skills")
    pdf.section_content(skills)
    pdf.section_header("Achievements")
    pdf.section_content(achievements)
    pdf.section_header("Hobbies")
    pdf.section_content(hobbies)
    pdf.section_header("Languages Known")
    pdf.section_content(languages)

    resume_path = f"static/{name.replace(' ', '_')}_resume.pdf"
    pdf.output(resume_path)
    return send_file(resume_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)