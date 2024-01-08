import platform
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFormLayout, QLineEdit, QPushButton, QListWidget

class FirewallApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firewall App")
        self.layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.ip_input = QLineEdit()
        self.block_button = QPushButton("Block IP")
        self.unblock_button = QPushButton("Unblock IP")
        self.ip_list = QListWidget()

        self.layout.addWidget(self.ip_input)
        self.layout.addWidget(self.block_button)
        self.layout.addWidget(self.unblock_button)
        self.layout.addWidget(self.ip_list)

        self.block_button.clicked.connect(self.block_ip)
        self.unblock_button.clicked.connect(self.unblock_ip)

    def get_connected_ips(self):
        system = platform.system()
        if system == "Linux":
            output = subprocess.check_output(['arp', '-a']).decode('utf-8')
            lines = output.split('\n')
            ips = []
            for line in lines:
                if line:
                    ip = line.split('(')[1].split(')')[0]
                    ips.append(ip)
            return ips
        elif system == "Windows":
            output = subprocess.check_output(['arp', '-a']).decode('utf-8')
            lines = output.split('\n')
            ips = []
            for line in lines:
                if line:
                    ip = line.split("|", 1)
                    ips.append(ip)
            return ips
        else:
            return []

    def block_ip(self):
        ip_address = self.ip_input.text()
        system = platform.system()
        if system == "Linux":
            subprocess.run(['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'])
        elif system == "Windows":
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name="BlockIP"', 'dir=in', 'action=block', 'remoteip=' + ip_address])
        else:
            print("Unsupported operating system.")

    def unblock_ip(self):
        ip_address = self.ip_input.text()
        system = platform.system()
        if system == "Linux":
            subprocess.run(['iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP'])
        elif system == "Windows":
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name="BlockIP"', 'dir=in', 'action=block', 'remoteip=' + ip_address])
        else:
            print("Unsupported operating system.")

    def update_ip_list(self):
        self.ip_list.clear()
        connected_ips = self.get_connected_ips()
        self.ip_list.addItems(connected_ips)

if __name__ == "__main__":
    app = QApplication([])
    window = FirewallApp()
    window.update_ip_list()
    window.show()
    app.exec_()