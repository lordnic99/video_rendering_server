import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QDialog, QLabel, QMessageBox
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class InputDialog(QDialog):
    def __init__(self, title, *messages, parent=None):
        super(InputDialog, self).__init__(parent)
        self.setWindowTitle(title)
        
        self.message_labels = [QLabel(message) for message in messages]
        self.input_field = QLineEdit()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        self.ok_button.setFixedHeight(40)
        self.cancel_button.setFixedHeight(40)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        for label in self.message_labels:
            layout.addWidget(label)
        layout.addWidget(self.input_field)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Adjust dialog size
        self.setFixedSize(400, 200 + len(messages) * 30)  # Adjust height based on the number of messages

    def get_input_text(self):
        if self.exec_():
            return self.input_field.text()
        else:
            return None

def get_audio_cut_time(t, job_name):
    app = QApplication(sys.argv)
    dialog = InputDialog("Nhập thời lượng cắt theo phút", 
                         f"Audio có thời lượng tổng là {t} tiếng",
                         f"Job đang thực hiên: {job_name}")
    if dialog.exec_():
        input_text = dialog.get_input_text()
        return input_text
    else:
        return None

def jpg_not_existed(job_name):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Lỗi")
    msg_box.setText(f"Lỗi, không tìm thấy JPG để tạo video, MASTER sẽ thoát ngay bây giờ, "
                    f"vui lòng chuẩn bị file JPG cho job {job_name} sau đó chạy lại MASTER để tiếp tục")
    
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    msg_box.exec_()
    
def audio_must_be_cut(job_name):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Lỗi")
    msg_box.setText(f"Lỗi, video có thời lượng > 12 tiếng, MASTER sẽ thoát ngay bây giờ, "
                    f"Vui lòng chạy lại MASTER để cắt audio, vì audio có thời lượng lớn hơn 12 tiếng nhưng không cắt")
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    
    msg_box.exec_()