import sys
import io
import math  # Add this line
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Watermarker")
        self.layout = QVBoxLayout()

        self.file_label = QLabel("Select PDF File:")
        self.layout.addWidget(self.file_label)

        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.file_button)

        self.watermark_label = QLabel("Watermark Text:")
        self.layout.addWidget(self.watermark_label)

        self.watermark_text = QLineEdit()
        self.layout.addWidget(self.watermark_text)

        self.process_button = QPushButton("Add Watermark")
        self.process_button.clicked.connect(self.add_watermark)
        self.layout.addWidget(self.process_button)

        self.setLayout(self.layout)

        self.selected_file = None

    def select_file(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("PDF files (*.pdf)")
        if file_dialog.exec_():
            self.selected_file = file_dialog.selectedFiles()[0]
            self.file_label.setText("Selected PDF File: " + self.selected_file)

    def add_watermark(self):
        if self.selected_file is None:
            QMessageBox.warning(self, "Warning", "Please select a PDF file.")
            return

        output_pdf = self.selected_file[:-4] + "_watermarked.pdf"
        watermark_text = self.watermark_text.text()

        try:
            pdf_writer = PdfWriter()

            pdf_reader = PdfReader(open(self.selected_file, "rb"))

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)

                # Calculate text width and height
                text_width = can.stringWidth(watermark_text, "Helvetica", 72)
                text_height = 72  # Assuming font size is 72

                # Calculate center position
                page_width, page_height = letter
                x = (page_width - text_width) / 2 + 20  # Adjusted x-coordinate
                y = (page_height - text_height) / 2

                # Set opacity to 45%
                can.setFillAlpha(0.45)

                # Rotate text by 45 degrees
                can.rotate(45)

                # Adjust coordinates after rotation
                x_rotated = (x * math.cos(math.radians(45)) + y * math.sin(math.radians(45)))
                y_rotated = (y * math.cos(math.radians(45)) - x * math.sin(math.radians(45)))

                # Draw watermark text
                can.setFont("Helvetica", 72)
                can.drawString(x_rotated, y_rotated, watermark_text)
                can.save()

                packet.seek(0)
                new_pdf = PdfReader(packet)
                page.merge_page(new_pdf.pages[0])
                pdf_writer.add_page(page)

            with open(output_pdf, "wb") as out:
                pdf_writer.write(out)

            QMessageBox.information(self, "Success", "Watermark added successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())