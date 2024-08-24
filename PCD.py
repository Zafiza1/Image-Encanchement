# Import modul.
import sys
import cv2 #Modul OpenCV untuk pengolahan gambar.
import numpy as np # Modul untuk operasi array.
from PyQt5 import QtWidgets, QtGui, QtCore # Modul untuk membuat (GUI) berbasis PyQt5

# Class Image Encanchement
class ImageEnhancementApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ImageEnhancementApp, self).__init__()

        self.setWindowTitle("Pengolahan Citra Digital") # Menetapkan judul aplikasi.
        self.setGeometry(150, 150, 850, 600) # Menetapkan posisi dan ukuran pada layar aplikasi.
        
        # Penginputan Widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Layar utama
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.image_label = QtWidgets.QLabel() # Label untuk menampilkan gambar.
        self.layout.addWidget(self.image_label)

        # Tombol-tombol
        self.controls_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        #Mengimport Gambar Dari File
        self.load_button = QtWidgets.QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        self.controls_layout.addWidget(self.load_button)

        #Menyimpan Gambar
        self.save_button = QtWidgets.QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        self.controls_layout.addWidget(self.save_button)

        #Mengembalikan Gambar Yang Telah Diedit
        self.undo_button = QtWidgets.QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        self.controls_layout.addWidget(self.undo_button)

        #Melanjutkan Gambar Yang Telah Diedit
        self.redo_button = QtWidgets.QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo)
        self.controls_layout.addWidget(self.redo_button)

        #Penyesuaian Kontras
        self.contrast_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.contrast_slider.setRange(1, 100)
        self.contrast_slider.setValue(50)
        self.contrast_slider.valueChanged.connect(self.change_contrast)
        self.controls_layout.addWidget(QtWidgets.QLabel("Contrast"))
        self.controls_layout.addWidget(self.contrast_slider)

        #Peningkatan Ketajaman
        self.sharpen_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sharpen_slider.setRange(1, 100)
        self.sharpen_slider.setValue(10)
        self.sharpen_slider.valueChanged.connect(self.change_sharpen)
        self.controls_layout.addWidget(QtWidgets.QLabel("Sharpen"))
        self.controls_layout.addWidget(self.sharpen_slider)

        #Penyesuaian Cahaya
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.setRange(1, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.change_brightness)
        self.controls_layout.addWidget(QtWidgets.QLabel("Brightness"))
        self.controls_layout.addWidget(self.brightness_slider)

        #Reduksi Noise
        self.noise_reduction_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.noise_reduction_slider.setRange(1, 100)
        self.noise_reduction_slider.setValue(10)
        self.noise_reduction_slider.valueChanged.connect(self.reduce_noise)
        self.controls_layout.addWidget(QtWidgets.QLabel("Noise Reduction"))
        self.controls_layout.addWidget(self.noise_reduction_slider)

        self.image = None
        self.original_image = None
        self.history = []
        self.history_index = -1

    def load_image(self):
        options = QtWidgets.QFileDialog.Options()
        # Membuka dialog untuk memilih file gambar dari disk.
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Image", "", "Images (*.png *.xpm *.jpg *.bmp)", options=options)
        if fileName:
            self.image = cv2.imread(fileName) # Memuat gambar dari file.
            self.original_image = self.image.copy() # Menyimpan gambar yang dimuat dan salinan aslinya.
            self.history = [self.image.copy()]
            self.history_index = 0 # Menyimpan riwayat gambar untuk fitur undo/redo
            self.display_image()

    def save_image(self):
        options = QtWidgets.QFileDialog.Options()
        # Membuka dialog untuk memilih lokasi dan nama file untuk menyimpan gambar.
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg *.bmp)", options=options)
        if fileName:
            cv2.imwrite(fileName, self.image) #  Menyimpan gambar ke file.

# Menampilkan gambar di label.
    def display_image(self):
        if self.image is None:
            return
        qformat = QtGui.QImage.Format_RGB888
        if len(self.image.shape) == 2:
            qformat = QtGui.QImage.Format_Grayscale8
        elif self.image.shape[2] == 4:
            qformat = QtGui.QImage.Format_RGBA8888

        qimage = QtGui.QImage(self.image, self.image.shape[1], self.image.shape[0], self.image.strides[0], qformat)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(qimage))

    def change_contrast(self):
        alpha = self.contrast_slider.value() / 50  # Mengatur skala slider
        self.image = cv2.convertScaleAbs(self.original_image, alpha=alpha, beta=0)
        self.update_history()
        self.display_image()

    def change_sharpen(self):
        level = self.sharpen_slider.value() / 10  # Mengatur skala slider
        kernel = np.array([[0, -1, 0], [-1, 5 + level, -1], [0, -1, 0]])
        self.image = cv2.filter2D(self.original_image, -1, kernel)
        self.update_history()
        self.display_image()

    def change_brightness(self):
        beta = self.brightness_slider.value() - 50  # Mengatur skala slider
        self.image = cv2.convertScaleAbs(self.original_image, alpha=1, beta=beta)
        self.update_history()
        self.display_image()

    def reduce_noise(self):
        h = self.noise_reduction_slider.value()  # Mengatur skala slider
        self.image = cv2.fastNlMeansDenoisingColored(self.original_image, None, h, h, 7, 21)
        self.update_history()
        self.display_image()

    def update_history(self):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(self.image.copy())
        self.history_index += 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.display_image()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.display_image()

# Running aplikasi
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ImageEnhancementApp()
    window.show()
    sys.exit(app.exec_())
