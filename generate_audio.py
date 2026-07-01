import wave, math, struct, subprocess, os, sys

SAMPLE_RATE = 44100
BITS = 16
TICK_FREQ = 1500
TICK_MS = 30
ATTACK_MS = 2
DECAY_MS = 8
FILE_SECS = 900
DIR = "E:/GIT/Metronomo/audio"
FFMPEG = "C:/Users/josue/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe"

os.makedirs(DIR, exist_ok=True)

def make_tick(ns):
    at = int(SAMPLE_RATE * ATTACK_MS / 1000)
    dc = int(SAMPLE_RATE * DECAY_MS / 1000)
    return [math.sin(2*math.pi*TICK_FREQ*i/SAMPLE_RATE) * (
        min(1.0, i/at) if i < at else
        max(0.0, (ns-i)/dc) if i > ns-dc else 1.0
    ) for i in range(ns)]

def gen(bpm):
    ns = int(SAMPLE_RATE * TICK_MS / 1000)
    tick = make_tick(ns)
    gap = max(0, int(SAMPLE_RATE * 60 / bpm) - ns)
    total = int(SAMPLE_RATE * FILE_SECS)
    audio = []
    while len(audio) < total:
        audio.extend(tick[:total - len(audio)])
        if len(audio) >= total: break
        rem = min(gap, total - len(audio))
        audio.extend([0.0] * rem)
    audio = audio[:total]

    wav = f"{DIR}/metronome_{bpm}bpm.wav"
    mp3 = f"{DIR}/metronome_{bpm}bpm.mp3"
    with wave.open(wav, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(BITS // 8)
        wf.setframerate(SAMPLE_RATE)
        for v in audio:
            wf.writeframes(struct.pack("<h", max(-32768, min(32767, int(v*32767)))))
    r = subprocess.run([FFMPEG, "-y", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "128k", mp3],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Error en BPM {bpm}: {r.stderr}")
    else:
        os.remove(wav)
        print(f"  {bpm:3d} BPM -> {os.path.getsize(mp3)//1024} KB")

print("Generando audios...")
for b in range(30, 301, 10):
    gen(b)
print(f"\nListo! {len(list(range(40,201,10)))} archivos en: {DIR}")
