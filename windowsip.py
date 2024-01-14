import platform
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QListWidget

class FirewallApp(QMainWindow):
    IP_RANGE = '192.168.29.0/24'
    RULE_NAME_PREFIX = 'BlockIP'
    RULE_DESCRIPTION = 'Blocking IP'
    TIMEOUT = '1'

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
        try:
            if system == "Linux":
                output = subprocess.check_output(['nmap', '-sn', self.IP_RANGE], text=True)
                return [line.split()[-1] for line in output.split('\n') if 'Nmap scan report' in line]
            elif system == "Windows":
                output = subprocess.check_output(['arp', '-a', '-v'], text=True)
                return [line.split()[1] for line in output.split('\n') if line]
            else:
                return []
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return []

    def block_unblock_ip(self, block=True):
        ip_address = self.ip_input.text()
        system = platform.system()
        try:
            if system == "Linux":
                action = '-A' if block else '-D'
                subprocess.run(['iptables', action, 'INPUT', '-s', ip_address, '-j', 'DROP'])
            elif system == "Windows":
                action = 'add' if block else 'delete'
                subprocess.run(['netsh', 'advfirewall', 'firewall', action, 'rule', f'name="{self.RULE_NAME_PREFIX}_{ip_address}"', 'dir=in', 'action=block', f'remoteip={ip_address}'])
            else:
                print("Unsupported operating system.")
                return
            print("Blocked IP:" if block else "Unblocked:", ip_address)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def block_ip(self):
        self.block_unblock_ip(block=True)

    def unblock_ip(self):
        self.block_unblock_ip(block=False)

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
