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
    # Get form data
    name = request.form['name']
    email = request.form['email']
    linkedin = request.form.get('linkedin', 'N/A')
    experience = request.form['experience']
    education = request.form['education']
    skills = request.form['skills']
    achievements = request.form.get('achievements', 'N/A')
    theme = request.form.get('theme', 'classic')

    # Initialize PDF
    pdf = PDF()
    pdf.add_page()

    # Define styles based on theme
    if theme == "classic":
        pdf.set_font("Arial", style="", size=14)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.set_draw_color(0, 0, 0)  # Black lines
    elif theme == "modern":
        pdf.set_font("Courier", style="B", size=14)
        pdf.set_text_color(0, 102, 204)  # Blue text
        pdf.set_draw_color(0, 102, 204)  # Blue lines
    elif theme == "creative":
        pdf.set_font("Times", style="I", size=16)
        pdf.set_text_color(255, 69, 0)  # Orange text
        pdf.set_draw_color(255, 69, 0)  # Orange lines

    # Draw a line to separate header
    pdf.set_line_width(1)
    pdf.line(10, 60, 200, 60)

    # Section Headers based on theme
    def add_section(title):
        if theme == "classic":
            pdf.set_fill_color(220, 220, 220)  # Light Gray Background
        elif theme == "modern":
            pdf.set_fill_color(0, 102, 204)  # Blue Background
        elif theme == "creative":
            pdf.set_fill_color(255, 69, 0)  # Orange Background

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.ln(2)

    profile_pic = request.files.get('profile_pic')

    profile_pic_path = None
    if profile_pic:
        filename = secure_filename(profile_pic.filename)
        profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_pic.save(profile_pic_path)

        # Convert image to JPG format if needed
        img = Image.open(profile_pic_path)
        if img.mode in ("RGBA", "P"):  # Convert PNG to RGB mode
            img = img.convert("RGB")
        # Fixing .jpeg extension handling
        jpg_path = profile_pic_path.rsplit(".", 1)[0] + ".jpg"  # Corrected path handling for all formats
        img.save(jpg_path, "JPEG")
        profile_pic_path = jpg_path  # Use the converted JPG path

        # Add Profile Picture to PDF
        pdf.image(profile_pic_path, x=75, y=30, w=60, h=60)  # Adjust position and size
        pdf.ln(70)  # Move down to avoid overlapping text

    # Add user data to the PDF
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, name, ln=True, align='C')
    pdf.cell(200, 10, email, ln=True, align='C')
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

    # Generate and add QR code
    # Assuming you're using the user's name to create the URL
    # Adjust the URL to a real URL that points to the resume
    base_url = "http://127.0.0.1:5000/resumes/"  # Change this to your live URL when deployed
    resume_url = f"{base_url}{name.replace(' ', '_')}_resume.pdf"  # Construct the full URL to the resume

    # Now generate the QR code with the valid URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(resume_url)  # Use the valid URL for QR code generation
    qr.make(fit=True)

    # Create the QR code image
    qr_image = qr.make_image(fill="black", back_color="white")

    # Save QR code image
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_qr.png")
    qr_image.save(qr_path)

    # Add QR code to PDF
    pdf.image(qr_path, x=80, y=pdf.get_y(), w=60)

    # Save and send the resume PDF
    resume_path = f"static/{name.replace(' ', '_')}_resume.pdf"
    pdf.output(resume_path)
    return send_file(resume_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
