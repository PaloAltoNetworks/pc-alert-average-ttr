from pcpi import session_loader
from datetime import datetime, timedelta
import statistics
import argparse


def paginate_closed_alerts(filter_lists, unit, amount, session):
    standards_list = filter_lists[0]
    clouds_list = filter_lists[1]
    severity_list = filter_lists[2]


    payload = {
        "detailed": False, #Set to True for complete alert details, keep in mind this vastly increases the amount of data returned
        "limit": 2000,
        "timeRange": {
            # "relativeTimeType": "BACKWARD",
            "type": "relative",
            "value": {
                "amount": amount,
                "unit": unit
            }
        },
        "filters": [
            {"name": "alert.status","operator": "=","value": "resolved"},
            {'name': 'timeRange.type', 'operator': '=', 'value': "ALERT_OPENED"}
        ]
    }

    for std in standards_list:
        payload['filters'].append({'name':'policy.complianceStandard', 'operator':'=', 'value':std})

    for cld in clouds_list:
        payload['filters'].append({'name':'cloud.type', 'operator':'=', 'value':cld})

    for svr in severity_list:
        payload['filters'].append({'name':'policy.severity', 'operator':'=', 'value': svr})

    # Write the alerts to file for later use
    alerts_data = []

    count = 0
    while True:
        print('Page:', count)


        #Calling alerts endpoint
        res = session.request('POST', 'v2/alert', json=payload)

        alerts_data.extend(res.json()['items'])

        #Extract next page token from API response
        nextPageToken = res.json().get('nextPageToken', '')

        #Update payload to now include the next page token
        payload.update({"pageToken":nextPageToken})

        #When there is no more data, stop the loop (Both of these options are fine exit cases, combined they are redundant but make for a good example)
        if nextPageToken == '' or len(res.json()['items']) == 0:
            break

        #Increment count for file naming
        count += 1

    return alerts_data


if __name__ == '__main__':

    #Process CMD Args
    parser = argparse.ArgumentParser(
        prog='Alert Time To Resolved Report',
        description='Calculates the Average time it takes an Alert to get resolved'
        )
    
    parser.add_argument('-u', '--unit', choices={'day', 'week', 'hour', 'minute'}, required=True, help='Unit of time for Alert filtering.')
    parser.add_argument('-a', '--amount', type=int, required=True, help='Integer amount of the specified unit of time.')

    args = parser.parse_args()





    session_managers = session_loader.load_config('creds.json')
    session = session_managers[0].create_cspm_session()

    ttr_list = []
    alerts_skipped = 0

    for alert in paginate_closed_alerts([[],[],[]], args.unit, args.amount, session):
        first_seen = alert['firstSeen']
        last_seen = alert['lastSeen']
        time_to_resolution = last_seen - first_seen

        #Only report on alerts that have some TTR, a lot of Prisma Alerts are closed instantly
        if time_to_resolution > 0:
            ttr_list.append(time_to_resolution)
        else:
            alerts_skipped += 1

       

        # ttr_list.append(time_to_resolution)

    avg = statistics.mean(ttr_list)
    median = statistics.median(ttr_list)
    
    print()
    print()
    print('Resolved Alerts Processed:', len(ttr_list))
    print('Alerts Skipped:', alerts_skipped)
    print()

    sec = timedelta(milliseconds=int(avg))
    d = datetime(1,1,1) + sec
    print('Average Time To Resolve (DAYS:HOURS:MINUTES) =',end=' ')
    print("%d:%d:%d" % (d.day-1, d.hour, d.minute))
    print()

    
    sec = timedelta(milliseconds=int(median))
    d = datetime(1,1,1) + sec
    print('Median Time To Resolve (DAYS:HOURS:MINUTES) =', end=' ')
    print("%d:%d:%d" % (d.day-1, d.hour, d.minute))
    print()



