:: Create FLAC file from an stock CX Card 14.3msps (10-bit) 16-bit sample capture .u16 file.
pushd %~dp0
echo Encoding Unsinged 16-bit to FLAC Compressed ... 
flac.exe -f "%~1" --threads 64 --best --sample-rate=14318 --sign=unsigned --channels=1 --endian=little --bps=16 "%~n1.flac"
echo Done. 
PAUSE