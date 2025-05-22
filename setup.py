import os

# Create necessary directories
os.makedirs('utils', exist_ok=True)
os.makedirs('components', exist_ok=True)
os.makedirs('assets', exist_ok=True)

# Create __init__.py files
with open(os.path.join('utils', '__init__.py'), 'w') as f:
    f.write('# Utils package initialization')

with open(os.path.join('components', '__init__.py'), 'w') as f:
    f.write('# Components package initialization')

print("Project structure created successfully!")
print("MindScribe is ready to be installed and run.")
print("\nInstallation Steps:")
print("1. pip install -r requirements.txt")
print("2. streamlit run app.py")
