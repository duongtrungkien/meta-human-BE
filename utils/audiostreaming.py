def chunk_audio(data, samplerate, maxduration):
    duration=len(data)/samplerate
    if duration > maxduration:
        chunksize=maxduration*samplerate
        chunks=[data[i:i + chunksize] for i in range(0, len(data), chunksize)]
        return chunks
    else:
        return [data]