from pipeline.data_handler import stream_data
p='./data/cleaned_jobs.json'
try:
    it=stream_data(p)
    first=next(it)
    print('First record type:', type(first))
    if isinstance(first, dict):
        print('Keys:', list(first.keys())[:10])
except Exception as e:
    print('Error while streaming:', e)
