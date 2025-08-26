import importlib.util

packages = ['langchain', 'langchain_openai', 'langchain_community', 'dotenv', 'serpapi']

for pkg in packages:
    if importlib.util.find_spec(pkg) is not None:
        print(f"{pkg} is installed.")
    else:
        print(f"{pkg} is NOT installed.")

