import json
import boto3
import json
import requests
import os
from datetime import datetime, date, timedelta

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def lambda_handler(event, context):
    client = boto3.client('ce')
    (start_date, end_date) = get_total_cost_date_range()

    mult_total_billing = get_total_billing(client, start_date, end_date)
    mult_billing_by_service = get_service_billings(client, start_date, end_date)
    one_day_total_billing = get_total_billing(client, get_prev_day(1), get_today())
    one_day_billing_by_service = get_service_billings(client, get_prev_day(1), get_today())

    message1 = create_notify_message1(mult_total_billing, mult_billing_by_service)
    message2 = create_notify_message2(one_day_total_billing, one_day_billing_by_service)

    notify_slack(message1[0], message2[0], message1[1], message2[1])

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "done notification",
            }
        ),
    }

def get_total_billing(client,start_date,end_date) -> dict:

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ]
    )
    return {
        'start': response['ResultsByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'],
    }

def get_total_cost_date_range() -> (str, str):
    start_date = get_begin_of_month()
    end_date = get_today()

    if start_date == end_date:
        end_of_month = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=-1)
        begin_of_month = end_of_month.replace(day=1)
        return begin_of_month.date().isoformat(), end_date
    return start_date, end_date


def get_begin_of_month() -> str:
    return date.today().replace(day=1).isoformat()


def get_prev_day(prev: int) -> str:
    return (date.today() - timedelta(days=prev)).isoformat()


def get_today() -> str:
    return date.today().isoformat()


def get_service_billings(client,start_date,end_date) -> list:

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    billings = []

    for item in response['ResultsByTime'][0]['Groups']:
        if item['Metrics']['AmortizedCost']['Amount'] == '0':
            continue
        billings.append({
            'service_name': item['Keys'][0],
            'billing': item['Metrics']['AmortizedCost']['Amount']
        })

    sorted_billings = reversed(sorted(billings, key=lambda x:x['billing']))
    return list(sorted_billings)


def create_notify_message1(total_billing,service_billings):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')

    # Endの日付は結果に含まないため、表示上は前日にしておく
    end_today = datetime.strptime(total_billing['end'], '%Y-%m-%d')
    end_yesterday = (end_today - timedelta(days=1)).strftime('%m/%d')

    total = round(float(total_billing['billing']), 2)

    title = f'{start}～{end_yesterday}の請求額は、{total:.2f} USDです。'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            # 請求無し（0.0 USD）の場合は、内訳を表示しない
            continue
        details.append(f'　・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)


def create_notify_message2(total_billing,service_billings):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')

    # Endの日付は結果に含まないため、表示上は前日にしておく
    end_today = datetime.strptime(total_billing['end'], '%Y-%m-%d')
    end_yesterday = (end_today - timedelta(days=1)).strftime('%m/%d')

    total = round(float(total_billing['billing']), 2)

    title = f'過去１日の請求額は、{total:.2f} USDです。'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            # 請求無し（0.0 USD）の場合は、内訳を表示しない
            continue
        details.append(f'　・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)


def notify_slack(title1: str, title2: str, message1: str, message2:str) -> None:
    """ notify #aws-billing
    """
    payload = {
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': title1,
                'text': message1
            },
            {
                'color': '#36a64f',
                'pretext': title2,
                'text': message2
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)

if __name__ == '__main__':
    client = boto3.client('ce')
    (start_date, end_date) = get_total_cost_date_range()

    mult_total_billing = get_total_billing(client, start_date, end_date)
    mult_billing_by_service = get_service_billings(client, start_date, end_date)
    one_day_total_billing = get_total_billing(client, get_prev_day(1), get_today())
    one_day_billing_by_service = get_service_billings(client, get_prev_day(1), get_today())

    message1 = create_notify_message1(mult_total_billing, mult_billing_by_service)
    message2 = create_notify_message2(one_day_total_billing, one_day_billing_by_service)

    notify_slack(message1[0], message2[0], message1[1], message2[1])

