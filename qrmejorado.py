from flask import Flask, render_template, request, redirect, url_for, send_file
import qrcode
import io
from fpdf import FPDF
from pyzbar.pyzbar import decode
from PIL import Image
import base64

app = Flask(__name__)

# Base de datos en memoria para simular almacenamiento
registrations = []

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    photo = request.files['photo'] if 'photo' in request.files else None
    qr_code = generate_qr(name, email)
    qr_code_b64 = base64.b64encode(qr_code.getvalue()).decode()

    # Agregar los nuevos datos al registro
    registrations.append({
        'name': name, 'email': email, 'phone': phone, 'address': address, 'photo': photo, 'qr_code': qr_code_b64, 'attendance': False
    })
    return render_template('register.html', qr_code=qr_code_b64)

@app.route('/admin')
def admin():
    return render_template('admin.html', registrations=registrations)

@app.route('/download')
def download():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt="Registro de Eventos", ln=True, align='C')
    pdf.ln(10)
    for reg in registrations:
        pdf.cell(200, 10, txt=f"Nombre: {reg['name']}, Email: {reg['email']}, Asistencia: {'Sí' if reg['attendance'] else 'No'}", ln=True)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name="registros_evento.pdf", mimetype="application/pdf")

@app.route('/scanner')
def scanner():
    return render_template('scanqr.html')

@app.route('/scan', methods=['POST'])
def scan_qr():
    file = request.files['qr_image']
    img = Image.open(file)
    decoded_objects = decode(img)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
        for reg in registrations:
            if qr_data == f"{reg['name']},{reg['email']}":
                reg['attendance'] = True
                return f"Asistencia registrada para {reg['name']}"
    return "QR no válido o no encontrado."

@app.route('/delete/<name>')
def delete_record(name):
    global registrations
    registrations = [reg for reg in registrations if reg['name'] != name]
    return redirect(url_for('admin'))

@app.route('/delete_all')
def delete_all():
    global registrations
    registrations.clear()
    return redirect(url_for('admin'))

def generate_qr(name, email):
    data = f"{name},{email}"
    qr = qrcode.make(data)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    return qr_io

if __name__ == '__main__':
    app.run(debug=True)
