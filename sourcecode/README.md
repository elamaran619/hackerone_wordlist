## Installation
```
python3 -m pip install -r requirements.txt
```

## Usage
#### Download Reports (download_reports.py)
Arguments:
```
--idrange - ID Range
--output - Output Directory (the reports will be saved there)
```
Example usage:
```
mkdir reports
python3 download_reports.py --idrange 25,10000 --output reports/
```

#### Process Reports (process_reports.py)
Arguments:
```
--reports - Reports Directory
--output - Output Filename (csv)
```
Example usage:
```
python3 process_reports.py --reports reports/ --output dataset.csv
```
#### Create Wordlist (create_wordlist.py)
Arguments:
```
--reports - Reports Directory
--output - Output Filename (csv)
--entropy - Maximum Entropy (Default: 4.2)
```
Example usage:
```
python3 create_wordlist.py --dataset dataset.csv --output wordlists/ --entropy 4
```

## Tested With
- Ubuntu 20.04 & Python 3.8.2
