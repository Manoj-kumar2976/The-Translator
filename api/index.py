from app import app

# Vercel serverless entry
def handler(request, response):
    return app(request, response)