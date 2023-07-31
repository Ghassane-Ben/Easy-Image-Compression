from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
import os
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 10 MB (adjust this limit as needed)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    # Get the uploaded file
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))

    # Check if the file size is within the allowed limit
    if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
        return render_template('error.html', error_message="File size exceeds the allowed limit.")

    # Reset the file pointer to the beginning of the file
    file.seek(0)

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Get the compression level from the form input
    try:
        compression_level = int(request.form['compressionPercentage'])
        if not 0 <= compression_level <= 100:
            raise ValueError
    except (ValueError, KeyError):
        return render_template('error.html', error_message="Compression percentage must be an integer between 0 and 100.")

    # Perform image compression
    if compression_level == 0:
        compressed_image_path = file_path  # No compression, use the original image
    else:
        compressed_image_path = compress_image(file_path, compression_level)

    # Return the compressed image for download
    return send_file(compressed_image_path, as_attachment=True)

def compress_image(file_path, compression_level):
    # Open the image using Pillow
    image = Image.open(file_path)

    # Convert image to RGB if it's in a different mode (e.g., RGBA)
    image = image.convert('RGB')

    # Calculate the compression quality based on the compression level
    quality = int(100 - compression_level)

    # Create a buffer to hold the compressed image
    compressed_image_buffer = io.BytesIO()

    # Compress the image with the specified quality and save it to the buffer
    image.save(compressed_image_buffer, format='JPEG', optimize=True, quality=quality)

    # Seek to the beginning of the buffer
    compressed_image_buffer.seek(0)

    # Save the compressed image from the buffer to a file
    compressed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed.jpg')
    with open(compressed_image_path, 'wb') as f:
        f.write(compressed_image_buffer.getvalue())

    # Return the path of the compressed image
    return compressed_image_path

if __name__ == '__main__':
    app.run()
