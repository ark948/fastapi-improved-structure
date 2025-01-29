from source import init_app
import uvicorn

server = init_app()

if __name__ == "__main__":
    uvicorn.run("source.main:app", host="127.0.0.1", port=8000)


# you can also just use the main