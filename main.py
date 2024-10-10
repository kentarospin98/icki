from fastapi import FastAPI, Response, UploadFile
from fastapi.staticfiles import StaticFiles
import random
import string
import torch
import demucs.api
import os
from time import sleep
import uvicorn

app = FastAPI()
device = torch.cuda.device(0)
if torch.cuda.device_count() == 0:
    device = torch.device("mps")
if device is None:
    raise RuntimeError("No Cuda Device found")
print(device)
model = demucs.api.Separator("htdemucs", device=device, progress=True)
# Initialize with default parameters:
#separator = demucs.api.Separator()

# Use another model and segment:
#separator = demucs.api.Separator(model="mdx_extra")

import os
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/split_audio")
async def split_audio(source_audio: UploadFile):
    random_string = "".join(random.choices(string.ascii_letters, k=8))
    filename = random_string+".mp3"
    with open(filename, "wb") as f:
        f.write(await source_audio.read())

    try:
        origin, separated = model.separate_audio_file(filename)
    except Exception as e:
        return Response(status_code=500, content='{"error": "Failed to split audio."}')
    finally:
        os.remove(filename)

    demucs.api.save_audio(separated["vocals"], f"static/{random_string}_vocals.mp3", samplerate=model.samplerate)
    demucs.api.save_audio(origin - separated["vocals"], f"static/{random_string}_no_vocals.mp3", samplerate=model.samplerate)
    return {
        "no_vocals": f"static/{random_string}_vocals.mp3",
        "vocals": f"static/{random_string}_no_vocals.mp3",
    }


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')