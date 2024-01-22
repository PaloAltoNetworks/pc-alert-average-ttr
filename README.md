# pc-alert-average-ttr
Script to calculate average time it takes for an Alert to move from Open status to Resolved status.


# Alert Time To Resolution Report

# Setup
```bash
python3 -m pip install pcpi
```

# Running the Script

Get Help Text
```bash
python3 alert_ttr_report.py -h
```

Get report on Alerts from the last 4 days
```bash
python3 alert_ttr_report.py -u day -a 4
```
