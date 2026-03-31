echo "Wait please"
sleep 2
echo "ok."
sleep 2
echo "Fixing..."
sudo apt-get install python3-tk -y
python3 -m venv venv
source venv/bin/activate
pip install customtkinter requests beautifulsoup4 urllib3 --break-system-packages
echo "Fixed!"
echo "Wait Tool starting."
sleep 3
python3 thor-suite.py