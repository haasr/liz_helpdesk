echo "Creating virtual environment"
python -m venv .venv
echo "> Done"

echo "\n--------------------------------"
echo "Activating virtual environment"
.\.venv\Scripts\activate.ps1
echo "> Done"

echo "\n--------------------------------"
echo "Installing requirements"
pip install -r requirements.txt
echo "> Done"

echo "\n--------------------------------"
echo "Migrating database"
python manage.py migrate
echo "> Done"

echo "\n--------------------------------"
echo "Creating sys manager 'ghimirep' with password 'badpassword'"
.\createsysmanager.ps1
echo "> Done. Use 'ghimirep' and 'badpassword' to login"

echo "\n--------------------------------"
echo "Setup complete! You may now run the server using .\runserver.ps1"


