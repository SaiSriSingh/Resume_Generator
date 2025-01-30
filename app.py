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

    def header(self):
        if self.theme == "classic":
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Resume", ln=True, align='C')
            self.ln(10)
        elif self.theme == "creative":
            self.set_font("Courier", "B", 20)
            self.set_text_color(0, 102, 204)
            self.cell(0, 10, "Creative Resume", ln=True, align='C')
            self.ln(10)
        elif self.theme == "modern":
            self.set_font("Helvetica", "B", 18)
            self.set_fill_color(50, 50, 50)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, "Modern Resume", ln=True, align='C', fill=True)
            self.ln(15)

    def section_header(self, title):
        if self.theme == "classic":
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, border=1, ln=True, align='L')
        elif self.theme == "creative":
            self.set_font("Courier", "B", 14)
            self.set_text_color(0, 102, 204)
            self.cell(0, 10, title, border="B", ln=True, align='C')
        elif self.theme == "modern":
            self.set_font("Helvetica", "B", 13)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 10, title, ln=True, align='L', fill=True)
        self.ln(5)

    def section_content(self, content):
        if self.theme == "classic":
            self.set_font("Arial", size=10)
        elif self.theme == "creative":
            self.set_font("Courier", size=11)
            self.set_text_color(80, 80, 80)
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
        profile_pic_path = jpg_path
        pdf.image(profile_pic_path, x=75, y=30, w=60, h=60)
        pdf.ln(70)

    # Apply theme-specific text styles
    if theme == "classic":
        pdf.set_font("Arial", size=12)
    elif theme == "creative":
        pdf.set_font("Courier", "B", 14)
        pdf.set_text_color(0, 102, 204)
    elif theme == "modern":
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(50, 50, 50)

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