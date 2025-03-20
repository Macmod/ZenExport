import json
from pathlib import Path
from time import sleep
import re
import requests
import arrow
import csv
import json
import os
import argparse
from datetime import datetime, timedelta

class ZenExport:
    def __init__(self, subdomain, email, token, out_dir='./exports', format_type='json', 
                 start_date=None, end_date=None, interval=7200, continuous=False):
        self.zendesk_subdomain = subdomain
        self.zendesk_user_email = email
        self.zendesk_api_token = token
        self.out_dir = out_dir
        self.format_type = format_type
        
        # Set default dates if not provided
        if not start_date:
            # TODO: Review
            self.start_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            self.start_date = start_date
            
        if not end_date:
            self.end_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            self.end_date = end_date
            
        self.interval = interval
        self.continuous = continuous
        
        # Create output directory if it doesn't exist
        os.makedirs(self.out_dir, exist_ok=True)

    def get_users(self, roles=['admin', 'agent']) -> list:
        print('[~] Querying users with roles ('+','.join(roles)+')')
        url = f'https://{self.zendesk_subdomain}.zendesk.com/api/v2/users'
        users = self.get_api_list('users', url, {'role[]': roles, 'page[size]': 100})
        return users

    def get_api_list(self, api_list_name, url, params) -> list:
        api_list = []
        auth = f'{self.zendesk_user_email}/token', self.zendesk_api_token 
        while url:
            response = requests.get(url, params=params, auth=auth)
            if response.status_code == 429:
                if 'retry-after' in response.headers:
                    wait_time = int(response.headers['retry-after'])
                else:
                    wait_time = 60
                    print(f'[-] Error: Rate limited! Will restart in {wait_time} seconds.')
                    sleep(wait_time)
                    response = requests.get(url, params=params, auth=auth)

            if response.status_code != 200:
                # TODO: Review
                print(f'[-] Error: API responded with status {response.status_code}: {response.text}. Trying again in 5 minutes...')
                sleep(300)
            else:
                data = response.json()
                api_list.extend(data[api_list_name])
                if 'meta' in data and data['meta']['has_more']:
                    params['page[after]'] = data['meta']['after_cursor']
                else:
                    url = ''

        return api_list

    def export_access_logs(self, start_date=None, end_date=None) -> str:
        # Use provided dates or instance defaults
        filter_start = start_date if start_date else self.start_date
        filter_end = end_date if end_date else self.end_date
        
        users = self.get_users()
        users_map = {u['id']: (u['name'], u['email']) for u in users}

        agent_access_logs = []

        api_list_name = 'access_logs'
        url = f'https://{self.zendesk_subdomain}.zendesk.com/api/v2/access_logs'
        params = {
                'filter[start]': filter_start,
                'filter[end]': filter_end,
                'page[size]': 1000
        }
        print(f'[~] Querying logs from {filter_start} to {filter_end}')

        access_logs = self.get_api_list(api_list_name, url, params)
        for log in access_logs:
            log['mapped_user'] = list(users_map[log['user_id']] if log['user_id'] in users_map else ('UNKNOWN', 'UNKNOWN'))
        agent_access_logs.extend(access_logs)

        if self.format_type.lower() == 'csv':
            file_path_str = os.path.join(self.out_dir, f'access_logs_{filter_start}-to-{filter_end}.csv')
        else:
            file_path_str = os.path.join(self.out_dir, f'access_logs_{filter_start}-to-{filter_end}.json')
        file_path = Path(file_path_str)

        if self.format_type.lower() == 'csv':
            with file_path.open(mode='w', newline='') as csv_file:
                report_writer = csv.writer(csv_file, delimiter=',')
                # Write header
                report_writer.writerow(['ID', 'Timestamp', 'User ID', 'User Name', 'User Email', 'IP Address', 'Method', 'URL', 'Status'])
                for log in agent_access_logs:
                    row = (
                        log['id'], log['timestamp'], log['user_id'], log['mapped_user'][0], log['mapped_user'][1],
                        log['ip_address'], log['method'], log['url'], log['status']
                    )

                    report_writer.writerow(row)
        else:
            with file_path.open(mode='w', newline='') as f:
                json.dump(agent_access_logs, f, indent=2)

        print(f'[+] Data exported to {file_path_str}\n')
        return file_path_str
    
    def run(self):
        if self.continuous:
            print(f"[~] Running in continuous mode with {self.interval} seconds interval")
            while True:
                # Update end_date to current time and start_date to interval ago
                end_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                start_date = (datetime.utcnow() - timedelta(seconds=self.interval)).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                self.export_access_logs(start_date, end_date)

                print(f'[~] Sleeping for {self.interval} seconds')
                sleep(self.interval)
        else:
            self.export_access_logs()

def parse_args():
    parser = argparse.ArgumentParser(description='Export Zendesk access logs')
    parser.add_argument('--subdomain', required=True, help='Zendesk subdomain (e.g., company in company.zendesk.com)')
    parser.add_argument('--email', required=True, help='Zendesk user email')
    parser.add_argument('--token', required=True, help='Zendesk API token')
    parser.add_argument('--outdir', default='./exports', help='Output directory for exported files (default: ./exports)')
    parser.add_argument('--format', choices=['csv', 'json'], default='json', help='Export format (csv or json, default: json)')
    parser.add_argument('--start-time', help='Start time for logs (ISO format, e.g., 2023-01-01T00:00:00Z)')
    parser.add_argument('--end-time', help='End time for logs (ISO format, e.g., 2023-01-31T23:59:59Z)')
    parser.add_argument('--interval', type=int, default=7200, help='Interval in seconds between exports for continuous mode (default: 7200)')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode, exporting logs at regular intervals')
    
    args = parser.parse_args()
    
    # Set default dates if not provided
    if not args.start_time:
        args.start_time = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    if not args.end_time:
        args.end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
    return args

if __name__ == '__main__':
    args = parse_args()
    
    exporter = ZenExport(
        subdomain=args.subdomain,
        email=args.email,
        token=args.token,
        out_dir=args.outdir,
        format_type=args.format,
        start_date=args.start_time,
        end_date=args.end_time,
        interval=args.interval,
        continuous=args.continuous
    )
    
    exporter.run()
