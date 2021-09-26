import wave


def read_wav_info(path) -> wave._wave_params:
    with wave.open(path) as wav:
        return wav.getparams()
