from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import qrcode
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", style='B', size=16)
        self.cell(200, 10, "Resume", ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", style='B', size=12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(5)

    def chapter_content(self, content):
        self.set_font("Arial", size=10)
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

    pdf = PDF()
    pdf.add_page()

    profile_pic = request.files.get('profile_pic')
    profile_pic_path = None
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

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, name, ln=True, align='C')
    pdf.cell(200, 10, email, ln=True, align='C')
    pdf.cell(200, 10, f"Phone: {phone}", ln=True, align='C')
    pdf.cell(200, 10, f"GitHub: {github}", ln=True, align='C')
    pdf.cell(200, 10, f"Date of Birth: {dob}", ln=True, align='C')
    pdf.cell(200, 10, f"Native Place: {native_place}", ln=True, align='C')
    pdf.cell(200, 10, f"Age: {age}", ln=True, align='C')
    pdf.cell(200, 10, f"Gender: {gender}", ln=True, align='C')
    pdf.cell(200, 10, f"LinkedIn: {linkedin}", ln=True, align='C')
    pdf.ln(10)

    pdf.chapter_title("Work Experience")
    pdf.chapter_content(experience)
    pdf.chapter_title("Education")
    pdf.chapter_content(education)
    pdf.chapter_title("Skills")
    pdf.chapter_content(skills)
    pdf.chapter_title("Achievements")
    pdf.chapter_content(achievements)
    pdf.chapter_title("Hobbies")
    pdf.chapter_content(hobbies)
    pdf.chapter_title("Languages Known")
    pdf.chapter_content(languages)

    resume_path = f"static/{name.replace(' ', '_')}_resume.pdf"
    pdf.output(resume_path)
    return send_file(resume_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
